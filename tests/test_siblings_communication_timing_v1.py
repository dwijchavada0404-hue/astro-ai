from datetime import datetime, timezone

import pytest

from app.astrology.features.siblings_communication_timing_v1 import analyze_siblings_communication_timing_v1

NOW = datetime(2026, 8, 22, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"1": {"lord": "Sun"}, "2": {"lord": "Moon"}, "3": {"lord": "Mercury"}, "5": {"lord": "Jupiter"}, "6": {"lord": "Saturn"}, "7": {"lord": "Venus"}, "11": {"lord": "Mars"}},
        "planets": {"Sun": {"house": 10}, "Moon": {"house": 2}, "Mercury": {"house": 3}, "Jupiter": {"house": 5}, "Saturn": {"house": 6}, "Venus": {"house": 7}, "Mars": {"house": 11}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Moon"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Mars", "sub_lord": "Venus"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Saturn"},
        ],
    }


def test_timing_has_past_present_future_without_claiming_events():
    result = analyze_siblings_communication_timing_v1(_chart(), NOW)
    assert result["available"] is True
    assert result["past"]["available"] and result["present"]["available"] and result["future"]["available"]
    assert result["past"]["historical_status"] == "unconfirmed"
    assert "not proof" in result["historical_validation"]["rule"].lower()


def test_timing_dimensions_are_bounded():
    future = analyze_siblings_communication_timing_v1(_chart(), NOW)["future"]["strongest_period"]
    for key in ("sibling_relationship_support_score", "communication_learning_support_score", "initiative_boundary_support_score", "collaboration_support_score"):
        assert 0.0 <= future[key] <= 1.0


def test_no_dashas_returns_unavailable():
    chart = _chart(); chart.pop("dasha_periods")
    result = analyze_siblings_communication_timing_v1(chart, NOW)
    assert result["available"] is False
    assert "dasha" in result["reason"].lower()


def test_timezone_and_bounds_are_enforced():
    with pytest.raises(ValueError, match="timezone"):
        analyze_siblings_communication_timing_v1(_chart(), datetime(2026, 8, 22))
    with pytest.raises(ValueError):
        analyze_siblings_communication_timing_v1(_chart(), NOW, lookahead_years=11)


def test_specific_person_and_outcome_boundaries_are_explicit():
    text = analyze_siblings_communication_timing_v1(_chart(), NOW)["limitation"].lower()
    assert "not a probability or guarantee" in text
    assert "estrangement" in text
    assert "specific person's intentions" in text
