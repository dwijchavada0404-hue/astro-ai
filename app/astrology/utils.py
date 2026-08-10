from datetime import datetime, timezone
from typing import Any

from app.astrology.constants import NAKSHATRAS, SIGNS


def normalize_degrees(value: float) -> float:
    return value % 360.0


def sign_from_longitude(longitude: float) -> tuple[str, float, int]:
    longitude = normalize_degrees(longitude)
    sign_index = int(longitude // 30)
    degree_in_sign = longitude - (sign_index * 30)
    return SIGNS[sign_index], degree_in_sign, sign_index


def dms(degrees: float) -> dict[str, float | int]:
    degrees = normalize_degrees(degrees)
    deg = int(degrees)
    minutes_float = (degrees - deg) * 60
    minutes = int(minutes_float)
    seconds = round((minutes_float - minutes) * 60, 2)
    return {"degrees": deg, "minutes": minutes, "seconds": seconds}


def nakshatra_from_longitude(longitude: float) -> dict[str, Any]:
    """
    27 nakshatras, each 13°20'.
    Pada is 1..4, each 3°20'.
    """
    longitude = normalize_degrees(longitude)
    nak_span = 360.0 / 27.0
    pada_span = nak_span / 4.0

    index = min(int(longitude / nak_span), 26)
    within = longitude - index * nak_span
    pada = min(int(within / pada_span) + 1, 4)

    name, lord = NAKSHATRAS[index]

    return {
        "name": name,
        "lord": lord,
        "number": index + 1,
        "pada": pada,
        "degrees_into_nakshatra": round(within, 8),
    }


def house_from_sign(planet_sign_index: int, ascendant_sign_index: int) -> int:
    return ((planet_sign_index - ascendant_sign_index) % 12) + 1


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()
