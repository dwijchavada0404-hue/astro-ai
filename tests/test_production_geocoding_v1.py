from types import SimpleNamespace

import pytest

from app.core.settings import Settings
from app.services import geocoding


def _production_settings(**overrides):
    values = {
        "environment": "production",
        "cors_origins": "https://astroai.example",
        "trusted_hosts": "astroai.example,healthcheck.railway.app",
        "docs_enabled": False,
        "security_headers_enabled": True,
        "rate_limit_enabled": True,
        "request_logging_enabled": True,
        "auth_enabled": True,
        "api_auth_required": True,
        "auth_jwt_secret": "x" * 40,
        "geocoding_provider": "openmapquest",
        "geocoding_api_key": "test-api-key",
    }
    values.update(overrides)
    return Settings(**values)


def test_production_rejects_public_nominatim():
    with pytest.raises(ValueError, match="Public Nominatim geocoding is not allowed"):
        _production_settings(geocoding_provider="nominatim", geocoding_api_key="")


def test_keyed_provider_requires_api_key():
    with pytest.raises(ValueError, match="ASTROAI_GEOCODING_API_KEY"):
        Settings(environment="staging", geocoding_provider="openmapquest", geocoding_api_key="")


def test_production_accepts_keyed_openmapquest():
    settings = _production_settings()
    assert settings.geocoding_provider == "openmapquest"


def test_resolve_place_uses_configured_provider_and_cache(monkeypatch):
    calls = []

    class FakeOpenMapQuest:
        def __init__(self, **kwargs):
            calls.append(("init", kwargs))

        def geocode(self, place, **kwargs):
            calls.append(("geocode", place, kwargs))
            return SimpleNamespace(
                latitude=19.076,
                longitude=72.8777,
                address="Mumbai, Maharashtra, India",
            )

    fake_settings = SimpleNamespace(
        geocoding_provider="openmapquest",
        geocoding_api_key="secret-key",
        geocoding_user_agent="astro-ai-test/1.0",
        geocoding_timeout_seconds=7,
    )
    monkeypatch.setattr(geocoding, "get_settings", lambda: fake_settings)
    monkeypatch.setattr(geocoding, "OpenMapQuest", FakeOpenMapQuest)
    monkeypatch.setattr(geocoding._tzf, "timezone_at", lambda **kwargs: "Asia/Kolkata")
    geocoding._resolve_normalized_place.cache_clear()

    first = geocoding.resolve_place(" Mumbai ")
    second = geocoding.resolve_place("Mumbai")

    assert first == second
    assert first["geocoding_provider"] == "openmapquest"
    assert first["timezone"] == "Asia/Kolkata"
    assert [call[0] for call in calls].count("geocode") == 1
    init = calls[0][1]
    assert init["api_key"] == "secret-key"
    assert init["timeout"] == 7
