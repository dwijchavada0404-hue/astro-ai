from typing import Any

from app.astrology.constants import SIGN_LORDS, SIGNS
from app.astrology.utils import dms, house_from_sign, sign_from_longitude


def navamsa_longitude(sidereal_longitude: float) -> float:
    """Return D9 longitude for a sidereal D1 longitude.

    Navamsa divides the zodiac into 108 equal parts of 3°20′. Mapping
    each part cyclically through the zodiac is equivalent to the
    classical movable/fixed/dual start-sign rule.
    """
    return (float(sidereal_longitude) * 9.0) % 360.0


def _navamsa_position(longitude: float) -> dict[str, Any]:
    d9_longitude = navamsa_longitude(longitude)
    sign, degree, sign_index = sign_from_longitude(d9_longitude)
    return {
        "longitude": round(d9_longitude, 8),
        "sign": sign,
        "sign_index": sign_index,
        "degree_in_sign": round(degree, 8),
        "degree_dms": dms(degree),
    }


def build_navamsa_chart(calculated: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic Navamsa (D9) chart from calculated D1 data."""
    ascendant = _navamsa_position(calculated["ascendant"]["longitude"])
    asc_sign_index = ascendant["sign_index"]

    planets: dict[str, Any] = {}
    for name, planet in calculated["planets"].items():
        position = _navamsa_position(planet["longitude"])
        planets[name] = {
            **position,
            "house": house_from_sign(position["sign_index"], asc_sign_index),
            "retrograde": bool(planet.get("retrograde", False)),
            "d1_sign": planet.get("sign"),
            "vargottama": planet.get("sign") == position["sign"],
        }

    houses: dict[str, Any] = {}
    for house_number in range(1, 13):
        sign_index = (asc_sign_index + house_number - 1) % 12
        sign = SIGNS[sign_index]
        houses[str(house_number)] = {
            "sign": sign,
            "sign_index": sign_index,
            "lord": SIGN_LORDS[sign],
        }

    return {
        "chart": "D9",
        "name": "Navamsa",
        "division": 9,
        "segment_degrees": 30.0 / 9.0,
        "method": "classical_navamsa",
        "ascendant": {
            **ascendant,
            "house": 1,
            "d1_sign": calculated["ascendant"].get("sign"),
            "vargottama": calculated["ascendant"].get("sign") == ascendant["sign"],
        },
        "planets": planets,
        "houses": houses,
    }
