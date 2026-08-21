from datetime import datetime, timezone

import pytest

from app.astrology.features.education_learning_trajectory_v1 import analyze_education_learning_trajectory_v1


NOW = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"3": {"lord": "Mercury"}, "4": {"lord": "Moon"}, "5": {"lord": "Jupiter"}, "8": {"lord": "Saturn"}, "9": {"lord": "Mars"}},
        "planets": {"Mercury": {"house": 5}, "Moon": {"house": 4}, "Jupiter": {"house": 9}, "Saturn": {"house": 8}, "Mars": {"house": 3}, "Venus": {"house": 5}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Jupiter"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Moon"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Mars"},
        ],
    }


def test_trajectory_scores_are_bounded():
    result = analyze_education_learning_trajectory_v1(_chart(), NOW)
    assert result["available"] is True
    for key in ("breadth_score", "specialization_score", "applied_learning_score", "research_depth_score", "continuing_learning_score", "transition_pressure_score"):
        assert 0.0 <= result[key] <= 1.0


def test_trajectory_and_near_term_direction_are_explicit():
    result = analyze_education_learning_trajectory_v1(_chart(), NOW)
    assert result["trajectory_pattern"]
    assert result["near_term_direction"]
    assert result["timing_available"] is True
    assert result["events_available"] is True


def test_known_education_history_overrides_astrology():
    result = analyze_education_learning_trajectory_v1(_chart(), NOW)
    rule = result["historical_validation"]["rule"].lower()
    assert "known education" in rule
    assert "must not create" in rule


def test_timezone_is_required():
    with pytest.raises(ValueError, match="timezone"):
        analyze_education_learning_trajectory_v1(_chart(), datetime(2026, 8, 21))


def test_outcome_guarantees_remain_disallowed():
    result = analyze_education_learning_trajectory_v1(_chart(), NOW)
    text = result["limitation"].lower()
    assert "does not guarantee" in text
    assert "exam results" in text
    assert "graduation" in text
    assert "employment" in text
