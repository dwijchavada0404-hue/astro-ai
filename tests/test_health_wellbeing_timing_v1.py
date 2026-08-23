from datetime import datetime, timezone

import pytest

from app.astrology.features.health_wellbeing_timing_v1 import analyze_health_wellbeing_timing_v1

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _chart():
    return {"houses": {"1": {"lord": "Sun"}, "6": {"lord": "Mercury"}, "8": {"lord": "Mars"}, "12": {"lord": "Moon"}}, "planets": {"Sun": {"house": 1}, "Mercury": {"house": 6}, "Mars": {"house": 8}, "Moon": {"house": 12}, "Saturn": {"house": 6}, "Jupiter": {"house": 1}, "Venus": {"house": 12}}, "dasha_periods": [{"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Moon", "sub_lord": "Venus"}, {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Sun", "sub_lord": "Saturn"}, {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Mercury"}]}


def test_timing_separates_phases_and_bounds_scores():
    result = analyze_health_wellbeing_timing_v1(_chart(), NOW)
    assert result["available"] is True
    assert result["past"]["strongest_period"] is not None and result["present"]["active_period"] is not None and result["future"]["strongest_period"] is not None
    for phase, key in (("past", "strongest_period"), ("present", "active_period"), ("future", "strongest_period")):
        period = result[phase][key]
        for score_key in ("vitality_support_score", "routine_support_score", "recovery_support_score", "stress_balance_support_score", "rest_support_score", "self_care_support_score", "overall_activation_score"):
            assert 0.0 <= period[score_key] <= 1.0


def test_past_activation_is_not_medical_evidence():
    result = analyze_health_wellbeing_timing_v1(_chart(), NOW)
    assert result["past"]["historical_status"] == "unconfirmed"
    rule = result["historical_validation"]["rule"].lower()
    assert "not evidence" in rule and "diagnosis" in rule


def test_medical_prediction_is_disallowed():
    text = analyze_health_wellbeing_timing_v1(_chart(), NOW)["limitation"].lower()
    for term in ("disease", "diagnosis", "prognosis", "lifespan", "death", "accidents", "treatment response"):
        assert term in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_health_wellbeing_timing_v1(_chart(), datetime(2026, 8, 23))


def test_missing_dasha_is_unavailable():
    chart = _chart(); chart.pop("dasha_periods")
    result = analyze_health_wellbeing_timing_v1(chart, NOW)
    assert result["available"] is False and "dasha" in result["reason"].lower()
