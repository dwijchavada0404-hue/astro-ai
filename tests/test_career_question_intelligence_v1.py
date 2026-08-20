import pytest

from app.astrology.features.career_question_intelligence_v1 import analyze_career_question_v1


def test_promotion_with_timing_is_event_intent():
    result = analyze_career_question_v1("When will I get promoted?")
    assert result["available"] is True
    assert result["primary_intent"] == "promotion"
    assert result["timing_requested"] is True
    assert result["requires_event_engine"] is True


def test_job_business_is_distinct_intent():
    result = analyze_career_question_v1("Should I do a job or business?")
    assert result["primary_intent"] == "job_vs_business"


def test_career_direction_is_distinct_intent():
    result = analyze_career_question_v1("Which career suits me best?")
    assert result["primary_intent"] == "career_direction"


def test_new_job_is_not_generic_job_change():
    result = analyze_career_question_v1("When will I get a new job?")
    assert result["primary_intent"] == "new_job"
    assert result["timing_requested"] is True


def test_unrelated_question_is_unknown():
    result = analyze_career_question_v1("When will I get married?")
    assert result["available"] is False
    assert result["primary_intent"] == "unknown"


def test_safety_contract_disallows_deterministic_claims():
    safety = analyze_career_question_v1("Will I lose my job?")["safety"]
    assert safety["guaranteed_outcome_language_allowed"] is False
    assert safety["termination_prediction_allowed"] is False
    assert safety["historical_event_assumption_allowed"] is False


def test_empty_question_rejected():
    with pytest.raises(ValueError):
        analyze_career_question_v1("   ")
