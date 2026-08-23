import pytest

from app.astrology.features.health_wellbeing_reasoning_v1 import analyze_health_wellbeing_v1


def _chart():
    return {
        "houses": {
            "1": {"lord": "Sun"},
            "6": {"lord": "Saturn"},
            "8": {"lord": "Mars"},
            "12": {"lord": "Jupiter"},
        },
        "planets": {
            "Sun": {"house": 1},
            "Moon": {"house": 5},
            "Mars": {"house": 3},
            "Saturn": {"house": 6},
            "Jupiter": {"house": 9},
            "Mercury": {"house": 10},
            "Venus": {"house": 12},
        },
    }


def test_health_wellbeing_scores_are_bounded():
    result = analyze_health_wellbeing_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "health_wellbeing"
    assert all(0.0 <= value <= 1.0 for value in result["theme_scores"].values())
    assert 0.0 <= result["confidence"] <= 1.0


def test_health_wellbeing_has_ranked_evidence_backed_themes():
    result = analyze_health_wellbeing_v1(_chart())
    assert result["dominant_theme"] in result["theme_scores"]
    assert result["secondary_theme"] in result["theme_scores"]
    assert len(result["ranked_themes"]) == 6
    assert result["evidence"]


def test_medical_reality_overrides_astrology():
    result = analyze_health_wellbeing_v1(_chart())
    rule = result["known_reality_rule"].lower()
    assert "medical history" in rule
    assert "clinician advice" in rule
    assert "override" in rule


def test_medical_safety_boundaries_are_explicit():
    result = analyze_health_wellbeing_v1(_chart())
    limitation = result["limitation"].lower()
    assert "not medical advice" in limitation
    assert "diagnose" in limitation
    assert "lifespan" in limitation and "death" in limitation
    assert "medication" in limitation and "treatment" in limitation
    assert all(value is False for value in result["safety"].values())


def test_missing_houses_returns_unavailable():
    result = analyze_health_wellbeing_v1({"planets": {}})
    assert result["available"] is False
    assert "house data" in result["reason"].lower()


def test_non_dict_chart_is_rejected():
    with pytest.raises(ValueError, match="dictionary"):
        analyze_health_wellbeing_v1([])
