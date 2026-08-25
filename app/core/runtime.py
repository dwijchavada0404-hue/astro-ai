from __future__ import annotations

import re
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.settings import Settings
from app.core.auth_tokens import (
    AuthenticationError,
    bearer_token_from_header,
    decode_bearer_token,
)


_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_DOC_PATHS = {"/docs", "/redoc", "/openapi.json"}


class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_name: str = "X-Request-ID"):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming = request.headers.get(self.header_name, "")
        request_id = incoming if _REQUEST_ID_RE.fullmatch(incoming) else uuid4().hex
        request.state.request_id = request_id
        started = perf_counter()
        response = await call_next(request)
        response.headers[self.header_name] = request_id
        response.headers["X-Process-Time-Ms"] = f"{(perf_counter() - started) * 1000:.2f}"
        return response


class DocsGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in _DOC_PATHS:
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        return await call_next(request)


class RequestBodyLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_bytes: int):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        raw_length = request.headers.get("content-length")
        if raw_length:
            try:
                content_length = int(raw_length)
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length header."})
            if content_length > self.max_bytes:
                return JSONResponse(status_code=413, content={"detail": "Request body too large."})
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault("Cache-Control", "no-store")
        return response


class ApiAccessControlMiddleware(BaseHTTPMiddleware):
    """Require the configured bearer identity for every application API route."""

    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "OPTIONS" or not request.url.path.startswith("/api/"):
            return await call_next(request)
        try:
            token = bearer_token_from_header(request.headers.get("authorization"))
            decode_bearer_token(token, self.settings)
        except AuthenticationError as exc:
            return JSONResponse(
                status_code=401,
                content={"detail": str(exc)},
                headers={"WWW-Authenticate": "Bearer"},
            )
        return await call_next(request)


def _register_probe_routes(app: FastAPI, settings: Settings) -> None:
    route_paths = {getattr(route, "path", None) for route in app.routes}

    if "/livez" not in route_paths:
        async def livez() -> dict[str, str]:
            return {"status": "ok", "service": settings.app_name, "version": settings.app_version}
        app.add_api_route("/livez", livez, methods=["GET"], include_in_schema=False)

    if "/readyz" not in route_paths:
        async def readyz() -> dict[str, str]:
            return {"status": "ready", "environment": settings.environment}
        app.add_api_route("/readyz", readyz, methods=["GET"], include_in_schema=False)


def configure_runtime(app: FastAPI, settings: Settings) -> FastAPI:
    """Apply deployment middleware without changing astrology domain behavior."""
    app.title = settings.app_name
    app.version = settings.app_version
    _register_probe_routes(app, settings)

    if not settings.docs_enabled:
        app.add_middleware(DocsGuardMiddleware)

    if settings.security_headers_enabled:
        app.add_middleware(SecurityHeadersMiddleware)

    if settings.api_auth_required:
        app.add_middleware(ApiAccessControlMiddleware, settings=settings)

    app.add_middleware(RequestBodyLimitMiddleware, max_bytes=settings.max_request_body_bytes)
    app.add_middleware(RequestContextMiddleware, header_name=settings.request_id_header)

    trusted_hosts = settings.trusted_host_list
    if trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

    origins = settings.cors_origin_list
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", settings.request_id_header],
            expose_headers=[settings.request_id_header, "X-Process-Time-Ms"],
        )

    return app
