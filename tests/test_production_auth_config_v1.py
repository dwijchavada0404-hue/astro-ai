import pytest

from app.core.settings import Settings


def _production_settings(**overrides):
    values = {
        "environment": "production",
        "cors_origins": "https://app.astroai.example",
        "trusted_hosts": "api.astroai.example,healthcheck.railway.app",
        "docs_enabled": False,
        "security_headers_enabled": True,
        "rate_limit_enabled": True,
        "request_logging_enabled": True,
        "auth_enabled": True,
        "api_auth_required": True,
        "auth_jwks_url": "https://tenant.example/.well-known/jwks.json",
        "auth_jwt_algorithm": "RS256",
        "auth_jwt_issuer": "https://tenant.example/",
        "auth_jwt_audience": "https://api.astroai.example",
        "geocoding_provider": "openmapquest",
        "geocoding_api_key": "test-api-key",
        "profile_database_path": "/data/astroai_profiles.db",
    }
    values.update(overrides)
    return Settings(**values)


def test_production_accepts_explicit_asymmetric_oidc_contract():
    settings = _production_settings()
    assert settings.auth_jwt_algorithm == "RS256"
    assert settings.auth_jwks_url.startswith("https://")
    assert settings.auth_jwt_issuer == "https://tenant.example/"
    assert settings.auth_jwt_audience == "https://api.astroai.example"


def test_production_rejects_symmetric_jwt_secret_authentication():
    with pytest.raises(ValueError, match="HTTPS JWKS endpoint"):
        _production_settings(
            auth_jwks_url="",
            auth_jwt_algorithm="HS256",
            auth_jwt_secret="x" * 40,
        )


def test_production_rejects_non_https_issuer():
    with pytest.raises(ValueError, match="issuer must be an explicit HTTPS"):
        _production_settings(auth_jwt_issuer="astroai")


def test_production_rejects_placeholder_audience():
    with pytest.raises(ValueError, match="audience must be explicitly configured"):
        _production_settings(auth_jwt_audience="astroai-api")
