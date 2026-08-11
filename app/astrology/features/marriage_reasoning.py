from typing import Any


# Vedic astrology: natural planetary relationships.
# This is intentionally kept explicit so the reasoning layer
# remains transparent and testable.
FRIENDLY_SIGNS = {
    "Sun": {"Aries", "Leo", "Sagittarius"},
    "Moon": {"Taurus", "Cancer", "Scorpio"},
    "Mars": {"Aries", "Scorpio", "Sagittarius", "Pisces"},
    "Mercury": {"Gemini", "Virgo", "Libra", "Aquarius"},
    "Jupiter": {"Sagittarius", "Pisces", "Cancer", "Aries"},
    "Venus": {"Taurus", "Libra", "Pisces", "Gemini"},
    "Saturn": {"Capricorn", "Aquarius", "Libra"},
}


SIGN_ELEMENTS = {
    "Aries": "fire",
    "Leo": "fire",
    "Sagittarius": "fire",
    "Taurus": "earth",
    "Virgo": "earth",
    "Capricorn": "earth",
    "Gemini": "air",
    "Libra": "air",
    "Aquarius": "air",
    "Cancer": "water",
    "Scorpio": "water",
    "Pisces": "water",
}


SIGN_MODALITIES = {
    "Aries": "movable",
    "Cancer": "movable",
    "Libra": "movable",
    "Capricorn": "movable",
    "Taurus": "fixed",
    "Leo": "fixed",
    "Scorpio": "fixed",
    "Aquarius": "fixed",
    "Gemini": "dual",
    "Virgo": "dual",
    "Sagittarius": "dual",
    "Pisces": "dual",
}


def analyze_seventh_house(chart: dict[str, Any]) -> dict[str, Any]:
    """
    Analyse the 7th house and its lord.

    This function does not generate user-facing predictions.
    It creates structured reasoning evidence that can later be
    consumed by the prediction/synthesis layer.
    """

    houses = chart.get("houses", {})
    planets = chart.get("planets", {})

    seventh_house = houses.get("7")

    if not seventh_house:
        return {
            "available": False,
            "reason": "7th house data is unavailable.",
        }

    seventh_sign = seventh_house.get("sign")
    seventh_lord = seventh_house.get("lord")

    lord_data = planets.get(seventh_lord, {}) if seventh_lord else {}

    lord_house = lord_data.get("house")
    lord_sign = lord_data.get("sign")
    lord_nakshatra = lord_data.get("nakshatra")

    analysis: dict[str, Any] = {
        "available": True,
        "seventh_house": {
            "house": 7,
            "sign": seventh_sign,
            "lord": seventh_lord,
        },
        "seventh_lord": {
            "planet": seventh_lord,
            "house": lord_house,
            "sign": lord_sign,
            "nakshatra": lord_nakshatra,
        },
        "sign_attributes": {
            "element": SIGN_ELEMENTS.get(seventh_sign),
            "modality": SIGN_MODALITIES.get(seventh_sign),
        },
        "indicators": [],
    }

    indicators = analysis["indicators"]

    # Fixed signs generally indicate greater stability and
    # resistance to sudden change in relationship matters.
    if SIGN_MODALITIES.get(seventh_sign) == "fixed":
        indicators.append(
            {
                "factor": "seventh_house_modality",
                "value": "fixed",
                "interpretation": (
                    "The spouse/relationship pattern may favour "
                    "stability, loyalty and persistence."
                ),
                "strength": 0.6,
            }
        )

    # Movable signs can indicate movement, change or relocation.
    elif SIGN_MODALITIES.get(seventh_sign) == "movable":
        indicators.append(
            {
                "factor": "seventh_house_modality",
                "value": "movable",
                "interpretation": (
                    "The relationship pattern may involve movement, "
                    "change or an active lifestyle."
                ),
                "strength": 0.5,
            }
        )

    # Dual signs can indicate flexibility or more than one phase
    # in relationship development.
    elif SIGN_MODALITIES.get(seventh_sign) == "dual":
        indicators.append(
            {
                "factor": "seventh_house_modality",
                "value": "dual",
                "interpretation": (
                    "The relationship pattern may involve flexibility, "
                    "adaptation or multiple phases before settling."
                ),
                "strength": 0.5,
            }
        )

    # Water signs tend to emphasise emotional depth and sensitivity.
    if SIGN_ELEMENTS.get(seventh_sign) == "water":
        indicators.append(
            {
                "factor": "seventh_house_element",
                "value": "water",
                "interpretation": (
                    "Emotional depth, sensitivity and privacy may "
                    "be important in the spouse/relationship dynamic."
                ),
                "strength": 0.6,
            }
        )

    # Air signs emphasise communication and social interaction.
    elif SIGN_ELEMENTS.get(seventh_sign) == "air":
        indicators.append(
            {
                "factor": "seventh_house_element",
                "value": "air",
                "interpretation": (
                    "Communication, intellectual compatibility and "
                    "social interaction may be important."
                ),
                "strength": 0.6,
            }
        )

    # Fire signs emphasise initiative and independence.
    elif SIGN_ELEMENTS.get(seventh_sign) == "fire":
        indicators.append(
            {
                "factor": "seventh_house_element",
                "value": "fire",
                "interpretation": (
                    "Initiative, confidence and independence may "
                    "be important in the spouse/relationship dynamic."
                ),
                "strength": 0.6,
            }
        )

    # Earth signs emphasise practicality and stability.
    elif SIGN_ELEMENTS.get(seventh_sign) == "earth":
        indicators.append(
            {
                "factor": "seventh_house_element",
                "value": "earth",
                "interpretation": (
                    "Practicality, stability and material responsibility "
                    "may be important in the relationship."
                ),
                "strength": 0.6,
            }
        )

    # 7th lord placement is one of the primary marriage indicators.
    if lord_house is not None:
        indicators.append(
            {
                "factor": "seventh_lord_house",
                "value": lord_house,
                "interpretation": (
                    f"The 7th lord is placed in the {lord_house}th house. "
                    "This house becomes an important area through which "
                    "relationship and spouse-related matters may manifest."
                ),
                "strength": 1.0,
            }
        )

    if lord_sign:
        indicators.append(
            {
                "factor": "seventh_lord_sign",
                "value": lord_sign,
                "interpretation": (
                    f"The 7th lord is placed in {lord_sign}, adding "
                    "the qualities of that sign to spouse/relationship matters."
                ),
                "strength": 0.7,
            }
        )

    return analysis