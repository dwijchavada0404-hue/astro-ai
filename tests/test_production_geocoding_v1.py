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


def test_production_rejects_public_nominatim():
    with pytest.raises(ValueError, match="Public Nominatim geocoding is not allowed"):
        _production_settings(geocoding_provider="nominatim", geocoding_api_key="")


def test_keyed_provider_requires_api_key():
    with pytest.raises(ValueError, match="ASTROAI_GEOCODING_API_KEY"):
        Settings(environment="staging", geocoding_provider="openmapquest", geocoding_api_key="")


def test_geoapify_requires_api_key():
    with pytest.raises(ValueError, match="ASTROAI_GEOCODING_API_KEY"):
        Settings(environment="staging", geocoding_provider="geoapify", geocoding_api_key="")


def test_production_accepts_keyed_openmapquest():
    settings = _production_settings()
    assert settings.geocoding_provider == "openmapquest"


def test_production_accepts_keyed_geoapify():
    settings = _production_settings(geocoding_provider="geoapify")
    assert settings.geocoding_provider == "geoapify"


def test_cached_resolver_uses_configured_provider(monkeypatch):
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
    fake_timezone_finder = SimpleNamespace(timezone_at=lambda **kwargs: "Asia/Kolkata")
    monkeypatch.setattr(geocoding, "get_settings", lambda: fake_settings)
    monkeypatch.setattr(geocoding, "OpenMapQuest", FakeOpenMapQuest)
    monkeypatch.setattr(geocoding, "_tzf", fake_timezone_finder)
    geocoding._resolve_normalized_place.cache_clear()

    first = geocoding._resolve_normalized_place("Mumbai")
    second = geocoding._resolve_normalized_place("Mumbai")

    assert first == second
    assert first["geocoding_provider"] == "openmapquest"
    assert first["timezone"] == "Asia/Kolkata"
    assert [call[0] for call in calls].count("geocode") == 1
    init = calls[0][1]
    assert init["api_key"] == "secret-key"
    assert init["timeout"] == 7


def test_cached_resolver_uses_geoapify(monkeypatch):
    calls = []

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "results": [{
                    "lat": 19.076,
                    "lon": 72.8777,
                    "formatted": "Mumbai, Maharashtra, India",
                }]
            }

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse()

    fake_settings = SimpleNamespace(
        geocoding_provider="geoapify",
        geocoding_api_key="secret-key",
        geocoding_user_agent="astro-ai-test/1.0",
        geocoding_timeout_seconds=7,
    )
    fake_timezone_finder = SimpleNamespace(timezone_at=lambda **kwargs: "Asia/Kolkata")
    monkeypatch.setattr(geocoding, "get_settings", lambda: fake_settings)
    monkeypatch.setattr(geocoding.requests, "get", fake_get)
    monkeypatch.setattr(geocoding, "_tzf", fake_timezone_finder)
    geocoding._resolve_normalized_place.cache_clear()

    first = geocoding._resolve_normalized_place("Mumbai")
    second = geocoding._resolve_normalized_place("Mumbai")

    assert first == second
    assert first["geocoding_provider"] == "geoapify"
    assert first["resolved_name"] == "Mumbai, Maharashtra, India"
    assert first["timezone"] == "Asia/Kolkata"
    assert len(calls) == 1
    url, kwargs = calls[0]
    assert url == "https://api.geoapify.com/v1/geocode/search"
    assert kwargs["params"]["text"] == "Mumbai"
    assert kwargs["params"]["apiKey"] == "secret-key"
    assert kwargs["params"]["limit"] == 1
    assert kwargs["timeout"] == 7
