from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.core.settings import Settings, get_settings


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
_bearer = HTTPBearer(auto_error=False)


class AuthenticatedUserProfile(BaseModel):
    user_id: str = Field(min_length=1, max_length=200)
    email: str | None = Field(default=None, max_length=320)
    display_name: str | None = Field(default=None, max_length=120)
    locale: str | None = Field(default=None, max_length=35)
    timezone: str | None = Field(default=None, max_length=100)
    email_verified: bool = False
    issued_at: datetime | None = None


class AuthMeResponse(BaseModel):
    authenticated: bool = True
    profile: AuthenticatedUserProfile


def _decode_token(token: str, settings: Settings) -> dict[str, Any]:
    if not settings.auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not enabled for this AstroAI runtime.",
        )
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
        raise HTTPException(status_code=401, detail="Authentication token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token.") from exc
    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    settings: Settings = Depends(get_settings),
) -> AuthenticatedUserProfile:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    claims = _decode_token(credentials.credentials, settings)
    subject = str(claims.get("sub") or "").strip()
    if not subject:
        raise HTTPException(status_code=401, detail="Authentication token subject is missing.")

    issued_at: datetime | None = None
    raw_iat = claims.get("iat")
    if isinstance(raw_iat, (int, float)):
        issued_at = datetime.fromtimestamp(raw_iat, tz=timezone.utc)

    return AuthenticatedUserProfile(
        user_id=subject,
        email=claims.get("email") if isinstance(claims.get("email"), str) else None,
        display_name=claims.get("name") if isinstance(claims.get("name"), str) else None,
        locale=claims.get("locale") if isinstance(claims.get("locale"), str) else None,
        timezone=claims.get("timezone") if isinstance(claims.get("timezone"), str) else None,
        email_verified=bool(claims.get("email_verified", False)),
        issued_at=issued_at,
    )


@router.get("/me", response_model=AuthMeResponse)
def read_current_user(profile: AuthenticatedUserProfile = Depends(get_current_user)) -> AuthMeResponse:
    """Return the authenticated AstroAI identity/profile derived from verified token claims."""
    return AuthMeResponse(profile=profile)
