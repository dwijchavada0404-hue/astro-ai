import pytest

from app.astrology.features.relationship_challenges_reasoning_v2 import (
    analyze_relationship_challenges_v2,
)


def _chart(seventh_lord="Mars", occupants=None):
    occupants = occupants or []
    planets = {
        "Mars": {"house": 3, "sign": "Aries"},
        "Saturn": {"house": 10, "sign": "Capricorn"},
        "Rahu": {"house": 11, "sign": "Aquarius"},
        "Ketu": {"house": 5, "sign": "Leo"},
        "Venus": {"house": 5, "sign": "Taurus"},
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


def test_v2_general_contract():
    result = analyze_relationship_challenges_v2(
        _chart(),
        "What challenges may I face in marriage?",
    )
    assert result["available"] is True
    assert result["event"] == "relationship_challenges"
    assert result["model_version"] == "v2"
    assert result["target"] == "general"
    assert 0.0 <= result["support_score"] <= 1.0
    assert result["answer"]
    assert result["evidence_count"] == len(result["evidence"])


@pytest.mark.parametrize(
    "question,target",
    [
        ("Will there be a lot of conflict in my marriage?", "conflict"),
        ("Could we become emotionally distant?", "distance"),
        ("Will my marriage be unstable?", "instability"),
        ("Is there delay in commitment?", "delay_pressure"),
        ("Can we reconcile after conflicts?", "repair"),
    ],
)
def test_v2_target_detection(question, target):
    result = analyze_relationship_challenges_v2(_chart(), question)
    assert result["target"] == target


def test_v2_preserves_safety_limitation():
    result = analyze_relationship_challenges_v2(
        _chart(),
        "Will I get divorced?",
    )
    limitation = result["limitation"].lower()
    assert "divorce" in limitation
    assert "abuse" in limitation
    assert "violence" in limitation
    assert "guaranteed" in limitation


def test_repair_target_has_bounded_support():
    result = analyze_relationship_challenges_v2(
        _chart(seventh_lord="Venus", occupants=["Jupiter"]),
        "Can we repair the relationship after conflict?",
    )
    assert result["target"] == "repair"
    assert 0.0 <= result["support_score"] <= 1.0


def test_v2_missing_chart_data_is_unavailable():
    result = analyze_relationship_challenges_v2(
        {"houses": {}, "planets": {}},
        "Will my marriage have conflict?",
    )
    assert result["available"] is False
    assert result["event"] == "relationship_challenges"


def test_v2_rejects_empty_question():
    with pytest.raises(ValueError):
        analyze_relationship_challenges_v2(_chart(), "   ")
