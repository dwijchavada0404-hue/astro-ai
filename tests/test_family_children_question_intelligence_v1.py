from app.astrology.features.family_children_question_intelligence_v1 import analyze_family_children_question_v1


def test_children_question_is_recognised_with_safety_guards():
    result = analyze_family_children_question_v1("When will I have children?")
    assert result["available"] is True
    assert result["primary_intent"] == "children_parenting"
    assert result["timing_requested"] is True
    assert result["safety"]["fertility_diagnosis_allowed"] is False
    assert result["safety"]["pregnancy_or_childbirth_prediction_allowed"] is False


def test_family_overview_is_recognised():
    result = analyze_family_children_question_v1("Tell me about my overall family future")
    assert result["primary_intent"] == "family_overview"


def test_family_support_question_is_recognised():
    result = analyze_family_children_question_v1("Will I get support from family and elders?")
    assert result["primary_intent"] == "family_support"


def test_unrelated_question_is_unknown():
    result = analyze_family_children_question_v1("Which career suits me best?")
    assert result["available"] is False
    assert result["primary_intent"] == "unknown"
