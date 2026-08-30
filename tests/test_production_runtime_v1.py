import json
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.runtime import (
    ApiAccessControlMiddleware,
    DocsGuardMiddleware,
    RequestBodyLimitMiddleware,
    RequestContextMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    StructuredRequestLoggingMiddleware,
    configure_runtime,
)
from app.core.settings import Settings


def test_settings_parse_csv_values():
    settings = Settings(
        cors_origins="https://app.example.com, https://admin.example.com",
        trusted_hosts="api.example.com,localhost",
    )
    assert settings.cors_origin_list == ["https://app.example.com", "https://admin.example.com"]
    assert settings.trusted_host_list == ["api.example.com", "localhost"]


def test_production_rejects_wildcard_cors():
    with pytest.raises(ValueError, match="Wildcard CORS"):
        Settings(
            environment="production",
            cors_origins="*",
            trusted_hosts="api.example.com",
            docs_enabled=False,
            api_auth_required=True,
            auth_enabled=True,
            auth_jwt_secret="test-secret-with-at-least-thirty-two-characters",
        )


def test_production_requires_explicit_trusted_hosts():
    with pytest.raises(ValueError, match="Explicit trusted hosts"):
        Settings(
            environment="production",
            cors_origins="https://app.example.com",
            trusted_hosts="*",
            docs_enabled=False,
            api_auth_required=True,
            auth_enabled=True,
            auth_jwt_secret="test-secret-with-at-least-thirty-two-characters",
        )


def test_production_requires_docs_disabled():
    with pytest.raises(ValueError, match="docs must be disabled"):
        Settings(
            environment="production",
            cors_origins="https://app.example.com",
            trusted_hosts="api.example.com",
            docs_enabled=True,
            api_auth_required=True,
            auth_enabled=True,
            auth_jwt_secret="test-secret-with-at-least-thirty-two-characters",
        )


def test_production_requires_security_headers():
    with pytest.raises(ValueError, match="Security headers"):
        Settings(
            environment="production",
            cors_origins="https://app.example.com",
            trusted_hosts="api.example.com",
            docs_enabled=False,
            security_headers_enabled=False,
            api_auth_required=True,
            auth_enabled=True,
            auth_jwt_secret="test-secret-with-at-least-thirty-two-characters",
        )


def test_production_requires_api_bearer_authentication():
    with pytest.raises(ValueError, match="bearer authentication"):
        Settings(
            environment="production",
            cors_origins="https://app.example.com",
            trusted_hosts="api.example.com",
            docs_enabled=False,
        )


def test_production_requires_rate_limiting():
    with pytest.raises(ValueError, match="rate limiting"):
        Settings(
            environment="production",
            cors_origins="https://app.example.com",
            trusted_hosts="api.example.com",
            docs_enabled=False,
            auth_enabled=True,
            api_auth_required=True,
            auth_jwt_secret="test-secret-with-at-least-thirty-two-characters",
            rate_limit_enabled=False,
        )


def test_production_requires_structured_request_logging():
    with pytest.raises(ValueError, match="Structured request logging"):
        Settings(
            environment="production",
            cors_origins="https://app.example.com",
            trusted_hosts="api.example.com",
            docs_enabled=False,
            auth_enabled=True,
            api_auth_required=True,
            auth_jwt_secret="test-secret-with-at-least-thirty-two-characters",
            request_logging_enabled=False,
        )


def test_api_auth_requirement_requires_authentication_enabled():
    with pytest.raises(ValueError, match="AUTH_ENABLED"):
        Settings(api_auth_required=True)


def test_runtime_updates_metadata_and_adds_security_middleware():
    app = FastAPI()
    settings = Settings(
        app_name="AstroAI Production",
        app_version="1.0.0",
        cors_origins="https://app.example.com",
        trusted_hosts="api.example.com",
        docs_enabled=False,
    )
    configured = configure_runtime(app, settings)
    assert configured is app
    assert app.title == "AstroAI Production"
    assert app.version == "1.0.0"
    middleware_classes = [item.cls for item in app.user_middleware]
    assert RequestContextMiddleware in middleware_classes
    assert RequestBodyLimitMiddleware in middleware_classes
    assert SecurityHeadersMiddleware in middleware_classes
    assert RateLimitMiddleware in middleware_classes
    assert StructuredRequestLoggingMiddleware in middleware_classes
    assert DocsGuardMiddleware in middleware_classes
    assert any(cls.__name__ == "TrustedHostMiddleware" for cls in middleware_classes)
    assert any(cls.__name__ == "CORSMiddleware" for cls in middleware_classes)


def test_runtime_registers_api_access_control_when_required():
    app = FastAPI()
    configure_runtime(
        app,
        Settings(
            cors_origins="",
            trusted_hosts="",
            auth_enabled=True,
            api_auth_required=True,
            auth_jwt_secret="test-secret-with-at-least-thirty-two-characters",
        ),
    )
    assert ApiAccessControlMiddleware in [item.cls for item in app.user_middleware]


def test_request_id_header_name_is_configurable():
    app = FastAPI()
    settings = Settings(request_id_header="X-Correlation-ID")
    configure_runtime(app, settings)
    request_context = next(item for item in app.user_middleware if item.cls is RequestContextMiddleware)
    assert request_context.kwargs["header_name"] == "X-Correlation-ID"


def test_request_body_limit_is_configurable():
    app = FastAPI()
    settings = Settings(max_request_body_bytes=256)
    configure_runtime(app, settings)
    body_limit = next(item for item in app.user_middleware if item.cls is RequestBodyLimitMiddleware)
    assert body_limit.kwargs["max_bytes"] == 256


