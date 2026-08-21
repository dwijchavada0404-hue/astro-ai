from datetime import datetime, timezone

import pytest

from app.astrology.features.purpose_personal_growth_timing_v1 import analyze_purpose_personal_growth_timing_v1

NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"1": {"lord": "Sun"}, "5": {"lord": "Jupiter"}, "6": {"lord": "Saturn"}, "9": {"lord": "Mercury"}, "10": {"lord": "Mars"}, "11": {"lord": "Venus"}, "12": {"lord": "Moon"}},
        "planets": {"Sun": {"house": 10}, "Jupiter": {"house": 9}, "Saturn": {"house": 6}, "Mercury": {"house": 5}, "Mars": {"house": 10}, "Venus": {"house": 11}, "Moon": {"house": 12}, "Ketu": {"house": 9}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Jupiter"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Sun", "sub_lord": "Saturn"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Moon"},
        ],
    }


def test_timing_has_past_present_future_without_claiming_growth_events():
    result = analyze_purpose_personal_growth_timing_v1(_chart(), NOW)
    assert result["available"] is True
    assert result["past"]["available"] and result["present"]["available"] and result["future"]["available"]
    assert result["past"]["historical_status"] == "unconfirmed"
    assert "not proof" in result["historical_validation"]["rule"].lower()


def test_timing_dimensions_are_separate_and_bounded():
    future = analyze_purpose_personal_growth_timing_v1(_chart(), NOW)["future"]["strongest_period"]
    for key in ("self_growth_support_score", "contribution_support_score", "meaning_guidance_support_score", "inner_growth_support_score"):
        assert 0.0 <= future[key] <= 1.0


def test_no_dashas_is_unavailable():
    chart = _chart(); chart.pop("dasha_periods")
    result = analyze_purpose_personal_growth_timing_v1(chart, NOW)
    assert result["available"] is False
    assert "dasha" in result["reason"].lower()


def test_timezone_and_bounds_are_enforced():
    with pytest.raises(ValueError, match="timezone"):
        analyze_purpose_personal_growth_timing_v1(_chart(), datetime(2026, 8, 21))
    with pytest.raises(ValueError):
        analyze_purpose_personal_growth_timing_v1(_chart(), NOW, lookahead_years=11)


def test_destiny_boundaries_are_explicit():
    text = analyze_purpose_personal_growth_timing_v1(_chart(), NOW)["limitation"].lower()
    assert "not proof of destiny" in text
    assert "spiritual attainment" in text
    assert "values and choices" in text
