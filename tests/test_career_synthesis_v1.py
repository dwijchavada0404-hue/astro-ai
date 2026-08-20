from datetime import datetime, timezone

import pytest

from app.astrology.features.career_synthesis_v1 import analyze_career_synthesis_v1


def _chart():
    return {
        "houses": {
            "1": {"lord": "Sun", "sign": "Leo"},
            "2": {"lord": "Mercury", "sign": "Virgo"},
            "3": {"lord": "Mars", "sign": "Aries"},
            "5": {"lord": "Mercury", "sign": "Gemini"},
            "6": {"lord": "Saturn", "sign": "Capricorn"},
            "7": {"lord": "Venus", "sign": "Libra"},
            "8": {"lord": "Jupiter", "sign": "Pisces"},
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


def test_synthesis_combines_all_career_layers():
    result = analyze_career_synthesis_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["available"] is True
    assert result["event"] == "career_synthesis"
    assert set(result["components"]) == {
        "natal",
        "direction",
        "job_vs_business",
        "timing",
        "events",
        "trajectory",
    }
    assert all(result["component_availability"].values())


def test_synthesis_scores_and_confidence_are_bounded():
    result = analyze_career_synthesis_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert 0.0 <= result["career_development_score"] <= 1.0
    assert result["career_development_outlook"] in {"strong", "moderate", "limited"}
    assert 0.0 <= result["confidence"] <= 1.0
    assert 0.0 <= result["future_challenge_score"] <= 1.0
    assert 0.0 <= result["strongest_future_event_score"] <= 1.0


def test_synthesis_exposes_direction_orientation_timing_and_trajectory():
    result = analyze_career_synthesis_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["primary_direction"] is not None
    assert result["primary_direction_label"]
    assert result["primary_environment"] is not None
    assert result["job_business_orientation"] in {
        "structured_employment",
        "independent_business",
        "mixed_hybrid",
    }
    assert result["trajectory_pattern"]
    assert result["near_term_direction"]
    assert result["active_present_period"] is not None
    assert result["strongest_future_period"] is not None


def test_synthesis_separates_future_opportunity_from_challenge():
    result = analyze_career_synthesis_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["strongest_future_event"] in {
        "promotion",
        "job_change",
        "new_job",
        "foreign_work",
    }
    assert result["strongest_future_event"] != "job_loss_challenge"
    assert "future_challenge_score" in result


def test_synthesis_preserves_reality_override_for_past_events():
    result = analyze_career_synthesis_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    historical = result["historical_validation"]
    assert historical["status"] == "unconfirmed"
    assert historical["reality_override"] is True
    assert "known career history overrides predictive assumptions" in historical["rule"].lower()
    assert "unless the user" in historical["rule"].lower()


def test_synthesis_language_is_non_deterministic():
    result = analyze_career_synthesis_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "does not guarantee employment" in text
    assert "predictions of termination" in text
    assert "professional career advice" in text


def test_synthesis_requires_timezone():
    with pytest.raises(ValueError):
        analyze_career_synthesis_v1(_chart(), datetime(2026, 8, 20))


def test_synthesis_handles_missing_foundation():
    result = analyze_career_synthesis_v1(
        {"houses": {}, "planets": {}},
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["available"] is False
