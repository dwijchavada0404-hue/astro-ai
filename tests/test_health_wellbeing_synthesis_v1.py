from datetime import datetime, timezone

import pytest

from app.astrology.features.health_wellbeing_synthesis_v1 import analyze_health_wellbeing_synthesis_v1

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"1": {"lord": "Sun"}, "6": {"lord": "Mercury"}, "8": {"lord": "Saturn"}, "12": {"lord": "Jupiter"}},
        "planets": {"Sun": {"house": 1}, "Moon": {"house": 4}, "Mars": {"house": 6}, "Saturn": {"house": 8}, "Jupiter": {"house": 12}, "Mercury": {"house": 6}, "Venus": {"house": 12}},
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Sun", "sub_lord": "Mercury"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Moon"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Venus"},
        ],
    }


def test_synthesis_scores_confidence_and_coverage_are_bounded():
    result = analyze_health_wellbeing_synthesis_v1(_chart(), NOW)
    assert result["available"] is True
    assert 0.0 <= result["confidence"] <= 1.0
    assert 0.0 <= result["component_coverage"] <= 1.0
    assert all(0.0 <= score <= 1.0 for score in result["scores"].values())


def test_synthesis_exposes_outlook_and_future_context():
    result = analyze_health_wellbeing_synthesis_v1(_chart(), NOW)
    assert result["outlook"]
    assert result["strongest_area"] in result["scores"]
    assert result["strongest_future_period"] is not None
    assert result["strongest_future_event"] is not None


def test_reality_override_preserves_medical_reality():
    rule = analyze_health_wellbeing_synthesis_v1(_chart(), NOW)["historical_validation"]["rule"].lower()
    assert "medical history" in rule
    assert "clinician advice override" in rule
    assert "must never manufacture" in rule
    assert "illness" in rule and "recovery" in rule


def test_medical_predictions_and_recommendations_are_disallowed():
    text = analyze_health_wellbeing_synthesis_v1(_chart(), NOW)["limitation"].lower()
    assert "non-medical" in text
    assert "diagnose" in text and "disease" in text
    assert "prognosis" in text and "lifespan" in text and "death" in text
    assert "fertility" in text and "treatment response" in text
    assert "medication" in text and "tests" in text and "supplements" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_health_wellbeing_synthesis_v1(_chart(), datetime(2026, 8, 23))
