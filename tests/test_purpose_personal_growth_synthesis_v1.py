from datetime import datetime, timezone

import pytest

from app.astrology.features.purpose_personal_growth_synthesis_v1 import analyze_purpose_personal_growth_synthesis_v1

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


def test_synthesis_scores_and_confidence_are_bounded():
    result = analyze_purpose_personal_growth_synthesis_v1(_chart(), NOW)
    assert result["available"] is True
    assert 0.0 <= result["confidence"] <= 1.0
    assert 0.0 <= result["component_coverage"] <= 1.0
    assert all(0.0 <= score <= 1.0 for score in result["scores"].values())


def test_synthesis_exposes_outlook_and_strongest_area():
    result = analyze_purpose_personal_growth_synthesis_v1(_chart(), NOW)
    assert result["outlook"]
    assert result["strongest_area"] in result["scores"]
    assert result["strongest_future_period"] is not None


def test_reality_override_prevents_manufactured_calling():
    result = analyze_purpose_personal_growth_synthesis_v1(_chart(), NOW)
    rule = result["historical_validation"]["rule"].lower()
    assert "known values" in rule
    assert "must never manufacture" in rule
    assert "calling" in rule


def test_fixed_destiny_and_spiritual_status_are_disallowed():
    result = analyze_purpose_personal_growth_synthesis_v1(_chart(), NOW)
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "not a fixed destiny" in text
    assert "cannot determine a fixed life purpose" in text
    assert "spiritual status" in text
    assert "personal values" in text


def test_timezone_is_required():
    with pytest.raises(ValueError, match="timezone"):
        analyze_purpose_personal_growth_synthesis_v1(_chart(), datetime(2026, 8, 21))
