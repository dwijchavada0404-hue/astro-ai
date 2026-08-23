from datetime import datetime, timezone

from app.astrology.features.travel_journeys_question_intelligence_v1 import analyze_travel_journeys_question_v1
from app.services.travel_journeys_question_router_v1 import route_travel_journeys_question_v1

NOW = datetime(2026, 8, 22, tzinfo=timezone.utc)


def _chart():
    return {"houses": {"3": {"lord": "Mercury"}, "9": {"lord": "Jupiter"}, "12": {"lord": "Saturn"}, "6": {"lord": "Mars"}, "10": {"lord": "Sun"}}, "planets": {"Mercury": {"house": 3}, "Jupiter": {"house": 9}, "Rahu": {"house": 12}, "Moon": {"house": 3}, "Mars": {"house": 6}, "Sun": {"house": 10}, "Saturn": {"house": 12}}, "dasha_periods": [{"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Rahu"}, {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Mercury"}]}


def test_overview_wins_over_component_words():
    result = analyze_travel_journeys_question_v1("Give me my travel and journeys overview")
    assert result["primary_intent"] == "travel_overview"


def test_foreign_travel_is_travel_not_settlement():
    result = analyze_travel_journeys_question_v1("When is foreign travel likely for me?")
    assert result["available"] is True
    assert result["primary_intent"] == "international_travel"
    assert result["timing_requested"] is True
    assert result["handoff_to_location_settlement"] is False


def test_permanent_settlement_is_handed_off():
    result = route_travel_journeys_question_v1("When will I settle abroad permanently?", _chart(), NOW)
    assert result["available"] is False
    assert "location & foreign settlement" in result["reason"].lower()


def test_visa_and_safety_outcomes_are_restricted():
    result = route_travel_journeys_question_v1("Will my visa be approved and will my trip be safe?", _chart(), NOW)
    assert result["restricted"] is True
    text = result["answer"].lower()
    assert "visa approval" in text and "travel safety" in text


def test_timing_question_routes_to_timing_engine():
    result = route_travel_journeys_question_v1("When is my strongest period for international travel?", _chart(), NOW)
    assert result["available"] is True
    assert result["result"]["event"] == "travel_journeys_timing"
