from datetime import datetime, timezone

import pytest

from app.astrology.features.travel_journeys_timing_v1 import analyze_travel_journeys_timing_v1

NOW = datetime(2026, 8, 22, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"3": {"lord": "Mercury"}, "6": {"lord": "Saturn"}, "9": {"lord": "Jupiter"}, "10": {"lord": "Sun"}, "12": {"lord": "Rahu"}},
        "planets": {"Mercury": {"house": 3}, "Moon": {"house": 9}, "Jupiter": {"house": 9}, "Rahu": {"house": 12}, "Saturn": {"house": 6}, "Sun": {"house": 10}, "Mars": {"house": 3}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Moon"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Rahu"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Mercury"},
        ],
    }


def test_timing_separates_past_present_future_and_bounds_scores():
    result = analyze_travel_journeys_timing_v1(_chart(), NOW)
    assert result["available"] is True
    assert result["past"]["strongest_period"] is not None
    assert result["present"]["active_period"] is not None
    assert result["future"]["strongest_period"] is not None
    for phase, key in (("past", "strongest_period"), ("present", "active_period"), ("future", "strongest_period")):
        period = result[phase][key]
        for score_key in (
            "short_journey_support_score", "long_distance_support_score", "international_support_score",
            "work_study_travel_support_score", "recurring_mobility_support_score", "travel_adaptability_support_score",
            "overall_activation_score",
        ):
            assert 0.0 <= period[score_key] <= 1.0


def test_past_travel_activation_is_unconfirmed():
    result = analyze_travel_journeys_timing_v1(_chart(), NOW)
    assert result["past"]["historical_status"] == "unconfirmed"
    rule = result["historical_validation"]["rule"].lower()
    assert "not evidence" in rule
    assert "known travel history overrides astrology" in rule


def test_travel_is_not_silently_converted_to_settlement_or_safety_prediction():
    text = analyze_travel_journeys_timing_v1(_chart(), NOW)["limitation"].lower()
    assert "immigration" in text
    assert "relocation" in text and "settlement" in text
    assert "travel safety" in text and "accident" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_travel_journeys_timing_v1(_chart(), datetime(2026, 8, 22))


def test_missing_dasha_is_unavailable_not_invented():
    chart = _chart(); chart.pop("dasha_periods")
    result = analyze_travel_journeys_timing_v1(chart, NOW)
    assert result["available"] is False
    assert "dasha" in result["reason"].lower()
