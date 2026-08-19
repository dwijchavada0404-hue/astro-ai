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
