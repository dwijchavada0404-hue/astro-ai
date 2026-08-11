from typing import Any


BENEFIC_PLANETS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFIC_PLANETS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}


def get_house(chart: dict[str, Any], house_number: int) -> dict[str, Any] | None:
    """
    Safely retrieve a house from the validated birth chart.
    """
    return chart.get("houses", {}).get(str(house_number))


def get_planet(chart: dict[str, Any], planet: str) -> dict[str, Any] | None:
    """
    Safely retrieve a planet from the validated birth chart.
    """
    return chart.get("planets", {}).get(planet)


def rule_seventh_lord_in_house(
    chart: dict[str, Any],
    seventh_lord: str | None,
) -> dict[str, Any] | None:
    """
    Identify the house occupied by the 7th lord.

    This is an evidence rule only. Interpretation will be
    added separately so that raw chart facts are not mixed
    with prediction language.
    """

    if not seventh_lord:
        return None

    placement = get_planet(chart, seventh_lord)

    if not placement:
        return None

    return {
        "rule": "seventh_lord_placement",
        "planet": seventh_lord,
        "house": placement.get("house"),
        "sign": placement.get("sign"),
        "strength": 1.0,
    }


def rule_venus_placement(
    chart: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Record Venus placement as a primary relationship indicator.
    """

    venus = get_planet(chart, "Venus")

    if not venus:
        return None

    return {
        "rule": "venus_placement",
        "planet": "Venus",
        "house": venus.get("house"),
        "sign": venus.get("sign"),
        "nakshatra": venus.get("nakshatra", {}).get("name"),
        "strength": 1.0,
    }


def rule_jupiter_placement(
    chart: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Record Jupiter placement as a supporting marriage indicator.
    """

    jupiter = get_planet(chart, "Jupiter")

    if not jupiter:
        return None

    return {
        "rule": "jupiter_placement",
        "planet": "Jupiter",
        "house": jupiter.get("house"),
        "sign": jupiter.get("sign"),
        "nakshatra": jupiter.get("nakshatra", {}).get("name"),
        "strength": 1.0,
    }


def rule_mars_placement(
    chart: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Record Mars placement for relationship dynamics.
    """

    mars = get_planet(chart, "Mars")

    if not mars:
        return None

    return {
        "rule": "mars_placement",
        "planet": "Mars",
        "house": mars.get("house"),
        "sign": mars.get("sign"),
        "strength": 1.0,
    }


def evaluate_marriage_rules(
    chart: dict[str, Any],
    seventh_lord: str | None,
) -> list[dict[str, Any]]:
    """
    Execute all currently available marriage rules.

    The returned objects are structured evidence. They deliberately
    do not contain final horoscope statements.
    """

    rules = [
        rule_seventh_lord_in_house(chart, seventh_lord),
        rule_venus_placement(chart),
        rule_jupiter_placement(chart),
        rule_mars_placement(chart),
    ]

    return [rule for rule in rules if rule is not None]