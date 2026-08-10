from typing import Any

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


_geocoder = Nominatim(user_agent="astro-ai-milestone1/0.1")
_tzf = TimezoneFinder()


def resolve_place(place: str) -> dict[str, Any]:
    location = _geocoder.geocode(
        place,
        exactly_one=True,
        addressdetails=True,
        language="en",
        timeout=10,
    )

    if location is None:
        raise ValueError(f"Could not find birth place: {place}")

    latitude = float(location.latitude)
    longitude = float(location.longitude)
    timezone_name = _tzf.timezone_at(
        lat=latitude,
        lng=longitude
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
    }
