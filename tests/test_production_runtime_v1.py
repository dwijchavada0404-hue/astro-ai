import pytest
from fastapi import FastAPI

from app.core.runtime import DocsGuardMiddleware, RequestContextMiddleware, configure_runtime
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
        Settings(environment="production", cors_origins="*", trusted_hosts="api.example.com")


def test_production_requires_explicit_trusted_hosts():
    with pytest.raises(ValueError, match="Explicit trusted hosts"):
        Settings(environment="production", cors_origins="https://app.example.com", trusted_hosts="*")


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
    assert DocsGuardMiddleware in middleware_classes
    assert any(cls.__name__ == "TrustedHostMiddleware" for cls in middleware_classes)
    assert any(cls.__name__ == "CORSMiddleware" for cls in middleware_classes)


def test_request_id_header_name_is_configurable():
    app = FastAPI()
    settings = Settings(request_id_header="X-Correlation-ID")
    configure_runtime(app, settings)
    request_context = next(item for item in app.user_middleware if item.cls is RequestContextMiddleware)
    assert request_context.kwargs["header_name"] == "X-Correlation-ID"
