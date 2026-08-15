from typing import Any


def _safe_dict(
    value: Any,
) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    return {}


def _sign_to_house_map(
    chart: dict[str, Any],
) -> dict[str, int]:
    """
    Build a sign -> natal house mapping from the
    chart's Whole Sign house structure.
    """

    houses = _safe_dict(
        chart.get("houses")
    )

    result: dict[str, int] = {}

    for house_number in range(
        1,
        13,
    ):
        house = _safe_dict(
            houses.get(
                str(house_number)
            )
        )

        sign = house.get(
            "sign"
        )

        if isinstance(
            sign,
            str,
        ):
            result[
                sign
            ] = house_number

    return result


def map_transits_to_natal_houses(
    chart: dict[str, Any],
    transits: dict[str, Any],
) -> dict[str, Any]:
    """
    Map sidereal transit signs into natal Whole Sign houses.

    This layer does not interpret whether a transit is good
    or bad. It only answers which natal house each transiting
    planet currently occupies.
    """

    if not isinstance(
        chart,
        dict,
    ):
        return {
            "available": False,
            "reason": (
                "Natal chart is unavailable."
            ),
        }

    if not transits.get(
        "available"
    ):
        return {
            "available": False,
            "reason": (
                "Transit calculation is unavailable."
            ),
        }

    sign_house_map = (
        _sign_to_house_map(
            chart
        )
    )

    if not sign_house_map:
        return {
            "available": False,
            "reason": (
                "Natal house-sign mapping is unavailable."
            ),
        }

    transit_planets = _safe_dict(
        transits.get(
            "planets"
        )
    )

    mapped_planets: dict[
        str,
        dict[str, Any],
    ] = {}

    for planet_name, data in (
        transit_planets.items()
    ):

        if not isinstance(
            data,
            dict,
        ):
            continue

        sign = data.get(
            "sign"
        )

        natal_house = (
            sign_house_map.get(
                sign
            )
        )

        mapped_planets[
            planet_name
        ] = {
            "planet": planet_name,
            "sign": sign,
            "longitude": data.get(
                "longitude"
            ),
            "degree_in_sign": data.get(
                "degree_in_sign"
            ),
            "retrograde": data.get(
                "retrograde"
            ),
            "nakshatra": data.get(
                "nakshatra"
            ),
            "natal_house": (
                natal_house
            ),
        }

    return {
        "available": True,
        "moment": transits.get(
            "moment"
        ),
        "system": transits.get(
            "system"
        ),
        "sign_house_map": (
            sign_house_map
        ),
        "planets": (
            mapped_planets
        ),
    }