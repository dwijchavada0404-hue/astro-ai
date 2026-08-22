from datetime import datetime, timezone

from app.astrology.features.parents_elders_question_intelligence_v1 import analyze_parents_elders_question_v1
from app.astrology.features.parents_elders_router_v1 import route_parents_elders_question_v1

NOW = datetime(2026, 8, 22, tzinfo=timezone.utc)


def _chart():
    return {"houses": {"4": {"lord": "Moon"}, "9": {"lord": "Jupiter"}, "10": {"lord": "Sun"}}, "planets": {"Moon": {"house": 4}, "Jupiter": {"house": 9}, "Sun": {"house": 10}, "Saturn": {"house": 6}, "Mars": {"house": 3}, "Venus": {"house": 4}}, "dasha_periods": [{"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Moon", "sub_lord": "Jupiter"}, {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Sun", "sub_lord": "Saturn"}, {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Venus"}]}


def test_overview_routes_to_synthesis():
    understanding = analyze_parents_elders_question_v1("Tell me about my parents and elders")
    assert understanding["primary_intent"] == "parents_elders_overview"
    result = route_parents_elders_question_v1(_chart(), "Tell me about my parents and elders", NOW)
    assert result["route"] == "parents_elders_synthesis_v1"
    assert result["available"] is True


def test_timing_question_routes_to_timing_engine():
    result = route_parents_elders_question_v1(_chart(), "When is a strong period for family responsibilities with parents?", NOW)
    assert result["route"] in {"parents_elders_event_v1", "parents_elders_timing_v1"}
    assert result["understanding"]["timing_requested"] is True


def test_prohibited_health_or_death_request_is_blocked():
    result = route_parents_elders_question_v1(_chart(), "When will my father die?", NOW)
    assert result["route"] == "parents_elders_safety_boundary_v1"
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "lifespan" in text and "death" in text
    assert "health" in text


def test_specific_person_character_inference_is_blocked():
    result = route_parents_elders_question_v1(_chart(), "Is my father good and what does my father think?", NOW)
    assert result["route"] == "parents_elders_safety_boundary_v1"
    assert result["understanding"]["prohibited_request_detected"] is True
    assert result["understanding"]["safety"]["specific_person_intention_or_character_inference_allowed"] is False


def test_unrelated_question_is_unsupported():
    result = route_parents_elders_question_v1(_chart(), "What colour should I paint my desk?", NOW)
    assert result["available"] is False
    assert result["route"] == "unsupported"
