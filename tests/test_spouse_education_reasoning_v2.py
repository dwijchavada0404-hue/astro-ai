from __future__ import annotations

from typing import Any

import pytest

from app.astrology.features.spouse_education_reasoning_v2 import (
    analyze_spouse_education_v2,
)


def _reference_chart() -> dict[str, Any]:
    return {
        "houses": {
            "1": {"sign": "Cancer", "lord": "Moon"},
            "2": {"sign": "Leo", "lord": "Sun"},
            "3": {"sign": "Virgo", "lord": "Mercury"},
            "4": {"sign": "Libra", "lord": "Venus"},
            "5": {"sign": "Scorpio", "lord": "Mars"},
            "6": {"sign": "Sagittarius", "lord": "Jupiter"},
            "7": {"sign": "Capricorn", "lord": "Saturn"},
            "8": {"sign": "Aquarius", "lord": "Saturn"},
            "9": {"sign": "Pisces", "lord": "Jupiter"},
            "10": {"sign": "Aries", "lord": "Mars"},
            "11": {"sign": "Taurus", "lord": "Venus"},
            "12": {"sign": "Gemini", "lord": "Mercury"},
        },
        "planets": {
            "Sun": {"house": 9, "sign": "Pisces"},
            "Moon": {"house": 9, "sign": "Pisces"},
            "Mars": {"house": 10, "sign": "Aries"},
            "Mercury": {"house": 3, "sign": "Virgo"},
            "Jupiter": {"house": 10, "sign": "Aries"},
            "Venus": {"house": 11, "sign": "Taurus"},
            "Saturn": {"house": 10, "sign": "Aries"},
            "Rahu": {"house": 12, "sign": "Gemini"},
            "Ketu": {"house": 6, "sign": "Sagittarius"},
        },
    }


def test_spouse_education_v2_basic_contract():
    result = analyze_spouse_education_v2(
        _reference_chart(),
        "What kind of education will my future spouse have?",
    )
    assert result["available"] is True
    assert result["event"] == "spouse_education"
    assert result["model_version"] == "v2"
    assert result["target"] == "general"
    assert result["answer"]
    assert result["summary"] == result["answer"]


@pytest.mark.parametrize(
    ("question", "target"),
    [
        ("Will my spouse be highly educated?", "higher_education"),
        ("Will my spouse have a professional qualification?", "professional_qualification"),
        ("Will my spouse be intelligent and analytical?", "analytical_intellect"),
        ("Could my spouse be an engineer?", "technical_education"),
        ("Will my spouse have a finance degree?", "finance_commerce"),
        ("Could my spouse have a law degree?", "law_advisory"),
        ("Will my spouse study design?", "creative_education"),
        ("Will my spouse be educated abroad?", "international_education"),
        ("Could my spouse have a research degree?", "research_specialisation"),
    ],
)
def test_spouse_education_v2_target_detection(question: str, target: str):
    result = analyze_spouse_education_v2(_reference_chart(), question)
    assert result["target"] == target


def test_spouse_education_v2_general_profile_propagation():
    result = analyze_spouse_education_v2(
        _reference_chart(),
        "Describe my spouse's education and intellect.",
    )
    assert result["target"] == "general"
    assert result["natal_profile"]["education_themes"]
    assert result["natal_analysis"]["model_version"] == "v1"


@pytest.mark.parametrize(
    "question",
    [
        "Will my spouse be highly educated?",
        "Will my spouse have a professional qualification?",
        "Could my spouse be an engineer?",
        "Will my spouse have a finance degree?",
        "Could my spouse have a law degree?",
        "Will my spouse be educated abroad?",
        "Could my spouse have a research degree?",
    ],
)
def test_spouse_education_v2_support_score_is_bounded(question: str):
    result = analyze_spouse_education_v2(_reference_chart(), question)
    assert 0.0 <= result["support_score"] <= 0.92
    assert result["support_level"] in {
        "strong_support",
        "moderate_support",
        "mild_support",
        "limited_support",
    }


def test_spouse_education_v2_confidence_is_bounded():
    result = analyze_spouse_education_v2(
        _reference_chart(),
        "What kind of education will my spouse have?",
    )
    assert 0.50 <= result["confidence"] <= 0.90


def test_spouse_education_v2_higher_education_limitation():
    result = analyze_spouse_education_v2(
        _reference_chart(),
        "Will my spouse be highly educated?",
    )
    assert "exact degree" in result["limitation"].lower()


def test_spouse_education_v2_international_limitation():
    result = analyze_spouse_education_v2(
        _reference_chart(),
        "Will my spouse be educated abroad?",
    )
    assert "international" in result["limitation"].lower()


def test_spouse_education_v2_preserves_question_metadata():
    question = "Will my spouse have a finance degree?"
    result = analyze_spouse_education_v2(_reference_chart(), question)
    assert result["question"] == question
    assert result["normalised_question"] == question.lower()
    assert "finance degree" in result["matched_keywords"]


def test_spouse_education_v2_evidence_contract():
    result = analyze_spouse_education_v2(
        _reference_chart(),
        "Could my spouse be an engineer?",
    )
    assert isinstance(result["evidence"], list)
    assert result["evidence_count"] == len(result["evidence"])
    if result["evidence"]:
        assert "theme" in result["evidence"][0]
        assert "relative_strength" in result["evidence"][0]


def test_spouse_education_v2_missing_seventh_house():
    result = analyze_spouse_education_v2(
        {"houses": {}, "planets": {}},
        "What kind of education will my spouse have?",
    )
    assert result["available"] is False
    assert result["event"] == "spouse_education"
    assert result["model_version"] == "v2"
    assert "reason" in result


def test_spouse_education_v2_rejects_non_dict_chart():
    with pytest.raises(ValueError, match="chart must be a dictionary"):
        analyze_spouse_education_v2([], "What education will my spouse have?")


def test_spouse_education_v2_rejects_non_string_question():
    with pytest.raises(ValueError, match="question must be a string"):
        analyze_spouse_education_v2(_reference_chart(), None)


def test_spouse_education_v2_rejects_empty_question():
    with pytest.raises(ValueError, match="question must not be empty"):
        analyze_spouse_education_v2(_reference_chart(), "   ")
