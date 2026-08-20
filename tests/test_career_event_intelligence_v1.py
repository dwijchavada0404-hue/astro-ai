from datetime import datetime, timezone

import pytest

from app.astrology.features.career_event_intelligence_v1 import analyze_career_event_intelligence_v1


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
            "Mars": {"house": 12, "sign": "Aries"},
            "Jupiter": {"house": 12, "sign": "Pisces"},
            "Venus": {"house": 11, "sign": "Pisces"},
            "Saturn": {"house": 12, "sign": "Aries"},
            "Rahu": {"house": 9, "sign": "Sagittarius"},
        },
        "dashas": {
            "mahadashas": [
                {
                    "planet": "Saturn",
                    "start": "2021-01-01T00:00:00+00:00",
                    "end": "2028-12-31T23:59:59+00:00",
                    "antardashas": [
                        {
                            "planet": "Mercury",
                            "start": "2021-01-01T00:00:00+00:00",
                            "end": "2024-12-31T23:59:59+00:00",
                        },
                        {
                            "planet": "Mars",
                            "start": "2025-01-01T00:00:00+00:00",
                            "end": "2028-12-31T23:59:59+00:00",
                        },
                    ],
                },
                {
                    "planet": "Mercury",
                    "start": "2029-01-01T00:00:00+00:00",
                    "end": "2034-12-31T23:59:59+00:00",
                    "antardashas": [
                        {
                            "planet": "Saturn",
                            "start": "2029-01-01T00:00:00+00:00",
                            "end": "2032-12-31T23:59:59+00:00",
                        }
                    ],
                },
            ]
        },
    }


def test_event_intelligence_returns_required_career_events():
    result = analyze_career_event_intelligence_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["available"] is True
    assert set(result["events"]) == {
        "promotion",
        "job_change",
        "new_job",
        "job_loss_challenge",
        "foreign_work",
    }
    for event in result["events"].values():
        assert 0.0 <= event["past"]["score"] <= 1.0
        assert 0.0 <= event["present"]["score"] <= 1.0
        assert 0.0 <= event["future"]["score"] <= 1.0


def test_new_job_is_distinct_from_generic_job_change():
    result = analyze_career_event_intelligence_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    new_job = result["events"]["new_job"]
    job_change = result["events"]["job_change"]
    assert new_job["employment_support"] is not None
    assert job_change["employment_support"] is None


def test_event_engine_uses_event_specific_dasha_timing():
    result = analyze_career_event_intelligence_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["event_specific_timing_available"] is True
    assert result["events"]["promotion"]["present"]["event_specific_period"] is not None
    assert result["events"]["job_change"]["future"]["event_specific_period"] is not None


def test_past_events_remain_unconfirmed():
    result = analyze_career_event_intelligence_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["historical_validation"]["status"] == "unconfirmed"
    assert "must not state" in result["historical_validation"]["rule"].lower()
    for event in result["events"].values():
        assert event["past"]["historical_status"] == "unconfirmed"


def test_job_loss_language_is_bounded():
    result = analyze_career_event_intelligence_v1(
        _chart(),
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "not the probability" in text
    assert "must not be presented as a prediction of termination" in text


def test_event_intelligence_requires_timezone():
    with pytest.raises(ValueError):
        analyze_career_event_intelligence_v1(_chart(), datetime(2026, 8, 20))


def test_event_intelligence_handles_missing_foundation():
    result = analyze_career_event_intelligence_v1(
        {"houses": {}, "planets": {}},
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["available"] is False
