from datetime import datetime, timezone

import pytest

from app.astrology.features.travel_journeys_synthesis_v1 import analyze_travel_journeys_synthesis_v1

NOW = datetime(2026, 8, 22, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"3": {"lord": "Mercury"}, "9": {"lord": "Jupiter"}, "12": {"lord": "Saturn"}, "6": {"lord": "Mars"}, "10": {"lord": "Sun"}},
        "planets": {"Mercury": {"house": 3}, "Jupiter": {"house": 9}, "Rahu": {"house": 12}, "Moon": {"house": 3}, "Mars": {"house": 6}, "Sun": {"house": 10}, "Saturn": {"house": 12}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Moon"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Rahu"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Mercury"},
        ],
    }


def test_synthesis_scores_confidence_and_coverage_are_bounded():
    result = analyze_travel_journeys_synthesis_v1(_chart(), NOW)
    assert result["available"] is True
    assert 0.0 <= result["confidence"] <= 1.0
    assert 0.0 <= result["component_coverage"] <= 1.0
    assert all(0.0 <= score <= 1.0 for score in result["scores"].values())


def test_synthesis_exposes_outlook_and_future_context():
    result = analyze_travel_journeys_synthesis_v1(_chart(), NOW)
    assert result["outlook"]
    assert result["strongest_area"] in result["scores"]
    assert result["strongest_future_period"] is not None
    assert result["strongest_future_event"] is not None


def test_reality_override_prevents_manufactured_travel_events():
    rule = analyze_travel_journeys_synthesis_v1(_chart(), NOW)["historical_validation"]["rule"].lower()
    assert "known travel history" in rule
    assert "must never manufacture" in rule
    assert "relocation" in rule and "settlement" in rule


def test_destination_settlement_visa_and_safety_claims_are_disallowed():
    text = analyze_travel_journeys_synthesis_v1(_chart(), NOW)["limitation"].lower()
    assert "exact destination" in text
    assert "visa/immigration" in text
    assert "permanent relocation or settlement" in text
    assert "accidents" in text and "delays" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_travel_journeys_synthesis_v1(_chart(), datetime(2026, 8, 22))
