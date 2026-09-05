from types import SimpleNamespace

import pytest
from geopy.exc import GeocoderTimedOut

from app.services import geocoding


def test_resolve_place_returns_actionable_error_when_provider_times_out(monkeypatch):
    def timeout(*args, **kwargs):
        raise GeocoderTimedOut("Nominatim did not respond")

    monkeypatch.setattr(geocoding._geocoder, "geocode", timeout)
    geocoding._resolve_normalized_place.cache_clear()

    with pytest.raises(ValueError, match="temporarily unavailable"):
        geocoding.resolve_place("Mumbai")


def test_resolve_place_caches_normalized_queries(monkeypatch):
    calls = 0

    def geocode(*args, **kwargs):
        nonlocal calls
        calls += 1
        return SimpleNamespace(latitude=19.076, longitude=72.8777, address="Mumbai, India")

    monkeypatch.setattr(geocoding._geocoder, "geocode", geocode)
    monkeypatch.setattr(
        type(geocoding._tzf),
        "timezone_at",
        lambda self, **kwargs: "Asia/Kolkata",
    )
    geocoding._resolve_normalized_place.cache_clear()

    assert geocoding.resolve_place("Mumbai") == geocoding.resolve_place(" Mumbai ")
    assert calls == 1
