from datetime import datetime, timezone

import pytest

from app.astrology.features.career_timing_v1 import analyze_career_timing_v1


def _chart():
    return {
        "houses": {
            "1": {"lord": "Sun"},
            "2": {"lord": "Mercury"},
            "3": {"lord": "Mars"},
            "6": {"lord": "Saturn"},
            "7": {"lord": "Venus"},
            "9": {"lord": "Jupiter"},
            "10": {"lord": "Saturn"},
            "11": {"lord": "Mercury"},
            "12": {"lord": "Jupiter"},
        },
        "planets": {
            "Sun": {"house": 10},
            "Mercury": {"house": 11},
            "Mars": {"house": 3},
            "Jupiter": {"house": 9},
            "Venus": {"house": 7},
            "Saturn": {"house": 10},
            "Rahu": {"house": 12},
        },
        "dasha_periods": [
            {
                "start": "2021-01-01T00:00:00+00:00",
                "end": "2023-12-31T23:59:59+00:00",
                "major_lord": "Jupiter",
                "sub_lord": "Mercury",
            },
            {
                "start": "2024-01-01T00:00:00+00:00",
                "end": "2026-12-31T23:59:59+00:00",
                "major_lord": "Saturn",
                "sub_lord": "Mars",
            },
            {
                "start": "2027-01-01T00:00:00+00:00",
                "end": "2031-12-31T23:59:59+00:00",
                "major_lord": "Mercury",
                "sub_lord": "Saturn",
            },
        ],
    }


def _nested_chart():
    chart = _chart()
    chart.pop("dasha_periods")
    chart["dashas"] = {
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
    }
    return chart


def test_career_timing_returns_past_present_future():
    result = analyze_career_timing_v1(
        _chart(),
        datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc),
    )
    assert result["available"] is True
    assert result["event"] == "career_timing"
    assert result["past"]["available"] is True
    assert result["present"]["available"] is True
    assert result["future"]["available"] is True
    assert 0.0 <= result["present"]["active_period"]["career_support_score"] <= 1.0
    assert 0.0 <= result["present"]["active_period"]["transition_score"] <= 1.0
    assert result["comparison"]["result"] in {"future_stronger", "past_stronger", "similar_strength"}


def test_career_timing_supports_nested_production_dashas():
    result = analyze_career_timing_v1(
        _nested_chart(),
        datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc),
    )
    assert result["available"] is True
    assert result["present"]["active_period"]["major_lord"] == "Saturn"
    assert result["present"]["active_period"]["sub_lord"] == "Mars"
    assert result["future"]["available"] is True


def test_historical_validation_never_claims_event_occurred():
    result = analyze_career_timing_v1(
        _chart(),
        datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc),
    )
    historical = result["historical_validation"]
    assert historical["status"] == "unconfirmed"
    assert "must not claim" in historical["rule"].lower()
    assert "unless the user confirms" in historical["rule"].lower()
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "does not establish that a past event happened" in text


def test_career_timing_requires_timezone():
    with pytest.raises(ValueError):
        analyze_career_timing_v1(_chart(), datetime(2026, 8, 20, 0, 0))


def test_career_timing_handles_missing_dashas():
    chart = _chart()
    chart.pop("dasha_periods")
    result = analyze_career_timing_v1(
        chart,
        datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc),
    )
    assert result["available"] is False
    assert "dasha" in result["reason"].lower()


def test_career_timing_input_validation():
    with pytest.raises(ValueError):
        analyze_career_timing_v1([], datetime(2026, 8, 20, tzinfo=timezone.utc))  # type: ignore[arg-type]
