from datetime import datetime, timezone

import pytest

from app.astrology.features.education_learning_timing_v1 import analyze_education_learning_timing_v1


NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {
            "3": {"lord": "Mercury"}, "4": {"lord": "Moon"}, "5": {"lord": "Jupiter"},
            "8": {"lord": "Saturn"}, "9": {"lord": "Mars"},
        },
        "planets": {
            "Mercury": {"house": 5}, "Moon": {"house": 4}, "Jupiter": {"house": 9},
            "Saturn": {"house": 8}, "Mars": {"house": 3}, "Venus": {"house": 5},
        },
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Jupiter"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Moon"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Mars"},
        ],
    }


def test_timing_exposes_past_present_future_without_claiming_events():
    result = analyze_education_learning_timing_v1(_chart(), NOW)
    assert result["available"] is True
    assert result["past"]["available"] is True
    assert result["present"]["available"] is True
    assert result["future"]["available"] is True
    assert result["past"]["historical_status"] == "unconfirmed"
    assert "not proof" in result["historical_validation"]["rule"].lower()


def test_learning_timing_dimensions_are_separate_and_bounded():
    result = analyze_education_learning_timing_v1(_chart(), NOW)
    future = result["future"]["strongest_period"]
    for key in ("study_support_score", "higher_education_support_score", "skill_learning_support_score", "research_support_score"):
        assert 0.0 <= future[key] <= 1.0


def test_no_dashas_returns_unavailable():
    chart = _chart()
    chart.pop("dasha_periods")
    result = analyze_education_learning_timing_v1(chart, NOW)
    assert result["available"] is False
    assert "dasha" in result["reason"].lower()


def test_timezone_and_bounds_are_enforced():
    with pytest.raises(ValueError, match="timezone"):
        analyze_education_learning_timing_v1(_chart(), datetime(2026, 8, 21))
    with pytest.raises(ValueError):
        analyze_education_learning_timing_v1(_chart(), NOW, lookahead_years=11)


def test_outcome_boundaries_are_explicit():
    result = analyze_education_learning_timing_v1(_chart(), NOW)
    text = result["limitation"].lower()
    assert "admission" in text
    assert "examination success" in text
    assert "graduation" in text
    assert "not a probability or guarantee" in text
