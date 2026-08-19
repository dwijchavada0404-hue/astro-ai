import pytest

from app.astrology.features.marriage_compatibility_dynamics_reasoning_v1 import (
    analyze_marriage_compatibility_dynamics_v1,
)


def _chart(seventh_lord="Venus", occupants=None):
    occupants = occupants or []
    planets = {
        "Moon": {"house": 4, "sign": "Cancer"},
        "Mercury": {"house": 6, "sign": "Virgo"},
        "Venus": {"house": 1, "sign": "Aries"},
        "Jupiter": {"house": 9, "sign": "Sagittarius"},
        "Saturn": {"house": 10, "sign": "Capricorn"},
        "Mars": {"house": 3, "sign": "Scorpio"},
        "Sun": {"house": 5, "sign": "Leo"},
        "Rahu": {"house": 11, "sign": "Aquarius"},
        "Ketu": {"house": 5, "sign": "Leo"},
    }
    for planet in occupants:
        planets.setdefault(planet, {"sign": "Libra"})
        planets[planet]["house"] = 7
    return {
        "houses": {"7": {"sign": "Libra", "lord": seventh_lord}},
        "planets": planets,
    }


def test_basic_contract():
    result = analyze_marriage_compatibility_dynamics_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "marriage_compatibility_dynamics"
    assert result["model_version"] == "v1"
    assert 0 <= result["confidence"] <= 1
    assert result["dominant_dimension"]
    assert result["ranked_dimensions"]
    assert result["evidence"]


def test_venus_supports_chemistry():
    result = analyze_marriage_compatibility_dynamics_v1(_chart(seventh_lord="Venus"))
    assert result["profile"]["dimension_scores"].get("chemistry", 0) > 0


def test_moon_supports_emotional_attunement():
    result = analyze_marriage_compatibility_dynamics_v1(_chart(seventh_lord="Moon", occupants=["Moon"]))
    assert result["profile"]["dimension_scores"].get("emotional_attunement", 0) > 0


def test_mercury_supports_communication():
    result = analyze_marriage_compatibility_dynamics_v1(_chart(seventh_lord="Mercury", occupants=["Mercury"]))
    assert result["profile"]["dimension_scores"].get("communication_flow", 0) > 0


def test_saturn_supports_stability():
    result = analyze_marriage_compatibility_dynamics_v1(_chart(seventh_lord="Saturn", occupants=["Saturn"]))
    assert result["profile"]["dimension_scores"].get("stability", 0) > 0


def test_mars_can_add_friction():
    result = analyze_marriage_compatibility_dynamics_v1(_chart(seventh_lord="Mars", occupants=["Mars"]))
    assert result["profile"]["dimension_scores"].get("friction", 0) > 0


def test_missing_seventh_house_is_unavailable():
    result = analyze_marriage_compatibility_dynamics_v1({"houses": {}, "planets": {}})
    assert result["available"] is False


def test_non_dict_chart_rejected():
    with pytest.raises(ValueError):
        analyze_marriage_compatibility_dynamics_v1([])
