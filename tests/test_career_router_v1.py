from datetime import datetime, timezone

from app.astrology.features.career_router_v1 import route_career_question_v1
from tests.test_career_synthesis_v1 import _chart


def _now():
    return datetime(2026, 8, 20, tzinfo=timezone.utc)


def test_promotion_question_routes_to_event_intelligence():
    result = route_career_question_v1(_chart(), "When will I get promoted?", _now())
    assert result["available"] is True
    assert result["route"] == "career_event_v1"
    assert result["event_key"] == "promotion"
    assert result["event_result"] is not None


def test_new_job_question_keeps_new_job_event_separate():
    result = route_career_question_v1(_chart(), "When will I get a new job?", _now())
    assert result["route"] == "career_event_v1"
    assert result["event_key"] == "new_job"


def test_job_business_question_routes_to_orientation_engine():
    result = route_career_question_v1(_chart(), "Should I do a job or business?", _now())
    assert result["route"] == "career_job_vs_business_v1"
    assert result["job_vs_business"]["orientation"] in {
        "structured_employment", "independent_business", "mixed_hybrid"
    }


def test_direction_question_routes_to_direction_engine():
    result = route_career_question_v1(_chart(), "Which career suits me best?", _now())
    assert result["route"] == "career_direction_v1"
    assert result["direction"]["primary_direction"] is not None


def test_overall_progress_question_routes_to_synthesis():
    result = route_career_question_v1(_chart(), "How will my career progress in the future?", _now())
    assert result["route"] == "career_synthesis_v1"
    assert result["synthesis"]["event"] == "career_synthesis"
    assert result["synthesis"]["historical_validation"]["status"] == "unconfirmed"


def test_generic_timing_question_routes_to_timing_engine():
    result = route_career_question_v1(_chart(), "When is my strongest career period?", _now())
    assert result["route"] == "career_timing_v1"
    assert result["timing"]["available"] is True


def test_job_loss_question_is_challenge_not_termination_prediction():
    result = route_career_question_v1(_chart(), "Will I lose my job?", _now())
    assert result["route"] == "career_event_v1"
    assert result["event_key"] == "job_loss_challenge"
    assert "must not be presented as a prediction of termination" in result["limitation"].lower()


def test_unrelated_question_is_declined():
    result = route_career_question_v1(_chart(), "When will I get married?", _now())
    assert result["available"] is False
    assert result["route"] == "unsupported"
