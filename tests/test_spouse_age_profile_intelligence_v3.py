from app.astrology.features.marriage_question_intelligence_v3 import (
    analyze_marriage_question_v3,
)


def test_spouse_age_profile_detection():
    questions = [
        "Will my spouse be older than me?",
        "Will my spouse be younger than me?",
        "Will my spouse be around my age?",
        "What age profile will my future spouse have?",
        "Will my spouse be more mature than me?",
    ]
    for question in questions:
        result = analyze_marriage_question_v3(question)
        assert result["primary_event"] == "spouse_age_profile"
        assert result["query_mode"] == "single_event"
        assert result["intent"]["direction"] == "neutral"


def test_spouse_age_probability_question_type():
    result = analyze_marriage_question_v3("Will my spouse be older than me?")
    assert result["intent"]["question_type"] == "probability"


def test_spouse_age_general_question_type():
    result = analyze_marriage_question_v3("What age profile will my future spouse have?")
    assert result["intent"]["question_type"] == "general_outlook"


def test_age_profile_does_not_hijack_spouse_traits():
    result = analyze_marriage_question_v3("What kind of person will I marry?")
    assert result["primary_event"] == "spouse_traits"


def test_age_profile_does_not_hijack_marriage_timing():
    result = analyze_marriage_question_v3("At what age will I get married?")
    assert result["primary_event"] == "marriage_timing"