def test_liveness_and_readiness_probes_are_registered(tmp_path):
    app = FastAPI()
    configure_runtime(app, Settings(cors_origins="", trusted_hosts="", profile_database_path=str(tmp_path / "profiles.db")))
    client = TestClient(app)
    live = client.get("/livez")
    ready = client.get("/readyz")
    assert live.status_code == 200
    assert live.json()["status"] == "ok"
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert ready.json()["checks"]["profile_database"] == "ok"


def test_readiness_fails_when_database_cannot_be_opened(tmp_path):
    app = FastAPI()
    configure_runtime(app, Settings(cors_origins="", trusted_hosts="", profile_database_path=str(tmp_path)))
    response = TestClient(app).get("/readyz")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["checks"]["profile_database"] == "failed"


def test_security_headers_are_added():
    app = FastAPI()

    @app.get("/ping")
    def ping():
        return {"ok": True}

    configure_runtime(app, Settings(cors_origins="", trusted_hosts=""))
    response = TestClient(app).get("/ping")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Cache-Control"] == "no-store"


def test_oversized_request_is_rejected_before_handler():
    app = FastAPI()

    @app.post("/echo")
    async def echo():
        return {"ok": True}

    configure_runtime(app, Settings(cors_origins="", trusted_hosts="", max_request_body_bytes=4))
    response = TestClient(app).post("/echo", content=b"12345")
    assert response.status_code == 413
    assert response.json()["detail"] == "Request body too large."


def test_api_rate_limit_returns_retry_metadata():
    app = FastAPI()

    @app.get("/api/ping")
    def ping():
        return {"ok": True}

    configure_runtime(
        app,
        Settings(
            cors_origins="",
            trusted_hosts="",
            rate_limit_requests_per_minute=2,
        ),
    )
    client = TestClient(app)
    first = client.get("/api/ping")
    second = client.get("/api/ping")
    limited = client.get("/api/ping")

    assert first.status_code == 200
    assert first.headers["X-RateLimit-Remaining"] == "1"
    assert second.headers["X-RateLimit-Remaining"] == "0"
    assert limited.status_code == 429
    assert limited.headers["X-RateLimit-Limit"] == "2"
    assert int(limited.headers["Retry-After"]) >= 1


def test_rate_limit_does_not_throttle_health_probes():
    app = FastAPI()
    configure_runtime(
        app,
        Settings(cors_origins="", trusted_hosts="", rate_limit_requests_per_minute=1),
    )
    client = TestClient(app)
    assert client.get("/livez").status_code == 200
    assert client.get("/livez").status_code == 200


def test_cors_allows_personal_data_deletion_and_exposes_rate_headers():
    app = FastAPI()

    @app.delete("/api/v1/profile", status_code=204)
    def delete_profile():
        return None

    configure_runtime(
        app,
        Settings(cors_origins="https://app.example.com", trusted_hosts=""),
    )
    response = TestClient(app).options(
        "/api/v1/profile",
        headers={
            "Origin": "https://app.example.com",
            "Access-Control-Request-Method": "DELETE",
        },
    )
    assert response.status_code == 200
    assert "DELETE" in response.headers["Access-Control-Allow-Methods"]
    deletion = TestClient(app).delete(
        "/api/v1/profile",
        headers={"Origin": "https://app.example.com"},
    )
    assert deletion.status_code == 204
    assert "X-RateLimit-Limit" in deletion.headers["Access-Control-Expose-Headers"]


def test_structured_request_log_excludes_query_body_and_credentials(caplog):
    app = FastAPI()

    @app.post("/api/echo")
    def echo():
        return {"ok": True}

    configure_runtime(app, Settings(cors_origins="", trusted_hosts=""))
    with caplog.at_level(logging.INFO, logger="astroai.request"):
        response = TestClient(app).post(
            "/api/echo?birth_place=private",
            content="private question",
            headers={"Authorization": "Bearer private-token", "X-Request-ID": "trace-123"},
        )

    payload = json.loads(caplog.records[-1].message)
    assert payload["event"] == "request_completed"
    assert payload["route"] == "/api/echo"
    assert payload["request_id"] == "trace-123"
    assert payload["status_code"] == 200
    assert "private" not in caplog.records[-1].message
    assert "token" not in caplog.records[-1].message


def test_structured_log_uses_route_template_instead_of_record_identifier(caplog):
    app = FastAPI()

    @app.get("/api/conversations/{conversation_id}")
    def conversation(conversation_id: str):
        return {"conversation_id": conversation_id}

    configure_runtime(app, Settings(cors_origins="", trusted_hosts=""))
    with caplog.at_level(logging.INFO, logger="astroai.request"):
        response = TestClient(app).get("/api/conversations/private-record-123")

    assert response.status_code == 200
    payload = json.loads(caplog.records[-1].message)
    assert payload["route"] == "/api/conversations/{conversation_id}"
    assert "private-record-123" not in caplog.records[-1].message


def test_unhandled_error_is_logged_without_exception_message(caplog):
    app = FastAPI()

    @app.get("/api/fail")
    def fail():
        raise RuntimeError("sensitive birth detail")

    configure_runtime(app, Settings(cors_origins="", trusted_hosts=""))
    with caplog.at_level(logging.ERROR, logger="astroai.request"):
        response = TestClient(app, raise_server_exceptions=False).get("/api/fail")

    assert response.status_code == 500
    payload = json.loads(caplog.records[-1].message)
    assert payload["event"] == "request_failed"
    assert payload["error_type"] == "RuntimeError"
    assert "sensitive birth detail" not in caplog.records[-1].message
