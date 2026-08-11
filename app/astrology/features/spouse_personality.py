from typing import Any

SIGN_PERSONALITY = {
    "Aries": ["independent", "energetic", "confisident"],
    "Taurus": ["stable", "practical", "patient"],
    "Gemini": ["communicative", "curious", "social"],
    "Cancer": ["caring", "emotional", "family-oriented"],
    "Leo": ["confident", "charismatic", "creative"],
    "Virgo": ["analytical", "organized", "helpful"],
    "Libra": ["charming", "balanced", "diplomatic"],
    "Scorpio": ["intense", "loyal", "private"],
    "Sagittarius": ["adventurous", "optimistic", "free-spirited"],
    "Capricorn": ["mature", "responsible", "disciplined"],
    "Aquarius": ["independent", "innovative", "intellectual"],
    "Pisces": ["compassionate", "creative", "sensitive"],
}


def analyze_spouse_personality(chart: dict[str, Any]) -> dict[str, Any]:
    """
    Determine spouse personality primarily from the
    sign occupying the 7th house.
    """

    seventh = chart.get("houses", {}).get("7")

    if not seventh:
        return {}

    sign = seventh.get("sign")

    return {
        "sign": sign,
        "traits": SIGN_PERSONALITY.get(sign, []),
        "confidence": 0.70,
        "rule": "7th_house_sign_personality",
    }