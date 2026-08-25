from __future__ import annotations

from typing import Any

import jwt

from app.core.settings import Settings


class AuthenticationError(ValueError):
    """A bearer token could not be verified against the runtime contract."""


def decode_bearer_token(token: str, settings: Settings) -> dict[str, Any]:
    if not settings.auth_enabled:
        raise AuthenticationError("Authentication is not enabled for this AstroAI runtime.")
    try:
        payload = jwt.decode(
            token,
            settings.auth_jwt_secret,
            algorithms=[settings.auth_jwt_algorithm],
            issuer=settings.auth_jwt_issuer,
            audience=settings.auth_jwt_audience,
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Authentication token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("Invalid authentication token.") from exc
    if not str(payload.get("sub") or "").strip():
        raise AuthenticationError("Authentication token subject is missing.")
    return payload


def bearer_token_from_header(header: str | None) -> str:
    if not header:
        raise AuthenticationError("Bearer authentication is required.")
    scheme, separator, token = header.partition(" ")
    if not separator or scheme.lower() != "bearer" or not token.strip():
        raise AuthenticationError("Bearer authentication is required.")
    return token.strip()
