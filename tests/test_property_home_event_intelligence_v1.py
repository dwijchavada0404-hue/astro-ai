from datetime import datetime, timezone

from app.astrology.features.property_home_event_intelligence_v1 import (
    analyze_property_home_event_intelligence_v1,
)
from tests.test_property_home_timing_v1 import _chart


def _now():
    return datetime(2026, 8, 21, tzinfo=timezone.utc)


def test_event_intelligence_exposes_distinct_event_categories():
    result = analyze_property_home_event_intelligence_v1(_chart(), _now())
    assert result["available"] is True
    assert result["event"] == "property_home_event_intelligence"
    assert set(result["events"]) == {
        "property_acquisition",
        "property_sale_disposal",
        "relocation",
        "inheritance_family_property",
        "renovation_construction",
    }


def test_event_scores_are_bounded_across_time():
    result = analyze_property_home_event_intelligence_v1(_chart(), _now())
    for event in result["events"].values():
        assert 0.0 <= event["natal_strength"] <= 1.0
        for bucket in ("past", "present", "future"):
            assert 0.0 <= event[bucket]["score"] <= 1.0


def test_past_event_windows_are_not_claimed_as_history():
    result = analyze_property_home_event_intelligence_v1(_chart(), _now())
    assert result["historical_validation"]["status"] == "unconfirmed"
    assert result["historical_validation"]["reality_override"] is True
    for event in result["events"].values():
        assert event["past"]["historical_status"] == "unconfirmed"


def test_future_event_highlight_is_not_probability_language():
    result = analyze_property_home_event_intelligence_v1(_chart(), _now())
    assert result["strongest_future_event"] in result["events"]
    assert 0.0 <= result["strongest_future_event_score"] <= 1.0
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "not event probability or proof" in text
    assert "does not predict or guarantee property purchase" in text


def test_missing_foundation_returns_unavailable():
    result = analyze_property_home_event_intelligence_v1(
        {"houses": {}, "planets": {}},
        _now(),
    )
    assert result["available"] is False
