from datetime import datetime, timezone

from app.astrology.features.siblings_communication_question_intelligence_v1 import analyze_siblings_communication_question_v1
from app.astrology.features.siblings_communication_router_v1 import route_siblings_communication_question_v1

NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"3": {"lord": "Mercury"}, "5": {"lord": "Jupiter"}, "6": {"lord": "Saturn"}, "7": {"lord": "Venus"}, "11": {"lord": "Moon"}},
        "planets": {"Mercury": {"house": 3}, "Mars": {"house": 6}, "Jupiter": {"house": 5}, "Venus": {"house": 7}, "Moon": {"house": 11}, "Saturn": {"house": 3}, "Sun": {"house": 10}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Jupiter"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Mars", "sub_lord": "Saturn"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Venus", "sub_lord": "Moon"},
        ],
    }


def test_question_intelligence_detects_sibling_timing():
    result = analyze_siblings_communication_question_v1("When is a strong period for my relationship with my brother?")
    assert result["available"] is True
    assert result["primary_intent"] == "sibling_relationship"
    assert result["timing_requested"] is True
    assert result["safety"]["loyalty_judgment_allowed"] is False


def test_router_routes_overview_to_synthesis():
    result = route_siblings_communication_question_v1(_chart(), "Give me a siblings and communication overview", NOW)
    assert result["available"] is True
    assert result["route"] == "siblings_communication_synthesis_v1"


def test_router_routes_specific_intent_to_event_layer():
    result = route_siblings_communication_question_v1(_chart(), "How is my communication expression?", NOW)
    assert result["route"] == "siblings_communication_event_v1"
    assert result["event_key"] == "communication_expression"


def test_specific_person_safety_is_preserved():
    understanding = analyze_siblings_communication_question_v1("Will my brother stay loyal to me?")
    assert understanding["available"] is True
    assert understanding["safety"]["specific_person_intention_inference_allowed"] is False
    assert understanding["safety"]["loyalty_judgment_allowed"] is False


def test_unknown_question_is_unsupported():
    result = route_siblings_communication_question_v1(_chart(), "What colour should I paint my desk?", NOW)
    assert result["available"] is False
    assert result["route"] == "unsupported"
