from typing import Any

from app.astrology.constants import SIGN_LORDS, SIGNS
from app.astrology.utils import dms, house_from_sign, sign_from_longitude


def dasamsa_longitude(sidereal_longitude: float) -> float:
    """Return classical Parashari D10 longitude for a sidereal D1 longitude.

    Each 30-degree sign is divided into ten 3-degree parts. Odd signs
    count forward from the natal sign itself; even signs count forward
    from the ninth sign from the natal sign.
    """
    longitude = float(sidereal_longitude) % 360.0
    sign_index = int(longitude // 30.0)
    degree_in_sign = longitude % 30.0
    segment_index = min(9, int(degree_in_sign // 3.0))

    if sign_index % 2 == 0:  # Aries is index 0 and is an odd-numbered sign.
        start_sign_index = sign_index
    else:
        start_sign_index = (sign_index + 8) % 12

    d10_sign_index = (start_sign_index + segment_index) % 12
    degree_in_d10_sign = (degree_in_sign % 3.0) * 10.0
    return (d10_sign_index * 30.0 + degree_in_d10_sign) % 360.0


def _dasamsa_position(longitude: float) -> dict[str, Any]:
    d10_longitude = dasamsa_longitude(longitude)
    sign, degree, sign_index = sign_from_longitude(d10_longitude)
    return {
        "longitude": round(d10_longitude, 8),
        "sign": sign,
        "sign_index": sign_index,
        "degree_in_sign": round(degree, 8),
        "degree_dms": dms(degree),
    }


def build_dasamsa_chart(calculated: dict[str, Any]) -> dict[str, Any]:
    """Build deterministic Dashamsha (D10) data from calculated D1 positions."""
    ascendant = _dasamsa_position(calculated["ascendant"]["longitude"])
    asc_sign_index = ascendant["sign_index"]

    planets: dict[str, Any] = {}
    for name, planet in calculated["planets"].items():
        position = _dasamsa_position(planet["longitude"])
        planets[name] = {
            **position,
            "house": house_from_sign(position["sign_index"], asc_sign_index),
            "retrograde": bool(planet.get("retrograde", False)),
            "d1_sign": planet.get("sign"),
            "same_sign_as_d1": planet.get("sign") == position["sign"],
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
        "chart": "D10",
        "name": "Dashamsha",
        "division": 10,
        "segment_degrees": 3.0,
        "method": "parashari_odd_even_dashamsha",
        "ascendant": {
            **ascendant,
            "house": 1,
            "d1_sign": calculated["ascendant"].get("sign"),
            "same_sign_as_d1": calculated["ascendant"].get("sign") == ascendant["sign"],
        },
        "planets": planets,
        "houses": houses,
    }
