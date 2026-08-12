from typing import Any

from app.astrology.dignity import evaluate_planetary_dignities


def _get_planet(chart: dict[str, Any], planet: str) -> dict[str, Any] | None:
    return chart.get("planets", {}).get(planet)


def _get_dignity_map(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """
    Build a lookup of planetary dignity information.

    Dignity is calculated by the central astrology dignity engine
    rather than duplicated inside the marriage reasoning layer.
    """

    dignities = evaluate_planetary_dignities(chart)

    return {
        item["planet"]: item
        for item in dignities
        if item.get("planet")
    }


def analyze_marriage_planets(chart: dict[str, Any]) -> dict[str, Any]:
    """
    Analyse Venus, Jupiter and Mars as marriage-related
    planetary indicators.

    This layer produces structured reasoning evidence only.
    It does not directly generate the final horoscope narrative.
    """

    venus = _get_planet(chart, "Venus")
    jupiter = _get_planet(chart, "Jupiter")
    mars = _get_planet(chart, "Mars")

    dignity_map = _get_dignity_map(chart)

    analysis: dict[str, Any] = {
        "available": True,
        "planets": {},
        "indicators": [],
    }

    indicators = analysis["indicators"]

    # ---------------------------------------------------------
    # Venus — primary relationship significator
    # ---------------------------------------------------------
    if venus:
        venus_dignity = dignity_map.get("Venus", {})

        venus_data = {
            "planet": "Venus",
            "house": venus.get("house"),
            "sign": venus.get("sign"),
            "nakshatra": venus.get("nakshatra"),
            "dignity": venus_dignity.get("dignity"),
            "dignity_strength": venus_dignity.get("strength"),
        }

        analysis["planets"]["Venus"] = venus_data

        if venus.get("house") == 11:
            indicators.append(
                {
                    "factor": "venus_house",
                    "value": 11,
                    "interpretation": (
                        "Venus in the 11th house may support relationships "
                        "through friendships, networks, social circles and "
                        "fulfilment of relationship desires."
                    ),
                    "strength": 0.7,
                }
            )

        if venus_dignity.get("dignity") == "exalted":
            indicators.append(
                {
                    "factor": "venus_dignity",
                    "value": "exalted",
                    "interpretation": (
                        "Venus is exalted, strengthening relationship "
                        "qualities such as affection, harmony, attraction "
                        "and appreciation of partnership."
                    ),
                    "strength": 1.0,
                }
            )

        elif venus_dignity.get("dignity") == "debilitated":
            indicators.append(
                {
                    "factor": "venus_dignity",
                    "value": "debilitated",
                    "interpretation": (
                        "A debilitated Venus may require greater care around "
                        "relationship expectations, harmony and emotional "
                        "balance."
                    ),
                    "strength": 0.7,
                }
            )

    # ---------------------------------------------------------
    # Jupiter — supporting marriage significator
    # ---------------------------------------------------------
    if jupiter:
        jupiter_dignity = dignity_map.get("Jupiter", {})

        jupiter_data = {
            "planet": "Jupiter",
            "house": jupiter.get("house"),
            "sign": jupiter.get("sign"),
            "nakshatra": jupiter.get("nakshatra"),
            "dignity": jupiter_dignity.get("dignity"),
            "dignity_strength": jupiter_dignity.get("strength"),
        }

        analysis["planets"]["Jupiter"] = jupiter_data

        if jupiter.get("house") == 12:
            indicators.append(
                {
                    "factor": "jupiter_house",
                    "value": 12,
                    "interpretation": (
                        "Jupiter in the 12th house may connect relationship "
                        "matters with travel, foreign environments, distance, "
                        "privacy or living away from the birthplace."
                    ),
                    "strength": 0.6,
                }
            )

        if jupiter_dignity.get("dignity") == "exalted":
            indicators.append(
                {
                    "factor": "jupiter_dignity",
                    "value": "exalted",
                    "interpretation": (
                        "Jupiter is exalted, strengthening supportive "
                        "qualities associated with wisdom, stability, "
                        "guidance and commitment."
                    ),
                    "strength": 0.9,
                }
            )

        elif jupiter_dignity.get("dignity") == "debilitated":
            indicators.append(
                {
                    "factor": "jupiter_dignity",
                    "value": "debilitated",
                    "interpretation": (
                        "A debilitated Jupiter may require greater care "
                        "around judgement, expectations and guidance "
                        "within relationships."
                    ),
                    "strength": 0.7,
                }
            )

    # ---------------------------------------------------------
    # Mars — relationship dynamics / 7th lord support
    # ---------------------------------------------------------
    if mars:
        mars_dignity = dignity_map.get("Mars", {})

        mars_data = {
            "planet": "Mars",
            "house": mars.get("house"),
            "sign": mars.get("sign"),
            "nakshatra": mars.get("nakshatra"),
            "dignity": mars_dignity.get("dignity"),
            "dignity_strength": mars_dignity.get("strength"),
        }

        analysis["planets"]["Mars"] = mars_data

        if mars.get("house") == 12:
            indicators.append(
                {
                    "factor": "mars_house",
                    "value": 12,
                    "interpretation": (
                        "Mars in the 12th house may bring themes of privacy, "
                        "distance, relocation or expenditure into "
                        "relationship dynamics."
                    ),
                    "strength": 0.6,
                }
            )

        if mars_dignity.get("dignity") == "own_sign":
            indicators.append(
                {
                    "factor": "mars_dignity",
                    "value": "own_sign",
                    "interpretation": (
                        "Mars is in its own sign, strengthening initiative, "
                        "assertiveness, independence and the ability to act "
                        "decisively in relationship matters."
                    ),
                    "strength": 0.85,
                }
            )

        elif mars_dignity.get("dignity") == "debilitated":
            indicators.append(
                {
                    "factor": "mars_dignity",
                    "value": "debilitated",
                    "interpretation": (
                        "A debilitated Mars may require greater care around "
                        "assertiveness, conflict management and impulsive "
                        "relationship dynamics."
                    ),
                    "strength": 0.7,
                }
            )

    return analysis