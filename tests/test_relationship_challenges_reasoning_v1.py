import pytest

from app.astrology.features.relationship_challenges_reasoning_v1 import (
    analyze_relationship_challenges_v1,
)


def _chart(seventh_lord="Mars", occupants=None):
    occupants = occupants or []
    planets = {
        "Mars": {"house": 3, "sign": "Aries"},
        "Saturn": {"house": 10, "sign": "Capricorn"},
        "Rahu": {"house": 11, "sign": "Aquarius"},
        "Ketu": {"house": 5, "sign": "Leo"},
        "Venus": {"house": 6, "sign": "Taurus"},
        "Jupiter": {"house": 9, "sign": "Sagittarius"},
        "Moon": {"house": 4, "sign": "Cancer"},
    }
    for planet in occupants:
        planets.setdefault(planet, {"sign": "Libra"})
        planets[planet]["house"] = 7
    return {
        "houses": {"7": {"sign": "Libra", "lord": seventh_lord}},
        "planets": planets,
    }


def test_basic_contract():
    result = analyze_relationship_challenges_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "relationship_challenges"
    assert result["model_version"] == "v1"
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["evidence"]
    assert result["limitation"]


def test_mars_supports_conflict_intensity():
    result = analyze_relationship_challenges_v1(_chart(seventh_lord="Mars", occupants=["Mars"]))
    assert result["profile"]["profile_scores"].get("conflict_intensity", 0) > 0


def test_saturn_supports_distance_and_delay():
    result = analyze_relationship_challenges_v1(_chart(seventh_lord="Saturn", occupants=["Saturn"]))
    scores = result["profile"]["profile_scores"]
    assert scores.get("emotional_distance", 0) > 0
    assert scores.get("delay_pressure", 0) > 0


def test_rahu_supports_instability():
    result = analyze_relationship_challenges_v1(_chart(seventh_lord="Rahu", occupants=["Rahu"]))
    assert result["profile"]["profile_scores"].get("instability", 0) > 0


def test_benefics_support_repair_capacity():
    result = analyze_relationship_challenges_v1(_chart(seventh_lord="Venus", occupants=["Venus"]))
    assert result["profile"]["profile_scores"].get("repair_capacity", 0) > 0


def test_missing_seventh_house_is_unavailable():
    result = analyze_relationship_challenges_v1({"houses": {}, "planets": {}})
    assert result["available"] is False
    assert result["event"] == "relationship_challenges"


def test_non_dict_chart_rejected():
    with pytest.raises(ValueError):
        analyze_relationship_challenges_v1([])
