from datetime import datetime, timezone

import pytest

from app.astrology.features.health_wellbeing_trajectory_v1 import analyze_health_wellbeing_trajectory_v1

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {
            "1": {"lord": "Sun"},
            "6": {"lord": "Mercury"},
            "8": {"lord": "Saturn"},
            "12": {"lord": "Jupiter"},
        },
        "planets": {
            "Sun": {"house": 1},
            "Moon": {"house": 4},
            "Mars": {"house": 6},
            "Saturn": {"house": 8},
            "Jupiter": {"house": 12},
            "Mercury": {"house": 6},
            "Venus": {"house": 12},
        },
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Sun", "sub_lord": "Mercury"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Moon"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Venus"},
        ],
    }


def test_trajectory_scores_are_bounded():
    result = analyze_health_wellbeing_trajectory_v1(_chart(), NOW)
    assert result["available"] is True
    for key in (
        "energy_management_score",
        "routine_consistency_score",
        "resilience_habits_score",
        "stress_balance_score",
        "rest_restoration_score",
        "preventive_self_care_score",
        "adaptability_score",
    ):
        assert 0.0 <= result[key] <= 1.0
    assert result["trajectory_pattern"]
    assert result["near_term_direction"]


def test_trajectory_uses_lower_layers():
    result = analyze_health_wellbeing_trajectory_v1(_chart(), NOW)
    assert result["timing_available"] is True
    assert result["events_available"] is True
    assert set(result["components"]) == {"natal", "timing", "events"}


def test_reality_override_preserves_medical_reality():
    rule = analyze_health_wellbeing_trajectory_v1(_chart(), NOW)["historical_validation"]["rule"].lower()
    assert "medical history" in rule
    assert "clinician advice override" in rule
    assert "must not manufacture" in rule
    assert "illness" in rule and "recovery" in rule


def test_medical_predictions_and_recommendations_are_disallowed():
    text = analyze_health_wellbeing_trajectory_v1(_chart(), NOW)["limitation"].lower()
    assert "diagnose" in text and "disease" in text
    assert "prognosis" in text and "lifespan" in text and "death" in text
    assert "treatment response" in text and "recovery outcomes" in text
    assert "medication" in text and "tests" in text and "supplements" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_health_wellbeing_trajectory_v1(_chart(), datetime(2026, 8, 23))
