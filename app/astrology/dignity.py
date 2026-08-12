from typing import Any


SIGN_INDEX = {
    "Aries": 0,
    "Taurus": 1,
    "Gemini": 2,
    "Cancer": 3,
    "Leo": 4,
    "Virgo": 5,
    "Libra": 6,
    "Scorpio": 7,
    "Sagittarius": 8,
    "Capricorn": 9,
    "Aquarius": 10,
    "Pisces": 11,
}


EXALTATION = {
    "Sun": 0,
    "Moon": 1,
    "Mars": 9,
    "Mercury": 5,
    "Jupiter": 3,
    "Venus": 11,
    "Saturn": 6,
}


DEBILITATION = {
    "Sun": 6,
    "Moon": 7,
    "Mars": 3,
    "Mercury": 11,
    "Jupiter": 9,
    "Venus": 5,
    "Saturn": 0,
}


OWN_SIGNS = {
    "Sun": {4},
    "Moon": {3},
    "Mars": {0, 7},
    "Mercury": {2, 5},
    "Jupiter": {8, 11},
    "Venus": {1, 6},
    "Saturn": {9, 10},
}


def get_planet_sign_index(
    planet_data: dict[str, Any],
) -> int | None:
    """
    Retrieve the sidereal sign index from the validated chart.
    """

    sign = planet_data.get("sign")

    if not isinstance(sign, str):
        return None

    return SIGN_INDEX.get(sign)


def calculate_dignity(
    planet: str,
    planet_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Determine basic planetary dignity from the planet's sidereal sign.

    Priority:
    1. Exalted
    2. Debilitated
    3. Own sign
    4. Ordinary placement
    """

    sign_index = get_planet_sign_index(planet_data)

    result = {
        "planet": planet,
        "sign": planet_data.get("sign"),
        "sign_index": sign_index,
        "dignity": "unknown",
        "strength": 0.0,
    }

    if sign_index is None:
        return result

    if EXALTATION.get(planet) == sign_index:
        result["dignity"] = "exalted"
        result["strength"] = 1.0
        return result

    if DEBILITATION.get(planet) == sign_index:
        result["dignity"] = "debilitated"
        result["strength"] = 0.25
        return result

    if sign_index in OWN_SIGNS.get(planet, set()):
        result["dignity"] = "own_sign"
        result["strength"] = 0.85
        return result

    result["dignity"] = "ordinary"
    result["strength"] = 0.5

    return result


def evaluate_planetary_dignities(
    chart: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Calculate basic dignity for all planets available in the chart.
    """

    planets = chart.get("planets", {})

    results = []

    for planet, planet_data in planets.items():
        if not isinstance(planet_data, dict):
            continue

        results.append(
            calculate_dignity(
                planet,
                planet_data,
            )
        )

    return results