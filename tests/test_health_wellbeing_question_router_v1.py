from datetime import datetime, timezone

from app.astrology.features.health_wellbeing_question_intelligence_v1 import analyze_health_wellbeing_question_v1
from app.astrology.features.health_wellbeing_router_v1 import route_health_wellbeing_question_v1

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"1": {"lord": "Sun"}, "6": {"lord": "Mercury"}, "8": {"lord": "Saturn"}, "12": {"lord": "Jupiter"}},
        "planets": {
            "Sun": {"house": 1}, "Moon": {"house": 4}, "Mars": {"house": 6},
            "Saturn": {"house": 8}, "Jupiter": {"house": 12}, "Mercury": {"house": 6}, "Venus": {"house": 12},
        },
        "dasha_periods": [
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Moon"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Venus"},
        ],
    }


def test_overview_routes_to_synthesis():
    result = route_health_wellbeing_question_v1(_chart(), "Give me my health and wellbeing overview", NOW)
    assert result["available"] is True
    assert result["route"] == "health_wellbeing_synthesis_v1"


def test_timing_routes_to_timing_engine():
    result = route_health_wellbeing_question_v1(_chart(), "When is a stronger period for my wellbeing routine?", NOW)
    assert result["available"] is True
    assert result["route"] == "health_wellbeing_timing_v1"


def test_component_routes_to_event_intelligence():
    result = route_health_wellbeing_question_v1(_chart(), "What are my stress balance themes?", NOW)
    assert result["available"] is True
    assert result["route"] == "health_wellbeing_event_v1"
    assert result["primary_intent"] == "stress_balance"


def test_medical_diagnosis_prediction_is_blocked():
    result = route_health_wellbeing_question_v1(_chart(), "Will I get diabetes in the future?", NOW)
    assert result["available"] is True
    assert result["route"] == "health_wellbeing_safety_boundary_v1"
    text = result["answer"].lower()
    assert "cannot diagnose or predict disease" in text


def test_treatment_and_medication_request_is_blocked():
    result = route_health_wellbeing_question_v1(_chart(), "Which medication or supplement should I take for this illness?", NOW)
    assert result["route"] == "health_wellbeing_safety_boundary_v1"
    text = result["answer"].lower()
    assert "cannot recommend treatment" in text
    assert "medication" in text and "supplements" in text


def test_non_health_question_stays_unavailable():
    result = analyze_health_wellbeing_question_v1("When will I buy a house?")
    assert result["available"] is False
    assert result["primary_intent"] == "unknown"
