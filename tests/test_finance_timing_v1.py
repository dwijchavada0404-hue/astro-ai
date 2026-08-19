from datetime import datetime, timezone

import pytest

from app.astrology.features.finance_timing_v1 import analyze_finance_timing_v1


def _chart():
    return {
        "houses": {
            "2": {"lord": "Mercury"},
            "5": {"lord": "Venus"},
            "8": {"lord": "Jupiter"},
            "9": {"lord": "Saturn"},
            "10": {"lord": "Saturn"},
            "11": {"lord": "Jupiter"},
        },
        "planets": {
            "Mercury": {"house": 11},
            "Venus": {"house": 5},
            "Jupiter": {"house": 9},
            "Saturn": {"house": 2},
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
                "sub_lord": "Venus",
            },
            {
                "start": "2027-01-01T00:00:00+00:00",
                "end": "2030-12-31T23:59:59+00:00",
                "major_lord": "Jupiter",
                "sub_lord": "Venus",
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
                        "planet": "Venus",
                        "start": "2025-01-01T00:00:00+00:00",
                        "end": "2028-12-31T23:59:59+00:00",
                    },
                ],
            },
            {
                "planet": "Jupiter",
                "start": "2029-01-01T00:00:00+00:00",
                "end": "2034-12-31T23:59:59+00:00",
                "antardashas": [
                    {
                        "planet": "Jupiter",
                        "start": "2029-01-01T00:00:00+00:00",
                        "end": "2032-12-31T23:59:59+00:00",
                    }
                ],
            },
        ]
    }
    return chart


def test_finance_timing_returns_past_present_future():
    result = analyze_finance_timing_v1(
        _chart(),
        datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc),
    )
    assert result["available"] is True
    assert result["past"]["available"] is True
    assert result["present"]["available"] is True
    assert result["future"]["available"] is True
    assert result["future"]["strongest_period"]["major_lord"] == "Jupiter"
    assert result["comparison"]["result"] in {"future_stronger", "past_stronger", "similar_strength"}


def test_finance_timing_supports_nested_production_dashas():
    result = analyze_finance_timing_v1(
        _nested_chart(),
        datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc),
    )
    assert result["available"] is True
    assert result["present"]["active_period"]["major_lord"] == "Saturn"
    assert result["present"]["active_period"]["sub_lord"] == "Venus"
    assert result["future"]["available"] is True


def test_finance_timing_does_not_promise_returns():
    result = analyze_finance_timing_v1(
        _chart(),
        datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc),
    )
    text = (result["answer"] + " " + result["limitation"]).lower()
    assert "guarantee" in text
    assert "financial advice" in text


def test_finance_timing_requires_timezone():
    with pytest.raises(ValueError):
        analyze_finance_timing_v1(_chart(), datetime(2026, 8, 20, 0, 0))


def test_finance_timing_handles_missing_dashas():
    chart = _chart()
    chart.pop("dasha_periods")
    result = analyze_finance_timing_v1(
        chart,
        datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc),
    )
    assert result["available"] is False
    assert "dasha" in result["reason"].lower()
