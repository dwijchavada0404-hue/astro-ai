from datetime import datetime, timezone

import pytest

from app.astrology.features.health_wellbeing_event_intelligence_v1 import analyze_health_wellbeing_event_intelligence_v1

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {
            "1": {"lord": "Sun"},
            "6": {"lord": "Mercury"},
            "8": {"lord": "Mars"},
            "12": {"lord": "Moon"},
        },
        "planets": {
            "Sun": {"house": 1},
            "Mercury": {"house": 6},
            "Mars": {"house": 3},
            "Moon": {"house": 12},
            "Saturn": {"house": 10},
            "Jupiter": {"house": 9},
            "Venus": {"house": 5},
        },
        "dasha_periods": [
            {"start": "2025-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Sun", "sub_lord": "Mars"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Moon", "sub_lord": "Mercury"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2029-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Saturn"},
        ],
    }


def test_event_scores_are_bounded_and_symbolic():
    result = analyze_health_wellbeing_event_intelligence_v1(_chart(), NOW)
    assert result["available"] is True
    assert result["strongest_event"] in result["events"]
    for event in result["events"].values():
        assert 0.0 <= event["score"] <= 1.0
        assert event["status"] == "symbolic_theme_only"


def test_events_cover_non_medical_wellbeing_themes():
    result = analyze_health_wellbeing_event_intelligence_v1(_chart(), NOW)
    assert set(result["events"]) == {
        "energy_pacing_focus",
        "routine_reset_focus",
        "resilience_development_focus",
        "stress_balance_focus",
        "rest_restoration_focus",
        "preventive_self_care_focus",
    }


def test_historical_validation_does_not_invent_illness_or_recovery():
    rule = analyze_health_wellbeing_event_intelligence_v1(_chart(), NOW)["historical_validation"]["rule"].lower()
    assert "override astrology" in rule
    assert "illness" in rule and "injury" in rule
    assert "recovery occurred" in rule


def test_medical_prediction_and_treatment_advice_are_disallowed():
    text = analyze_health_wellbeing_event_intelligence_v1(_chart(), NOW)["limitation"].lower()
    assert "diagnose" in text and "disease" in text
    assert "prognosis" in text and "lifespan" in text and "death" in text
    assert "treatment response" in text and "recovery outcomes" in text
    assert "medication" in text and "tests" in text and "supplements" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_health_wellbeing_event_intelligence_v1(_chart(), datetime(2026, 8, 23))
