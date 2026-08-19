import pytest

from app.astrology.features.spouse_age_profile_reasoning_v2 import (
    analyze_spouse_age_profile_v2,
)


def _chart(seventh_lord="Saturn"):
    return {
        "houses": {"7": {"sign": "Libra", "lord": seventh_lord}},
        "planets": {
            "Saturn": {"house": 10, "sign": "Capricorn"},
            "Mercury": {"house": 3, "sign": "Gemini"},
            "Jupiter": {"house": 9, "sign": "Sagittarius"},
            "Venus": {"house": 2, "sign": "Taurus"},
        },
    }


@pytest.mark.parametrize(
    "question,target",
    [
        ("Will my spouse be older than me?", "older_spouse"),
        ("Could my spouse be younger than me?", "younger_spouse"),
        ("Will my spouse be around my age?", "similar_age_spouse"),
        ("What age profile does my future spouse show?", "general_age_profile"),
    ],
)
def test_v2_detects_age_target(question, target):
    result = analyze_spouse_age_profile_v2(_chart(), question)
    assert result["available"] is True
    assert result["event"] == "spouse_age_profile"
    assert result["target"] == target
    assert 0.0 <= result["support_score"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0


def test_older_question_scores_high_with_saturn_seventh_lord():
    result = analyze_spouse_age_profile_v2(_chart("Saturn"), "Will my spouse be older than me?")
    assert result["support_score"] >= 0.58


def test_exact_age_limitation_is_preserved():
    result = analyze_spouse_age_profile_v2(_chart(), "How old will my spouse be?")
    assert "exact age" in result["limitation"].lower()
