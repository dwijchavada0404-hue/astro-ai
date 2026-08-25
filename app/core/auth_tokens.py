from __future__ import annotations

from functools import lru_cache
from typing import Any

import jwt
from jwt import PyJWKClient

from app.core.settings import Settings


class AuthenticationError(ValueError):
    """A bearer token could not be verified against the runtime contract."""


def decode_bearer_token(token: str, settings: Settings) -> dict[str, Any]:
    if not settings.auth_enabled:
        raise AuthenticationError("Authentication is not enabled for this AstroAI runtime.")
    try:
        signing_key: Any = settings.auth_jwt_secret
        if settings.auth_jwks_url:
            signing_key = _jwks_client(settings.auth_jwks_url).get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[settings.auth_jwt_algorithm],
            issuer=settings.auth_jwt_issuer,
            audience=settings.auth_jwt_audience,
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Authentication token has expired.") from exc
    except (jwt.InvalidTokenError, jwt.PyJWKClientError) as exc:
        raise AuthenticationError("Invalid authentication token.") from exc
    if not str(payload.get("sub") or "").strip():
        raise AuthenticationError("Authentication token subject is missing.")
    return payload


@lru_cache(maxsize=8)
def _jwks_client(url: str) -> PyJWKClient:
    """Reuse PyJWT's JWKS cache instead of fetching provider keys for every request."""
    return PyJWKClient(url, cache_keys=True)


def bearer_token_from_header(header: str | None) -> str:
    if not header:
        raise AuthenticationError("Bearer authentication is required.")
    scheme, separator, token = header.partition(" ")
    if not separator or scheme.lower() != "bearer" or not token.strip():
        raise AuthenticationError("Bearer authentication is required.")
    return token.strip()
