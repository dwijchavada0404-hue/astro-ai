from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.runtime import configure_runtime
from app.core.settings import Settings


SECRET = "test-secret-with-at-least-thirty-two-characters"
ISSUER = "astroai-test"
AUDIENCE = "astroai-api-test"


def _settings(*, required: bool = True) -> Settings:
    return Settings(
        environment="test",
        cors_origins="",
        trusted_hosts="",
        auth_enabled=True,
        api_auth_required=required,
        auth_jwt_secret=SECRET,
        auth_jwt_issuer=ISSUER,
        auth_jwt_audience=AUDIENCE,
    )


def _token(**overrides) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "user_123",
        "iat": now,
        "exp": now + timedelta(minutes=30),
        "iss": ISSUER,
        "aud": AUDIENCE,
    }
    payload.update(overrides)
    return jwt.encode(payload, SECRET, algorithm="HS256")


def _app(*, required: bool = True) -> FastAPI:
    app = FastAPI()

    @app.post("/api/v1/question")
    def question():
        return {"ok": True}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return configure_runtime(app, _settings(required=required))


def test_api_routes_require_bearer_token_when_enabled():
    response = TestClient(_app()).post("/api/v1/question")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_api_routes_reject_invalid_token():
    response = TestClient(_app()).post(
        "/api/v1/question",
        headers={"Authorization": "Bearer invalid"},
    )
    assert response.status_code == 401


def test_api_routes_reject_token_without_subject():
    response = TestClient(_app()).post(
        "/api/v1/question",
        headers={"Authorization": f"Bearer {_token(sub='')}"},
    )
    assert response.status_code == 401
    assert "subject" in response.json()["detail"].lower()


def test_api_routes_accept_verified_token():
    response = TestClient(_app()).post(
        "/api/v1/question",
        headers={"Authorization": f"Bearer {_token()}"},
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_health_and_probe_routes_remain_public():
    client = TestClient(_app())
    assert client.get("/health").status_code == 200
    assert client.get("/livez").status_code == 200
    assert client.get("/readyz").status_code == 200


def test_legacy_api_remains_public_when_gate_is_disabled():
    response = TestClient(_app(required=False)).post("/api/v1/question")
    assert response.status_code == 200


def test_cors_preflight_is_not_blocked_by_bearer_gate():
    response = TestClient(_app()).options("/api/v1/question")
    assert response.status_code != 401
