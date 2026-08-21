from datetime import datetime, timezone

import pytest

from app.astrology.features.location_settlement_timing_v1 import analyze_location_settlement_timing_v1


NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {
            "3": {"lord": "Mercury"}, "4": {"lord": "Moon"}, "7": {"lord": "Mars"},
            "9": {"lord": "Jupiter"}, "12": {"lord": "Saturn"},
        },
        "planets": {
            "Mercury": {"house": 9}, "Moon": {"house": 12}, "Mars": {"house": 7},
            "Jupiter": {"house": 12}, "Saturn": {"house": 4}, "Rahu": {"house": 9}, "Ketu": {"house": 3},
        },
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Rahu"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Saturn"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Jupiter"},
        ],
    }


def test_timing_exposes_past_present_future_without_claiming_events():
    result = analyze_location_settlement_timing_v1(_chart(), NOW)
    assert result["available"] is True
    assert result["past"]["available"] is True
    assert result["present"]["available"] is True
    assert result["future"]["available"] is True
    assert result["past"]["historical_status"] == "unconfirmed"
    assert "not proof" in result["historical_validation"]["rule"].lower()


def test_future_period_keeps_exposure_and_settlement_distinct():
    result = analyze_location_settlement_timing_v1(_chart(), NOW)
    future = result["future"]["strongest_period"]
    assert 0.0 <= future["foreign_exposure_score"] <= 1.0
    assert 0.0 <= future["foreign_settlement_support_score"] <= 1.0
    assert "relocation_activation_score" in future


def test_no_dashas_returns_unavailable():
    chart = _chart()
    chart.pop("dasha_periods")
    result = analyze_location_settlement_timing_v1(chart, NOW)
    assert result["available"] is False
    assert "dasha" in result["reason"].lower()


def test_timezone_and_bounds_are_enforced():
    with pytest.raises(ValueError, match="timezone"):
        analyze_location_settlement_timing_v1(_chart(), datetime(2026, 8, 21))
    with pytest.raises(ValueError):
        analyze_location_settlement_timing_v1(_chart(), NOW, lookahead_years=11)


def test_immigration_boundaries_are_explicit():
    result = analyze_location_settlement_timing_v1(_chart(), NOW)
    text = result["limitation"].lower()
    assert "visa approval" in text
    assert "citizenship" in text
    assert "without permanent settlement" in text
