import pytest

from app.astrology.features.career_profession_reasoning_v1 import analyze_career_profession_v1


def _chart():
    return {
        "houses": {
            "1": {"lord": "Mars"},
            "2": {"lord": "Venus"},
            "3": {"lord": "Mercury"},
            "5": {"lord": "Mercury"},
            "6": {"lord": "Saturn"},
            "7": {"lord": "Venus"},
            "9": {"lord": "Jupiter"},
            "10": {"lord": "Saturn"},
            "11": {"lord": "Jupiter"},
        },
        "planets": {
            "Mars": {"house": 3},
            "Venus": {"house": 7},
            "Mercury": {"house": 10},
            "Saturn": {"house": 10},
            "Jupiter": {"house": 11},
            "Sun": {"house": 9},
        },
    }


def test_career_foundation_returns_ranked_themes():
    result = analyze_career_profession_v1(_chart())
    assert result["available"] is True
    assert result["event"] == "career_profession"
    assert result["dominant_theme"] in result["theme_scores"]
    assert len(result["ranked_themes"]) == 6
    assert 0.0 <= result["dominant_score"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0


def test_tenth_house_has_material_career_weight():
    result = analyze_career_profession_v1(_chart())
    assert result["theme_scores"]["career_strength"] >= 0.4


def test_service_and_enterprise_can_coexist():
    result = analyze_career_profession_v1(_chart())
    assert result["theme_scores"]["service_employment"] > 0
    assert result["theme_scores"]["independent_enterprise"] > 0


def test_evidence_and_safety_limitation_are_exposed():
    result = analyze_career_profession_v1(_chart())
    assert result["evidence"]
    limitation = result["limitation"].lower()
    assert "does not guarantee" in limitation
    assert "promotion" in limitation


def test_missing_house_data_is_unavailable():
    result = analyze_career_profession_v1({"houses": {}, "planets": {}})
    assert result["available"] is False


def test_invalid_chart_rejected():
    with pytest.raises(ValueError):
        analyze_career_profession_v1([])  # type: ignore[arg-type]
