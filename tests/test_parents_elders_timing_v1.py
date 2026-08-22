from datetime import datetime, timezone

import pytest

from app.astrology.features.parents_elders_timing_v1 import analyze_parents_elders_timing_v1

NOW = datetime(2026, 8, 22, tzinfo=timezone.utc)


def _chart():
    return {"houses": {"4": {"lord": "Moon"}, "9": {"lord": "Jupiter"}, "10": {"lord": "Sun"}}, "planets": {"Moon": {"house": 4}, "Jupiter": {"house": 9}, "Sun": {"house": 10}, "Saturn": {"house": 6}, "Mars": {"house": 3}, "Venus": {"house": 4}}, "dasha_periods": [{"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Moon", "sub_lord": "Jupiter"}, {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Sun", "sub_lord": "Saturn"}, {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Venus"}]}


def test_timing_separates_past_present_future_and_bounds_scores():
    result = analyze_parents_elders_timing_v1(_chart(), NOW)
    assert result["available"] is True
    assert result["past"]["strongest_period"] is not None
    assert result["present"]["active_period"] is not None
    assert result["future"]["strongest_period"] is not None
    for phase, key in (("past", "strongest_period"), ("present", "active_period"), ("future", "strongest_period")):
        period = result[phase][key]
        for score_key in ("guidance_support_score", "emotional_support_score", "duty_support_score", "authority_support_score", "boundary_support_score", "continuity_support_score", "overall_activation_score"):
            assert 0.0 <= period[score_key] <= 1.0


def test_past_family_activation_is_unconfirmed():
    result = analyze_parents_elders_timing_v1(_chart(), NOW)
    assert result["past"]["historical_status"] == "unconfirmed"
    rule = result["historical_validation"]["rule"].lower()
    assert "not evidence" in rule
    assert "known family history overrides astrology" in rule


def test_health_death_and_relationship_outcomes_are_disallowed():
    text = analyze_parents_elders_timing_v1(_chart(), NOW)["limitation"].lower()
    assert "health" in text and "illness" in text
    assert "lifespan" in text and "death" in text
    assert "reconciliation" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_parents_elders_timing_v1(_chart(), datetime(2026, 8, 22))


def test_missing_dasha_is_unavailable_not_invented():
    chart = _chart(); chart.pop("dasha_periods")
    result = analyze_parents_elders_timing_v1(chart, NOW)
    assert result["available"] is False
    assert "dasha" in result["reason"].lower()
