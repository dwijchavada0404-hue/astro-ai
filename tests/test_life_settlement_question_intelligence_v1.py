from app.astrology.features.life_settlement_question_intelligence_v1 import analyze_life_settlement_question_v1


def test_settlement_timing_question():
    result = analyze_life_settlement_question_v1("When will I be settled in life?")
    assert result["available"] is True
    assert result["primary_intent"] == "settlement_timing"
    assert result["requires_timing_engine"] is True


def test_settlement_age_question():
    result = analyze_life_settlement_question_v1("At what age will I settle in life?")
    assert result["available"] is True
    assert result["primary_intent"] == "settlement_age"


def test_target_age_is_extracted():
    result = analyze_life_settlement_question_v1("What will my life look like at 30?")
    assert result["primary_intent"] == "target_age_outlook"
    assert result["target_age"] == 30


def test_overview_question():
    result = analyze_life_settlement_question_v1("When will everything fall into place?")
    assert result["available"] is True
    assert result["requires_cross_domain_synthesis"] is True


def test_unrelated_question_is_unknown():
    result = analyze_life_settlement_question_v1("What colour should I paint my desk?")
    assert result["available"] is False
    assert result["primary_intent"] == "unknown"


def test_safety_boundaries_are_explicit():
    result = analyze_life_settlement_question_v1("When will I be settled?")
    assert result["safety"]["guaranteed_settlement_date_allowed"] is False
    assert result["safety"]["single_domain_equals_settlement_allowed"] is False
    assert result["safety"]["known_reality_override_required"] is True
