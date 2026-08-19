from app.astrology.features.spouse_age_profile_reasoning_v1 import (
    analyze_spouse_age_profile_v1,
)


def _chart(seventh_lord="Saturn", occupants=None):
    occupants = occupants or []
    planets = {
        "Saturn": {"house": 10, "sign": "Capricorn"},
        "Mercury": {"house": 3, "sign": "Gemini"},
        "Jupiter": {"house": 9, "sign": "Sagittarius"},
        "Venus": {"house": 2, "sign": "Taurus"},
    }
    for planet in occupants:
        planets.setdefault(planet, {})["house"] = 7
        planets[planet]["sign"] = "Libra"
    return {
        "houses": {
            "7": {"sign": "Libra", "lord": seventh_lord},
        },
        "planets": planets,
    }


def test_v1_returns_age_profile_contract():
    result = analyze_spouse_age_profile_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "spouse_age_profile"
    assert result["model_version"] == "v1"
    assert result["dominant_profile"] in {"older_mature", "similar_age", "younger_youthful", "mixed"}
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["evidence"]


def test_saturn_seventh_lord_supports_older_mature_pattern():
    result = analyze_spouse_age_profile_v1(_chart(seventh_lord="Saturn"))
    assert result["dominant_profile"] == "older_mature"


def test_mercury_seventh_lord_supports_younger_pattern():
    result = analyze_spouse_age_profile_v1(_chart(seventh_lord="Mercury"))
    assert result["dominant_profile"] == "younger_youthful"


def test_missing_seventh_house_is_unavailable():
    result = analyze_spouse_age_profile_v1({"houses": {}, "planets": {}})
    assert result["available"] is False
