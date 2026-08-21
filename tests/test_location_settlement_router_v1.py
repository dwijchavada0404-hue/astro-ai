from datetime import datetime, timezone

from app.astrology.features.location_settlement_question_intelligence_v1 import analyze_location_settlement_question_v1
from app.astrology.features.location_settlement_router_v1 import route_location_settlement_question_v1
from tests.test_location_settlement_timing_v1 import _chart


NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def test_foreign_settlement_question_is_distinct_from_exposure():
    understanding = analyze_location_settlement_question_v1("Will I settle abroad permanently?")
    assert understanding["primary_intent"] == "foreign_settlement"
    assert understanding["safety"]["foreign_exposure_equals_settlement"] is False


def test_travel_question_routes_to_foreign_exposure_event():
    result = route_location_settlement_question_v1(_chart(), "Will I travel abroad?", NOW)
    assert result["available"] is True
    assert result["route"] == "location_settlement_event_v1"
    assert result["event_key"] == "foreign_travel_exposure"


def test_foreign_settlement_question_routes_to_strict_event():
    result = route_location_settlement_question_v1(_chart(), "Will I settle abroad?", NOW)
    assert result["route"] == "location_settlement_event_v1"
    assert result["event_key"] == "foreign_settlement"
    assert result["event_result"] is not None


def test_generic_foreign_timing_question_routes_to_timing():
    result = route_location_settlement_question_v1(_chart(), "When is my strongest foreign period?", NOW)
    assert result["route"] == "location_settlement_timing_v1"
    assert result["timing"]["available"] is True


def test_location_overview_routes_to_synthesis():
    result = route_location_settlement_question_v1(_chart(), "Tell me about my location future", NOW)
    assert result["route"] == "location_settlement_synthesis_v1"
    assert result["synthesis"]["historical_validation"]["status"] == "unconfirmed"


def test_unrelated_question_is_declined():
    result = route_location_settlement_question_v1(_chart(), "When will I get married?", NOW)
    assert result["available"] is False
    assert result["route"] == "unsupported"


def test_router_preserves_immigration_boundary():
    result = route_location_settlement_question_v1(_chart(), "Will I settle abroad?", NOW)
    text = result["limitation"].lower()
    assert "visa approval" in text
    assert "citizenship" in text
    assert "particular country or city" in text
