from app.astrology.features.property_home_question_intelligence_v1 import analyze_property_home_question_v1


def test_acquisition_question_detected():
    result = analyze_property_home_question_v1("Will I buy a house?")
    assert result["available"] is True
    assert result["primary_intent"] == "property_acquisition"
    assert result["timing_requested"] is False


def test_relocation_question_detected():
    result = analyze_property_home_question_v1("When will I relocate?")
    assert result["primary_intent"] == "relocation"
    assert result["timing_requested"] is True


def test_inheritance_question_detected():
    result = analyze_property_home_question_v1("Is ancestral property indicated?")
    assert result["primary_intent"] == "inheritance_family_property"


def test_overview_question_detected():
    result = analyze_property_home_question_v1("Tell me about my property future")
    assert result["primary_intent"] == "property_overview"


def test_unrelated_question_is_declined():
    result = analyze_property_home_question_v1("When will I get promoted?")
    assert result["available"] is False
    assert result["primary_intent"] == "unknown"


def test_safety_flags_disallow_fact_inference_and_advice():
    result = analyze_property_home_question_v1("Will I own a house?")
    safety = result["safety"]
    assert safety["ownership_fact_inference_allowed"] is False
    assert safety["guaranteed_transaction_language_allowed"] is False
    assert safety["financial_or_legal_advice_allowed"] is False
