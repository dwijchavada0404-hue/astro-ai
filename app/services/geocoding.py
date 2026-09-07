from functools import lru_cache
from typing import Any

from geopy.exc import GeocoderServiceError, GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim, OpenMapQuest
from timezonefinder import TimezoneFinder

from app.core.settings import get_settings


# Preserve the legacy Nominatim instance as a stable seam for existing tests and
# development/staging behaviour. Production never reaches this path because
# Settings rejects public Nominatim when ASTROAI_ENVIRONMENT=production.
_geocoder = Nominatim(user_agent="astro-ai-milestone1/0.1")
_tzf = TimezoneFinder()


def resolve_place(place: str) -> dict[str, Any]:
    """Resolve a birth place without leaking provider failures to API callers."""

    normalized_place = place.strip()
    if not normalized_place:
        raise ValueError("Birth place must not be empty.")

    return _resolve_normalized_place(normalized_place)


@lru_cache(maxsize=1_024)
def _resolve_normalized_place(place: str) -> dict[str, Any]:
    settings = get_settings()
    provider = settings.geocoding_provider
    timeout = settings.geocoding_timeout_seconds

    if provider == "openmapquest":
        geocoder = OpenMapQuest(
            api_key=settings.geocoding_api_key,
            user_agent=settings.geocoding_user_agent,
            timeout=timeout,
        )
        geocode_kwargs = {
            "exactly_one": True,
            "timeout": timeout,
        }
    else:
        geocoder = _geocoder
        geocode_kwargs = {
            "exactly_one": True,
            "addressdetails": True,
            "language": "en",
            "timeout": timeout,
        }

    try:
        location = geocoder.geocode(place, **geocode_kwargs)
    except (GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError) as exc:
        raise ValueError(
            "Birth-place lookup is temporarily unavailable. Please try again in a moment."
        ) from exc

    if location is None:
        raise ValueError(f"Could not find birth place: {place}")

    latitude = float(location.latitude)
    longitude = float(location.longitude)
    timezone_name = _tzf.timezone_at(
        lat=latitude,
        lng=longitude,
    )

    if not timezone_name:
        raise ValueError(
            f"Could not determine timezone for: {location.address}"
        )

    return {
        "query": place,
        "resolved_name": location.address,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone_name,
        "geocoding_provider": provider,
    }
