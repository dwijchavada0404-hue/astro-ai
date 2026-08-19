from app.astrology.features.marriage_question_intelligence_v3 import analyze_marriage_question_v3


def test_married_life_quality_detection():
    result = analyze_marriage_question_v3("Will my marriage be harmonious?")
    assert result["primary_event"] == "married_life_quality"
    assert result["query_mode"] == "single_event"
    assert result["intent"]["event"] == "married_life_quality"
    assert result["intent"]["question_type"] in {"general_outlook", "probability"}


def test_marriage_stability_quality_detection():
    result = analyze_marriage_question_v3("Will my marriage be stable?")
    assert result["primary_event"] == "married_life_quality"


def test_general_married_life_detection():
    result = analyze_marriage_question_v3("How will my married life be?")
    assert result["primary_event"] == "married_life_quality"


def test_spouse_profile_not_hijacked():
    result = analyze_marriage_question_v3("What will my spouse profession be?")
    assert result["primary_event"] == "spouse_profession"
