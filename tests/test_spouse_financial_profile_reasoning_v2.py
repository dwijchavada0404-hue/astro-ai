import pytest

from app.astrology.features.spouse_financial_profile_reasoning_v2 import (
    analyze_spouse_financial_profile_v2,
)


def _chart(seventh_lord="Jupiter", eighth_lord="Venus"):
    return {
        "houses": {
            "7": {"sign": "Pisces", "lord": seventh_lord},
            "8": {"sign": "Aries", "lord": eighth_lord},
        },
        "planets": {
            "Jupiter": {"house": 7, "sign": "Pisces"},
            "Venus": {"house": 8, "sign": "Aries"},
            "Mercury": {"house": 10, "sign": "Gemini"},
            "Saturn": {"house": 11, "sign": "Aquarius"},
            "Mars": {"house": 3, "sign": "Scorpio"},
            "Rahu": {"house": 6, "sign": "Aquarius"},
        },
    }


def test_v2_general_contract():
    result = analyze_spouse_financial_profile_v2(_chart(), "Describe my future spouse's financial profile.")
    assert result["available"] is True
    assert result["event"] == "spouse_financial_profile"
    assert result["model_version"] == "v2"
    assert result["target"] == "general"
    assert 0 <= result["support_score"] <= 1
    assert result["answer"]
    assert result["evidence_count"] == len(result["evidence"])


def test_v2_detects_rich_target():
    result = analyze_spouse_financial_profile_v2(_chart(), "Will my spouse be rich?")
    assert result["target"] == "affluent"
    assert "rich" in result["matched_keywords"]


def test_v2_detects_stability_target():
    result = analyze_spouse_financial_profile_v2(_chart(seventh_lord="Saturn"), "Will my spouse be financially stable?")
    assert result["target"] == "stable"


def test_v2_detects_entrepreneurial_target():
    result = analyze_spouse_financial_profile_v2(_chart(seventh_lord="Mercury"), "Could my spouse be an entrepreneur?")
    assert result["target"] == "entrepreneurial"


def test_v2_detects_variable_target():
    result = analyze_spouse_financial_profile_v2(_chart(seventh_lord="Rahu"), "Could my spouse have variable income?")
    assert result["target"] == "variable"


def test_v2_preserves_financial_limitation():
    result = analyze_spouse_financial_profile_v2(_chart(), "What will my spouse's net worth be?")
    limitation = result["limitation"].lower()
    assert "exact salary" in limitation
    assert "net worth" in limitation
    assert "guaranteed" in limitation


def test_v2_missing_chart_data_is_unavailable():
    result = analyze_spouse_financial_profile_v2({"houses": {}, "planets": {}}, "Will my spouse be wealthy?")
    assert result["available"] is False
    assert result["event"] == "spouse_financial_profile"


def test_v2_rejects_empty_question():
    with pytest.raises(ValueError):
        analyze_spouse_financial_profile_v2(_chart(), "   ")
