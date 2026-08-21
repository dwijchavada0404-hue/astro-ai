from datetime import datetime, timezone

import pytest

from app.astrology.features.career_trajectory_v1 import analyze_career_trajectory_v1


def _chart():
    return {
        "houses": {
            "1": {"lord": "Sun", "sign": "Leo"},
            "2": {"lord": "Mercury", "sign": "Virgo"},
            "3": {"lord": "Mars", "sign": "Aries"},
            "6": {"lord": "Saturn", "sign": "Capricorn"},
            "7": {"lord": "Venus", "sign": "Libra"},
            "9": {"lord": "Jupiter", "sign": "Sagittarius"},
            "10": {"lord": "Saturn", "sign": "Capricorn", "occupants": ["Mercury"]},
            "11": {"lord": "Mercury", "sign": "Gemini"},
            "12": {"lord": "Jupiter", "sign": "Pisces"},
        },
        "planets": {
            "Sun": {"house": 11, "sign": "Gemini"},
            "Mercury": {"house": 10, "sign": "Capricorn"},
            "Mars": {"house": 3, "sign": "Aries"},
            "Jupiter": {"house": 9, "sign": "Sagittarius"},
            "Venus": {"house": 7, "sign": "Libra"},
            "Saturn": {"house": 10, "sign": "Capricorn"},
            "Rahu": {"house": 12, "sign": "Pisces"},
        },
        "dashas": {
            "mahadashas": [
                {
                    "planet": "Saturn",
                    "start": "2021-01-01T00:00:00+00:00",
                    "end": "2028-12-31T23:59:59+00:00",
                    "antardashas": [
                        {"planet": "Mercury", "start": "2021-01-01T00:00:00+00:00", "end": "2024-12-31T23:59:59+00:00"},
                        {"planet": "Mars", "start": "2025-01-01T00:00:00+00:00", "end": "2028-12-31T23:59:59+00:00"},
                    ],
                },
                {
                    "planet": "Mercury",
                    "start": "2029-01-01T00:00:00+00:00",
                    "end": "2034-12-31T23:59:59+00:00",
                    "antardashas": [
                        {"planet": "Saturn", "start": "2029-01-01T00:00:00+00:00", "end": "2032-12-31T23:59:59+00:00"}
                    ],
                },
            ]
        },
    }


def test_trajectory_returns_bounded_scores_and_pattern():
    result = analyze_career_trajectory_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["available"] is True
    assert result["event"] == "career_trajectory"
    assert result["trajectory_pattern"]
    assert result["near_term_direction"]
    for key in (
        "progression_score",
        "stability_score",
        "mobility_score",
        "challenge_score",
        "resilience_score",
        "recovery_score",
    ):
        assert 0.0 <= result[key] <= 1.0


def test_trajectory_includes_event_context_and_orientation():
    result = analyze_career_trajectory_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["job_business_orientation"] in {"structured_employment", "independent_business", "mixed_hybrid"}
    assert "future_promotion_score" in result["event_context"]
    assert "future_challenge_score" in result["event_context"]


def test_trajectory_has_resilience_evidence():
    result = analyze_career_trajectory_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["resilience_score"] > 0
    assert result["evidence"]["resilience"]


def test_trajectory_preserves_historical_validation_boundary():
    result = analyze_career_trajectory_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert "must remain unconfirmed" in result["historical_rule"].lower()
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "do not predict termination" in text


def test_trajectory_requires_timezone():
    with pytest.raises(ValueError):
        analyze_career_trajectory_v1(_chart(), datetime(2026, 8, 20))


def test_trajectory_handles_missing_foundation():
    result = analyze_career_trajectory_v1(
        {"houses": {}, "planets": {}},
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["available"] is False
