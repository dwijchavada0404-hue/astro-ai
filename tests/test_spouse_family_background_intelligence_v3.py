from app.astrology.features.marriage_question_intelligence_v3 import (
    analyze_marriage_question_v3,
)


def test_family_background_detection():
    questions = [
        "What kind of family background will my spouse have?",
        "Will my spouse come from a traditional family?",
        "Will my spouse come from an educated family?",
        "Will my spouse come from a business family?",
        "Will my spouse come from a professional family?",
        "Will my spouse come from a multicultural family?",
        "Will my spouse come from a creative family?",
    ]
    for question in questions:
        result = analyze_marriage_question_v3(question)
        assert result["primary_event"] == "spouse_family_background"
        assert result["query_mode"] == "single_event"
        assert result["intent"]["direction"] == "neutral"


def test_family_background_probability_question_type():
    result = analyze_marriage_question_v3(
        "Will my spouse come from a traditional family?"
    )
    assert result["intent"]["question_type"] == "probability"


def test_wealthy_family_remains_spouse_wealth():
    result = analyze_marriage_question_v3(
        "Will my spouse come from a wealthy family?"
    )
    assert result["primary_event"] == "spouse_wealth"


def test_profession_question_not_hijacked():
    result = analyze_marriage_question_v3(
        "Will my spouse work in a corporate job?"
    )
    assert result["primary_event"] == "spouse_profession"


def test_foreign_origin_question_not_hijacked():
    result = analyze_marriage_question_v3(
        "Will my spouse be from another country?"
    )
    assert result["primary_event"] == "foreign_intercultural_connection"
