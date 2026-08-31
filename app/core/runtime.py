from __future__ import annotations

import re
import asyncio
import json
import logging
import sqlite3
from collections import defaultdict, deque
from pathlib import Path
from time import monotonic, perf_counter
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
_REQUEST_LOGGER = logging.getLogger("astroai.request")


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


class StructuredRequestLoggingMiddleware(BaseHTTPMiddleware):
    """Emit privacy-safe JSON request telemetry for provider log collection."""

    def __init__(self, app, environment: str, slow_request_threshold_ms: int):
        super().__init__(app)
        self.environment = environment
        self.slow_request_threshold_ms = slow_request_threshold_ms

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        started = perf_counter()
        request_id = getattr(request.state, "request_id", "unavailable")
        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (perf_counter() - started) * 1000
            self._write(
                logging.ERROR,
                event="request_failed",
                request=request,
                request_id=request_id,
                duration_ms=duration_ms,
                status_code=500,
                error_type=type(exc).__name__,
            )
            raise

        duration_ms = (perf_counter() - started) * 1000
        level = logging.WARNING if response.status_code >= 500 or duration_ms >= self.slow_request_threshold_ms else logging.INFO
        self._write(
            level,
            event="request_completed",
            request=request,
            request_id=request_id,
            duration_ms=duration_ms,
            status_code=response.status_code,
        )
        return response

    def _write(
        self,
        level: int,
        *,
        event: str,
        request: Request,
        request_id: str,
        duration_ms: float,
        status_code: int,
        error_type: str | None = None,
    ) -> None:
        payload: dict[str, object] = {
            "duration_ms": round(duration_ms, 2),
            "environment": self.environment,
            "event": event,
            "method": request.method,
            "route": _route_template(request),
            "request_id": request_id,
            "status_code": status_code,
        }
        if error_type:
            payload["error_type"] = error_type
        _REQUEST_LOGGER.log(level, json.dumps(payload, separators=(",", ":"), sort_keys=True))


def _route_template(request: Request) -> str:
    """Return the registered route pattern without logging record identifiers."""
    route = request.scope.get("route")
    template = getattr(route, "path", None)
    return template if isinstance(template, str) else "<unmatched>"


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
            claims = decode_bearer_token(token, self.settings)
        except AuthenticationError as exc:
            return JSONResponse(
                status_code=401,
                content={"detail": str(exc)},
                headers={"WWW-Authenticate": "Bearer"},
            )
        request.state.auth_subject = str(claims.get("sub") or "").strip()
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Bound authenticated API traffic with a per-user sliding window."""

    def __init__(self, app, requests_per_minute: int):
        super().__init__(app)
        self.limit = requests_per_minute
        self.window_seconds = 60.0
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "OPTIONS" or not request.url.path.startswith("/api/"):
            return await call_next(request)

        subject = getattr(request.state, "auth_subject", "")
        client_host = request.client.host if request.client else "unknown"
        key = f"user:{subject}" if subject else f"ip:{client_host}"
        now = monotonic()

        async with self._lock:
            bucket = self._requests[key]
            cutoff = now - self.window_seconds
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= self.limit:
                retry_after = max(1, int(self.window_seconds - (now - bucket[0])) + 1)
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again shortly."},
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(self.limit),
                        "X-RateLimit-Remaining": "0",
                    },
                )
            bucket.append(now)
            remaining = self.limit - len(bucket)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response


def _register_probe_routes(app: FastAPI, settings: Settings) -> None:
    route_paths = {getattr(route, "path", None) for route in app.routes}

    if "/livez" not in route_paths:
        async def livez() -> dict[str, str]:
            return {"status": "ok", "service": settings.app_name, "version": settings.app_version}
        app.add_api_route("/livez", livez, methods=["GET"], include_in_schema=False)

    if "/readyz" not in route_paths:
        async def readyz() -> Response:
            storage_ready = _database_ready(settings.profile_database_path)
            payload = {
                "status": "ready" if storage_ready else "not_ready",
                "environment": settings.environment,
                "checks": {"profile_database": "ok" if storage_ready else "failed"},
            }
            return JSONResponse(status_code=200 if storage_ready else 503, content=payload)
        app.add_api_route("/readyz", readyz, methods=["GET"], include_in_schema=False)


def _database_ready(database_path: str) -> bool:
    """Verify that the configured SQLite store can be opened and queried."""
    try:
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path, timeout=1) as database:
            database.execute("SELECT name FROM sqlite_master LIMIT 1").fetchone()
        return True
    except (OSError, sqlite3.Error):
        return False


def configure_runtime(app: FastAPI, settings: Settings) -> FastAPI:
    """Apply deployment middleware without changing astrology domain behavior."""
    app.title = settings.app_name
    app.version = settings.app_version
    _register_probe_routes(app, settings)

    if not settings.docs_enabled:
        app.add_middleware(DocsGuardMiddleware)

    if settings.security_headers_enabled:
        app.add_middleware(SecurityHeadersMiddleware)

    if settings.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=settings.rate_limit_requests_per_minute,
        )

    if settings.api_auth_required:
        app.add_middleware(ApiAccessControlMiddleware, settings=settings)

    app.add_middleware(RequestBodyLimitMiddleware, max_bytes=settings.max_request_body_bytes)
    if settings.request_logging_enabled:
        app.add_middleware(
            StructuredRequestLoggingMiddleware,
            environment=settings.environment,
            slow_request_threshold_ms=settings.slow_request_threshold_ms,
        )
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
            # The browser client updates saved conversation/profile metadata with
            # PATCH.  Keep the preflight allow-list aligned with the public API
            # methods so a successful server route is reachable from the hosted
            # web app as well as from same-origin test clients.
            allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", settings.request_id_header],
            expose_headers=[
                settings.request_id_header,
                "X-Process-Time-Ms",
                "X-RateLimit-Limit",
                "X-RateLimit-Remaining",
                "Retry-After",
            ],
        )

    return app
