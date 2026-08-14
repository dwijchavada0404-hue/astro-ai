from typing import Any


def _safe_dict(value: Any) -> dict[str, Any]:
    """Return a dictionary or an empty dictionary."""
    if isinstance(value, dict):
        return value
    return {}


def analyze_tenth_house(
    chart: dict[str, Any],
) -> dict[str, Any]:
    """
    Analyse the 10th house and 10th lord for career matters.

    This is the first reasoning layer for career analysis.
    It uses chart data already calculated by the astrology engine
    and does not perform new astronomical calculations.
    """

    houses = _safe_dict(
        chart.get("houses")
    )

    planets = _safe_dict(
        chart.get("planets")
    )

    tenth_house = _safe_dict(
        houses.get("10")
    )

    if not tenth_house:
        return {
            "available": False,
            "reason": "10th-house data is unavailable.",
        }

    tenth_sign = tenth_house.get("sign")
    tenth_lord_name = tenth_house.get("lord")

    tenth_lord = _safe_dict(
        planets.get(tenth_lord_name)
    )

    if not tenth_lord:
        return {
            "available": False,
            "reason": "10th-lord planetary data is unavailable.",
        }

    indicators: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # 10TH HOUSE SIGN
    # ---------------------------------------------------------

    indicators.append(
        {
            "factor": "tenth_house_sign",
            "interpretation": (
                f"The 10th house falls in {tenth_sign}, making "
                "the qualities of this sign relevant to career, "
                "professional direction and public responsibilities."
            ),
            "strength": 0.6,
            "type": "theme",
        }
    )

    # ---------------------------------------------------------
    # 10TH LORD PLACEMENT
    # ---------------------------------------------------------

    tenth_lord_house = tenth_lord.get("house")
    tenth_lord_sign = tenth_lord.get("sign")

    if tenth_lord_house is not None:
        indicators.append(
            {
                "factor": "tenth_lord_house",
                "interpretation": (
                    f"The 10th lord {tenth_lord_name} is placed "
                    f"in the {tenth_lord_house}th house. "
                    "This house becomes an important area through "
                    "which career and professional developments "
                    "may manifest."
                ),
                "strength": 0.8,
                "type": "theme",
            }
        )

    if tenth_lord_sign:
        indicators.append(
            {
                "factor": "tenth_lord_sign",
                "interpretation": (
                    f"The 10th lord {tenth_lord_name} is placed "
                    f"in {tenth_lord_sign}, adding the qualities "
                    "of this sign to professional expression."
                ),
                "strength": 0.6,
                "type": "theme",
            }
        )

    # ---------------------------------------------------------
    # PLANETS OCCUPYING THE 10TH HOUSE
    # ---------------------------------------------------------

    occupants: list[str] = []

    for planet_name, planet_data in planets.items():

        if not isinstance(planet_data, dict):
            continue

        if planet_data.get("house") == 10:
            occupants.append(planet_name)

    if occupants:
        indicators.append(
            {
                "factor": "tenth_house_occupants",
                "interpretation": (
                    "The 10th house contains "
                    + ", ".join(occupants)
                    + ". These planets may strongly influence "
                    "career direction, professional behaviour "
                    "and public responsibilities."
                ),
                "strength": 0.8,
                "type": "theme",
            }
        )

    # ---------------------------------------------------------
    # SATURN
    # ---------------------------------------------------------

    saturn = _safe_dict(
        planets.get("Saturn")
    )

    if saturn:
        saturn_house = saturn.get("house")

        indicators.append(
            {
                "factor": "saturn_house",
                "interpretation": (
                    f"Saturn is placed in the {saturn_house}th "
                    "house. Saturn's placement can describe areas "
                    "where discipline, persistence, responsibility "
                    "and gradual professional development become "
                    "important."
                ),
                "strength": 0.6,
                "type": "theme",
            }
        )

    # ---------------------------------------------------------
    # SUN
    # ---------------------------------------------------------

    sun = _safe_dict(
        planets.get("Sun")
    )

    if sun:
        sun_house = sun.get("house")

        indicators.append(
            {
                "factor": "sun_house",
                "interpretation": (
                    f"The Sun is placed in the {sun_house}th house. "
                    "Its placement may contribute themes of "
                    "authority, visibility, leadership and "
                    "professional recognition."
                ),
                "strength": 0.6,
                "type": "theme",
            }
        )

    return {
        "available": True,
        "tenth_house": {
            "sign": tenth_sign,
            "lord": tenth_lord_name,
            "occupants": occupants,
        },
        "tenth_lord": {
            "planet": tenth_lord_name,
            "house": tenth_lord_house,
            "sign": tenth_lord_sign,
            "longitude": tenth_lord.get("longitude"),
            "retrograde": tenth_lord.get("retrograde"),
        },
        "career_planets": {
            "Saturn": saturn,
            "Sun": sun,
        },
        "indicators": indicators,
    }