from datetime import datetime, timezone

from app.astrology.features.property_home_synthesis_v1 import analyze_property_home_synthesis_v1
from tests.test_property_home_timing_v1 import _chart


def _now():
    return datetime(2026, 8, 21, tzinfo=timezone.utc)


def test_synthesis_combines_all_property_home_layers():
    result = analyze_property_home_synthesis_v1(_chart(), _now())
    assert result["available"] is True
    assert result["event"] == "property_home_synthesis"
    assert set(result["components"]) == {"natal", "direction", "timing", "events", "trajectory"}
    assert all(result["component_availability"].values())


def test_synthesis_scores_and_confidence_are_bounded():
    result = analyze_property_home_synthesis_v1(_chart(), _now())
    assert 0.0 <= result["property_home_development_score"] <= 1.0
    assert result["property_home_development_outlook"] in {"strong", "moderate", "limited"}
    assert 0.0 <= result["confidence"] <= 1.0
    assert 0.0 <= result["strongest_future_event_score"] <= 1.0


def test_synthesis_exposes_direction_timing_and_trajectory():
    result = analyze_property_home_synthesis_v1(_chart(), _now())
    assert result["primary_direction"] is not None
    assert result["primary_direction_label"]
    assert result["trajectory_pattern"]
    assert result["near_term_direction"]
    assert result["active_present_period"] is not None
    assert result["strongest_future_period"] is not None
    assert result["strongest_future_event"] in {
        "property_acquisition",
        "property_sale_disposal",
        "relocation",
        "inheritance_family_property",
        "renovation_construction",
    }


def test_synthesis_preserves_reality_override():
    result = analyze_property_home_synthesis_v1(_chart(), _now())
    historical = result["historical_validation"]
    assert historical["status"] == "unconfirmed"
    assert historical["reality_override"] is True
    assert "known ownership" in historical["rule"].lower()
    assert "user has confirmed" in historical["rule"].lower()


def test_synthesis_language_is_non_deterministic():
    result = analyze_property_home_synthesis_v1(_chart(), _now())
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "does not guarantee property ownership" in text
    assert "real-estate advice" in text


def test_missing_foundation_returns_unavailable():
    result = analyze_property_home_synthesis_v1(
        {"houses": {}, "planets": {}},
        _now(),
    )
    assert result["available"] is False
