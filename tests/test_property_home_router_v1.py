from datetime import datetime, timezone

from app.astrology.features.property_home_router_v1 import route_property_home_question_v1
from tests.test_property_home_timing_v1 import _chart


def _now():
    return datetime(2026, 8, 21, tzinfo=timezone.utc)


def test_acquisition_question_routes_to_event_intelligence():
    result = route_property_home_question_v1(_chart(), "Will I buy a house?", _now())
    assert result["available"] is True
    assert result["route"] == "property_home_event_v1"
    assert result["event_key"] == "property_acquisition"
    assert result["event_result"] is not None


def test_relocation_question_routes_to_event_intelligence():
    result = route_property_home_question_v1(_chart(), "When will I relocate?", _now())
    assert result["route"] == "property_home_event_v1"
    assert result["event_key"] == "relocation"


def test_generic_timing_question_routes_to_timing():
    result = route_property_home_question_v1(_chart(), "When is my strongest property period?", _now())
    assert result["route"] == "property_home_timing_v1"
    assert result["timing"]["available"] is True


def test_direction_question_routes_to_direction_engine():
    result = route_property_home_question_v1(_chart(), "How is my property potential?", _now())
    assert result["route"] == "property_home_direction_v1"
    assert result["direction"]["primary_direction"] is not None


def test_overview_question_routes_to_synthesis():
    result = route_property_home_question_v1(_chart(), "Tell me about my property future", _now())
    assert result["route"] == "property_home_synthesis_v1"
    assert result["synthesis"]["event"] == "property_home_synthesis"
    assert result["synthesis"]["historical_validation"]["status"] == "unconfirmed"


def test_unrelated_question_is_declined():
    result = route_property_home_question_v1(_chart(), "When will I get married?", _now())
    assert result["available"] is False
    assert result["route"] == "unsupported"


def test_router_keeps_non_guarantee_language():
    result = route_property_home_question_v1(_chart(), "Will I own a house?", _now())
    assert "does not predict or guarantee property purchase" in result["limitation"].lower()
