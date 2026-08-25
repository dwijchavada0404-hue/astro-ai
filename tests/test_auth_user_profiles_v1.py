from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.auth_v1 import router
from app.core.settings import Settings


SECRET = "test-secret-with-at-least-thirty-two-characters"
ISSUER = "astroai-test"
AUDIENCE = "astroai-api-test"


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


def _settings() -> Settings:
    return Settings(
        environment="test",
        auth_enabled=True,
        auth_jwt_secret=SECRET,
        auth_jwt_issuer=ISSUER,
        auth_jwt_audience=AUDIENCE,
    )


def _token(**overrides):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "user_123",
        "email": "user@example.com",
        "name": "Astro User",
        "email_verified": True,
        "locale": "en-IN",
        "timezone": "Asia/Kolkata",
        "iat": now,
        "exp": now + timedelta(minutes=30),
        "iss": ISSUER,
        "aud": AUDIENCE,
    }
    payload.update(overrides)
    return jwt.encode(payload, SECRET, algorithm="HS256")


def test_me_returns_verified_identity(monkeypatch):
    from app.api import auth_v1

    monkeypatch.setattr(auth_v1, "get_settings", _settings)
    auth_v1.get_current_user.__defaults__ = auth_v1.get_current_user.__defaults__
    app = _app()
    app.dependency_overrides[auth_v1.get_settings] = _settings
    client = TestClient(app)
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {_token()}"})
    assert response.status_code == 200
    body = response.json()
    assert body["authenticated"] is True
    assert body["profile"]["user_id"] == "user_123"
    assert body["profile"]["email"] == "user@example.com"
    assert body["profile"]["email_verified"] is True
    assert body["profile"]["timezone"] == "Asia/Kolkata"


def test_me_requires_bearer_token(monkeypatch):
    from app.api import auth_v1

    app = _app()
    app.dependency_overrides[auth_v1.get_settings] = _settings
    response = TestClient(app).get("/api/v1/auth/me")
    assert response.status_code == 401


def test_expired_token_is_rejected(monkeypatch):
    from app.api import auth_v1

    now = datetime.now(timezone.utc)
    token = _token(iat=now - timedelta(hours=2), exp=now - timedelta(hours=1))
    app = _app()
    app.dependency_overrides[auth_v1.get_settings] = _settings
    response = TestClient(app).get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_wrong_audience_is_rejected(monkeypatch):
    from app.api import auth_v1

    token = _token(aud="other-api")
    app = _app()
    app.dependency_overrides[auth_v1.get_settings] = _settings
    response = TestClient(app).get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_auth_enabled_requires_long_secret():
    try:
        Settings(environment="test", auth_enabled=True, auth_jwt_secret="short")
    except ValueError as exc:
        assert "32 characters" in str(exc)
    else:
        raise AssertionError("Expected short auth secret to be rejected")
