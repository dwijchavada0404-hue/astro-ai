from datetime import datetime, timezone

from app.astrology.features.education_learning_question_intelligence_v1 import analyze_education_learning_question_v1
from app.astrology.features.education_learning_router_v1 import route_education_learning_question_v1


NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"3": {"lord": "Mercury"}, "4": {"lord": "Moon"}, "5": {"lord": "Jupiter"}, "8": {"lord": "Saturn"}, "9": {"lord": "Mars"}},
        "planets": {"Mercury": {"house": 5}, "Moon": {"house": 4}, "Jupiter": {"house": 9}, "Saturn": {"house": 8}, "Mars": {"house": 3}, "Venus": {"house": 5}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Jupiter"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Moon"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Mars"},
        ],
    }


def test_question_intelligence_detects_event_and_timing():
    result = analyze_education_learning_question_v1("When is a strong period for my higher studies?")
    assert result["available"] is True
    assert result["primary_intent"] == "higher_study_transition"
    assert result["timing_requested"] is True
    assert result["safety"]["admission_guarantee_allowed"] is False


def test_router_routes_overview_to_synthesis():
    result = route_education_learning_question_v1(_chart(), "Give me an education overview", NOW)
    assert result["available"] is True
    assert result["route"] == "education_learning_synthesis_v1"


def test_router_routes_specific_event_without_guaranteeing_outcome():
    result = route_education_learning_question_v1(_chart(), "Will I clear my exam?", NOW)
    assert result["route"] == "education_learning_event_v1"
    assert result["event_key"] == "exam_assessment"
    assert "guarantee" in result["limitation"].lower() or "not" in result["limitation"].lower()


def test_unknown_question_is_unsupported():
    result = route_education_learning_question_v1(_chart(), "What colour should I paint my room?", NOW)
    assert result["available"] is False
    assert result["route"] == "unsupported"
