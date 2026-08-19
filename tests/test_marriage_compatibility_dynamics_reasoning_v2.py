import pytest

from app.astrology.features.marriage_compatibility_dynamics_reasoning_v2 import (
    analyze_marriage_compatibility_dynamics_v2,
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


def test_v2_general_contract():
    result = analyze_marriage_compatibility_dynamics_v2(
        _chart(),
        "What kind of compatibility dynamics are indicated in marriage?",
    )
    assert result["available"] is True
    assert result["event"] == "marriage_compatibility_dynamics"
    assert result["model_version"] == "v2"
    assert result["target"] == "general"
    assert 0.0 <= result["support_score"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["answer"]
    assert result["evidence_count"] == len(result["evidence"])


@pytest.mark.parametrize(
    "question,target",
    [
        ("Will we be emotionally compatible?", "emotional_attunement"),
        ("Will we communicate well with each other?", "communication_flow"),
        ("Are shared values likely to be important?", "shared_values"),
        ("Is there strong chemistry and attraction?", "chemistry"),
        ("Does the chart support a stable long-term marriage?", "stability"),
        ("Will either partner need a lot of personal freedom or space?", "independence"),
        ("Are there compatibility issues or adjustment pressure?", "friction"),
    ],
)
def test_v2_target_detection(question, target):
    result = analyze_marriage_compatibility_dynamics_v2(_chart(), question)
    assert result["target"] == target


def test_v2_target_support_is_bounded():
    result = analyze_marriage_compatibility_dynamics_v2(
        _chart(seventh_lord="Mercury", occupants=["Mercury"]),
        "Will we communicate well?",
    )
    assert result["target"] == "communication_flow"
    assert 0.0 <= result["support_score"] <= 1.0
    assert result["analysis"]["requested_dimensions"] == ["communication_flow"]


def test_v2_preserves_one_chart_limitation():
    result = analyze_marriage_compatibility_dynamics_v2(
        _chart(),
        "Are we compatible?",
    )
    limitation = result["limitation"].lower()
    assert "one natal chart" in limitation
    assert "synastry" in limitation
    assert "real-world" in limitation


def test_v2_missing_chart_data_is_unavailable():
    result = analyze_marriage_compatibility_dynamics_v2(
        {"houses": {}, "planets": {}},
        "Will we communicate well?",
    )
    assert result["available"] is False
    assert result["event"] == "marriage_compatibility_dynamics"
    assert result["model_version"] == "v2"


def test_v2_rejects_empty_question():
    with pytest.raises(ValueError):
        analyze_marriage_compatibility_dynamics_v2(_chart(), "   ")


def test_v2_rejects_non_string_question():
    with pytest.raises(ValueError):
        analyze_marriage_compatibility_dynamics_v2(_chart(), None)
