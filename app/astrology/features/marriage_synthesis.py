from typing import Any


def synthesize_marriage(
    seventh_house_analysis: dict[str, Any],
    marriage_planet_analysis: dict[str, Any],
) -> dict[str, Any]:
    """
    Combine 7th-house reasoning and planetary marriage indicators
    into higher-level marriage conclusions.

    This layer synthesizes existing evidence. It does not calculate
    new astronomical or chart data.
    """

    if not seventh_house_analysis.get("available"):
        return {
            "available": False,
            "reason": "7th-house analysis is unavailable.",
        }

    if not marriage_planet_analysis.get("available"):
        return {
            "available": False,
            "reason": "Marriage planetary analysis is unavailable.",
        }

    indicators = []

    # ---------------------------------------------------------
    # 7th LORD STRENGTH
    # ---------------------------------------------------------

    seventh_lord = seventh_house_analysis.get("seventh_lord", {})
    dignity = seventh_lord.get("dignity", {})
    dignity_name = dignity.get("dignity")
    dignity_strength = dignity.get("strength", 0.0)

    if dignity_name in {"own_sign", "exalted"}:
        indicators.append(
            {
                "factor": "strong_seventh_lord",
                "interpretation": (
                    "The 7th lord has strong dignity, which supports "
                    "the ability of marriage-related matters to manifest."
                ),
                "strength": dignity_strength,
                "type": "positive",
            }
        )

    elif dignity_name == "debilitated":
        indicators.append(
            {
                "factor": "weak_seventh_lord",
                "interpretation": (
                    "The 7th lord is debilitated, which may create "
                    "additional challenges or delays in relationship matters."
                ),
                "strength": 0.25,
                "type": "challenge",
            }
        )

    # ---------------------------------------------------------
    # VENUS
    # ---------------------------------------------------------

    planets = marriage_planet_analysis.get("planets", {})
    venus = planets.get("Venus", {})

    venus_dignity = venus.get("dignity")

    if venus_dignity == "exalted":
        indicators.append(
            {
                "factor": "strong_venus",
                "interpretation": (
                    "Exalted Venus provides a strong supportive influence "
                    "for affection, attraction, harmony and partnership."
                ),
                "strength": 1.0,
                "type": "positive",
            }
        )

    # Venus in 11th
    if venus.get("house") == 11:
        indicators.append(
            {
                "factor": "venus_eleventh_house",
                "interpretation": (
                    "Venus in the 11th house supports fulfilment of "
                    "relationship desires and connections through "
                    "social networks or friendships."
                ),
                "strength": 0.7,
                "type": "positive",
            }
        )

    # ---------------------------------------------------------
    # 12TH HOUSE THEMES
    # ---------------------------------------------------------

    seventh_lord_house = seventh_lord.get("house")

    if seventh_lord_house == 12:
        indicators.append(
            {
                "factor": "seventh_lord_twelfth_house",
                "interpretation": (
                    "The 7th lord in the 12th house can introduce themes "
                    "of distance, relocation, foreign environments, privacy "
                    "or living away from the birthplace."
                ),
                "strength": 0.7,
                "type": "theme",
            }
        )

    mars = planets.get("Mars", {})

    if mars.get("house") == 12:
        indicators.append(
            {
                "factor": "mars_twelfth_house",
                "interpretation": (
                    "Mars in the 12th house can add intensity, privacy, "
                    "distance or relocation themes to relationship dynamics."
                ),
                "strength": 0.6,
                "type": "theme",
            }
        )

    # ---------------------------------------------------------
    # OVERALL ASSESSMENT
    # ---------------------------------------------------------

    positive_strength = sum(
        item["strength"]
        for item in indicators
        if item["type"] == "positive"
    )

    challenge_strength = sum(
        item["strength"]
        for item in indicators
        if item["type"] == "challenge"
    )

    if positive_strength >= challenge_strength + 1.0:
        outlook = "favourable"
    elif challenge_strength > positive_strength:
        outlook = "mixed"
    else:
        outlook = "generally favourable with some challenges"

    # Confidence is deliberately bounded.
    confidence = min(
        0.95,
        max(
            0.50,
            0.60 + (positive_strength - challenge_strength) * 0.08,
        ),
    )

    return {
        "available": True,
        "outlook": outlook,
        "confidence": round(confidence, 2),
        "positive_factors": [
            item for item in indicators if item["type"] == "positive"
        ],
        "themes": [
            item for item in indicators if item["type"] == "theme"
        ],
        "challenges": [
            item for item in indicators if item["type"] == "challenge"
        ],
        "indicators": indicators,
    }