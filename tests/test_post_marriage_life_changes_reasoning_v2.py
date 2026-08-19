import pytest

from app.astrology.features.post_marriage_life_changes_reasoning_v2 import (
    analyze_post_marriage_life_changes_v2,
)


def _chart(seventh_lord="Jupiter", seventh_lord_house=12):
    return {
        "houses": {
            "7": {"sign": "Pisces", "lord": seventh_lord},
            "4": {"lord": "Venus"},
            "8": {"lord": "Mars"},
            "10": {"lord": "Mercury"},
            "11": {"lord": "Saturn"},
            "12": {"lord": "Moon"},
        },
        "planets": {
            seventh_lord: {"house": seventh_lord_house},
            "Venus": {"house": 7},
            "Mars": {"house": 7},
            "Mercury": {"house": 7},
            "Saturn": {"house": 7},
            "Moon": {"house": 9},
            "Rahu": {"house": 9},
        },
    }


def test_v2_general_contract():
    result = analyze_post_marriage_life_changes_v2(_chart(), "How could my life change after marriage?")
    assert result["available"] is True
    assert result["event"] == "post_marriage_life_changes"
    assert result["model_version"] == "v2"
    assert result["target"] == "general"
    assert result["answer"]
    assert result["evidence_count"] == len(result["evidence"])


def test_v2_detects_relocation():
    result = analyze_post_marriage_life_changes_v2(_chart(), "Will I relocate after marriage?")
    assert result["target"] == "relocation"


def test_v2_detects_international_exposure():
    result = analyze_post_marriage_life_changes_v2(_chart(), "Could I move abroad after marriage?")
    assert result["target"] == "international_exposure"


def test_v2_detects_career_shift():
    result = analyze_post_marriage_life_changes_v2(_chart(seventh_lord_house=10), "Will there be a career change after marriage?")
    assert result["target"] == "career_shift"


def test_v2_detects_financial_change():
    result = analyze_post_marriage_life_changes_v2(_chart(seventh_lord_house=11), "Will my finances change after marriage?")
    assert result["target"] == "financial_change"


def test_v2_detects_family_responsibility():
    result = analyze_post_marriage_life_changes_v2(_chart(seventh_lord_house=4), "Will my family responsibilities increase after marriage?")
    assert result["target"] == "family_responsibility"


def test_v2_detects_lifestyle_change():
    result = analyze_post_marriage_life_changes_v2(_chart(seventh_lord_house=4), "Will my lifestyle change after marriage?")
    assert result["target"] == "lifestyle_change"


def test_v2_preserves_non_guarantee_limitation():
    result = analyze_post_marriage_life_changes_v2(_chart(), "Will I definitely move abroad after marriage?")
    limitation = result["limitation"].lower()
    assert "cannot guarantee" in limitation
    assert "timeline" in limitation


def test_v2_unavailable_chart():
    result = analyze_post_marriage_life_changes_v2({"houses": {}, "planets": {}}, "Will I relocate after marriage?")
    assert result["available"] is False


def test_v2_rejects_empty_question():
    with pytest.raises(ValueError):
        analyze_post_marriage_life_changes_v2(_chart(), "   ")
