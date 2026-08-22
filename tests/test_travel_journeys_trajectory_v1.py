from datetime import datetime, timezone

import pytest

from app.astrology.features.travel_journeys_trajectory_v1 import analyze_travel_journeys_trajectory_v1

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


def test_trajectory_scores_are_bounded_and_patterned():
    result = analyze_travel_journeys_trajectory_v1(_chart(), NOW)
    assert result["available"] is True
    for key in ("short_journey_score", "long_distance_score", "international_exposure_score", "work_study_travel_score", "recurring_mobility_score", "travel_adaptability_score"):
        assert 0.0 <= result[key] <= 1.0
    assert result["trajectory_pattern"]
    assert result["near_term_direction"]


def test_trajectory_uses_all_lower_layers():
    result = analyze_travel_journeys_trajectory_v1(_chart(), NOW)
    assert result["timing_available"] is True
    assert result["events_available"] is True
    assert set(result["components"]) == {"natal", "timing", "events"}


def test_reality_override_prevents_manufactured_travel_history():
    rule = analyze_travel_journeys_trajectory_v1(_chart(), NOW)["historical_validation"]["rule"].lower()
    assert "known travel history" in rule
    assert "must not manufacture" in rule
    assert "relocation" in rule and "settlement" in rule


def test_settlement_visa_destination_and_safety_claims_are_disallowed():
    text = analyze_travel_journeys_trajectory_v1(_chart(), NOW)["limitation"].lower()
    assert "exact destination" in text
    assert "visa/immigration" in text
    assert "permanent relocation or settlement" in text
    assert "accidents" in text and "delays" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_travel_journeys_trajectory_v1(_chart(), datetime(2026, 8, 22))
