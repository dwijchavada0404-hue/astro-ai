from datetime import datetime, timezone

from app.astrology.features.property_home_trajectory_v1 import analyze_property_home_trajectory_v1
from tests.test_property_home_timing_v1 import _chart


def _now():
    return datetime(2026, 8, 21, tzinfo=timezone.utc)


def test_trajectory_exposes_long_term_dimensions():
    result = analyze_property_home_trajectory_v1(_chart(), _now())
    assert result["available"] is True
    assert result["event"] == "property_home_trajectory"
    for key in (
        "accumulation_score", "stability_score", "mobility_score", "challenge_score",
        "resilience_score", "recovery_score",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_trajectory_has_pattern_and_near_term_direction():
    result = analyze_property_home_trajectory_v1(_chart(), _now())
    assert result["trajectory_pattern"] in {
        "stable_asset_building",
        "mobile_or_transitioning_home_pattern",
        "challenging_but_recoverable",
        "mixed_gradual_development",
    }
    assert result["near_term_direction"] in {
        "strengthening",
        "cooling_or_consolidating",
        "change_or_mobility_emphasis",
        "broadly_stable",
    }


def test_trajectory_preserves_reality_override():
    result = analyze_property_home_trajectory_v1(_chart(), _now())
    historical = result["historical_validation"]
    assert historical["status"] == "unconfirmed"
    assert historical["reality_override"] is True
    assert "known property and residence history overrides" in historical["rule"].lower()


def test_trajectory_keeps_non_guarantee_language():
    result = analyze_property_home_trajectory_v1(_chart(), _now())
    assert "does not guarantee property accumulation" in result["limitation"].lower()
    assert "components" in result


def test_missing_foundation_returns_unavailable():
    result = analyze_property_home_trajectory_v1(
        {"houses": {}, "planets": {}},
        _now(),
    )
    assert result["available"] is False
