from datetime import datetime, timezone
from typing import Any

import swisseph as swe

from app.astrology.constants import PLANETS, SIGN_LORDS, SIGNS
from app.astrology.utils import (
    dms,
    house_from_sign,
    nakshatra_from_longitude,
    sign_from_longitude,
)


def _planet_id(name: str) -> int:
    return getattr(swe, PLANETS[name])


def _calc_sidereal_longitude(
    jd_ut: float,
    planet_id: int,
) -> float:
    """
    Calculate Lahiri sidereal planetary longitude.
    """

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

    return xx[0] % 360.0


def _is_retrograde(
    jd_ut: float,
    planet_id: int,
) -> bool:
    """
    Determine whether a planet is retrograde.
    """

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

    return xx[3] < 0


def calculate_chart(
    birth_utc: datetime,
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    """
    Calculate a Lahiri sidereal Vedic astrology chart.

    Methodology:
    - Swiss Ephemeris
    - Lahiri ayanamsa
    - Sidereal zodiac
    - Whole Sign houses
    - Mean lunar node
    """

    if birth_utc.tzinfo is None:
        raise ValueError(
            "birth_utc must be timezone-aware"
        )

    # ---------------------------------------------------------
    # IMPORTANT:
    # Explicitly reset Lahiri mode for every chart calculation.
    #
    # Swiss Ephemeris sidereal mode is global state, so this
    # prevents a previous calculation elsewhere in the same
    # process from affecting this chart.
    # ---------------------------------------------------------

    swe.set_sid_mode(
        swe.SIDM_LAHIRI
    )

    utc = birth_utc.astimezone(
        timezone.utc
    )

    hour_decimal = (
        utc.hour
        + utc.minute / 60.0
        + utc.second / 3600.0
        + utc.microsecond / 3_600_000_000.0
    )

    jd_ut = swe.julday(
        utc.year,
        utc.month,
        utc.day,
        hour_decimal,
        swe.GREG_CAL,
    )

    # ---------------------------------------------------------
    # Ascendant
    # ---------------------------------------------------------
    #
    # houses() returns the tropical Ascendant.
    # We convert that Ascendant to Lahiri sidereal longitude.
    #
    # Whole Sign houses are subsequently derived from the
    # resulting sidereal Ascendant sign.
    # ---------------------------------------------------------

    _, ascmc = swe.houses(
        jd_ut,
        latitude,
        longitude,
        b"P",
    )

    tropical_ascendant = (
        ascmc[0] % 360.0
    )

    ayanamsa = swe.get_ayanamsa_ut(
        jd_ut
    )

    asc_longitude = (
        tropical_ascendant
        - ayanamsa
    ) % 360.0

    (
        asc_sign,
        asc_degree,
        asc_sign_index,
    ) = sign_from_longitude(
        asc_longitude
    )

    # ---------------------------------------------------------
    # Planets
    # ---------------------------------------------------------

    planets: dict[str, Any] = {}

    for name in PLANETS:

        planet_id = _planet_id(name)

        longitude_value = (
            _calc_sidereal_longitude(
                jd_ut,
                planet_id,
            )
        )

        (
            sign,
            degree,
            sign_index,
        ) = sign_from_longitude(
            longitude_value
        )

        planets[name] = {
            "longitude": round(
                longitude_value,
                8,
            ),
            "sign": sign,
            "degree_in_sign": round(
                degree,
                8,
            ),
            "degree_dms": dms(
                degree
            ),
            "house": house_from_sign(
                sign_index,
                asc_sign_index,
            ),
            "nakshatra": (
                nakshatra_from_longitude(
                    longitude_value
                )
            ),
            "retrograde": (
                _is_retrograde(
                    jd_ut,
                    planet_id,
                )
            ),
        }

    # ---------------------------------------------------------
    # Ketu
    # ---------------------------------------------------------
    #
    # Ketu is exactly opposite Rahu.
    # ---------------------------------------------------------

    rahu_longitude = planets[
        "Rahu"
    ]["longitude"]

    ketu_longitude = (
        rahu_longitude
        + 180.0
    ) % 360.0

    (
        ketu_sign,
        ketu_degree,
        ketu_sign_index,
    ) = sign_from_longitude(
        ketu_longitude
    )

    planets["Ketu"] = {
        "longitude": round(
            ketu_longitude,
            8,
        ),
        "sign": ketu_sign,
        "degree_in_sign": round(
            ketu_degree,
            8,
        ),
        "degree_dms": dms(
            ketu_degree
        ),
        "house": house_from_sign(
            ketu_sign_index,
            asc_sign_index,
        ),
        "nakshatra": (
            nakshatra_from_longitude(
                ketu_longitude
            )
        ),
        "retrograde": True,
    }

    # ---------------------------------------------------------
    # Whole Sign houses
    # ---------------------------------------------------------

    houses: dict[str, Any] = {}

    for house_number in range(
        1,
        13,
    ):

        sign_index = (
            asc_sign_index
            + house_number
            - 1
        ) % 12

        sign = SIGNS[
            sign_index
        ]

        houses[
            str(house_number)
        ] = {
            "sign": sign,
            "sign_index": sign_index,
            "lord": SIGN_LORDS[
                sign
            ],
        }

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    return {
        "julian_day_ut": jd_ut,
        "ayanamsa": {
            "name": "Lahiri",
            "value": round(
                ayanamsa,
                8,
            ),
        },
        "ascendant": {
            "longitude": round(
                asc_longitude,
                8,
            ),
            "sign": asc_sign,
            "degree_in_sign": round(
                asc_degree,
                8,
            ),
            "degree_dms": dms(
                asc_degree
            ),
        },
        "planets": planets,
        "houses": houses,
    }