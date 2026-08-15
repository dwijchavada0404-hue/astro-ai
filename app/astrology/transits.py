from datetime import datetime, timezone
from typing import Any

import swisseph as swe

from app.astrology.constants import PLANETS
from app.astrology.utils import (
    dms,
    nakshatra_from_longitude,
    sign_from_longitude,
)


swe.set_sid_mode(
    swe.SIDM_LAHIRI
)


def _planet_id(
    name: str,
) -> int:
    return getattr(
        swe,
        PLANETS[name],
    )


def _calc_sidereal_longitude(
    jd_ut: float,
    planet_id: int,
) -> float:
    flags = (
        swe.FLG_SWIEPH
        | swe.FLG_SIDEREAL
    )

    result = swe.calc_ut(
        jd_ut,
        planet_id,
        flags,
    )

    xx = result[0]

    return (
        xx[0]
        % 360.0
    )


def _is_retrograde(
    jd_ut: float,
    planet_id: int,
) -> bool:
    flags = (
        swe.FLG_SWIEPH
        | swe.FLG_SIDEREAL
        | swe.FLG_SPEED
    )

    result = swe.calc_ut(
        jd_ut,
        planet_id,
        flags,
    )

    xx = result[0]

    return (
        xx[3]
        < 0
    )


def _julian_day(
    moment: datetime,
) -> float:
    if moment.tzinfo is None:
        raise ValueError(
            "moment must be timezone-aware"
        )

    utc = moment.astimezone(
        timezone.utc
    )

    hour_decimal = (
        utc.hour
        + utc.minute / 60.0
        + utc.second / 3600.0
        + utc.microsecond
        / 3_600_000_000.0
    )

    return swe.julday(
        utc.year,
        utc.month,
        utc.day,
        hour_decimal,
        swe.GREG_CAL,
    )


def calculate_transits(
    moment: datetime,
) -> dict[str, Any]:
    """
    Calculate Lahiri sidereal planetary transits
    for a timezone-aware moment.

    This function calculates planetary positions only.

    It does not interpret:
    - career effects
    - marriage effects
    - transit aspects
    - house activation

    Those belong in higher reasoning layers.
    """

    jd_ut = _julian_day(
        moment
    )

    planets: dict[
        str,
        Any,
    ] = {}

    for name in PLANETS:

        longitude = (
            _calc_sidereal_longitude(
                jd_ut,
                _planet_id(name),
            )
        )

        sign, degree, sign_index = (
            sign_from_longitude(
                longitude
            )
        )

        planets[name] = {
            "longitude": round(
                longitude,
                8,
            ),
            "sign": sign,
            "sign_index": sign_index,
            "degree_in_sign": round(
                degree,
                8,
            ),
            "degree_dms": dms(
                degree
            ),
            "nakshatra": (
                nakshatra_from_longitude(
                    longitude
                )
            ),
            "retrograde": (
                _is_retrograde(
                    jd_ut,
                    _planet_id(name),
                )
            ),
        }

    # Ketu is always exactly opposite Rahu.
    rahu_longitude = (
        planets["Rahu"][
            "longitude"
        ]
    )

    ketu_longitude = (
        rahu_longitude
        + 180.0
    ) % 360.0

    ketu_sign, ketu_degree, ketu_sign_index = (
        sign_from_longitude(
            ketu_longitude
        )
    )

    planets["Ketu"] = {
        "longitude": round(
            ketu_longitude,
            8,
        ),
        "sign": ketu_sign,
        "sign_index": ketu_sign_index,
        "degree_in_sign": round(
            ketu_degree,
            8,
        ),
        "degree_dms": dms(
            ketu_degree
        ),
        "nakshatra": (
            nakshatra_from_longitude(
                ketu_longitude
            )
        ),
        "retrograde": True,
    }

    return {
        "available": True,
        "system": "Lahiri sidereal",
        "moment": (
            moment.isoformat()
        ),
        "julian_day_ut": jd_ut,
        "planets": planets,
    }