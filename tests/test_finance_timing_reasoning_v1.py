from datetime import datetime, timezone

import pytest

from app.astrology.features.finance_timing_reasoning_v1 import (
    analyze_finance_timing_v1,
    score_finance_moment_v1,
)


@pytest.fixture
def chart():
    return {
        "houses": {
            "2": {"lord": "Mercury"},
            "5": {"lord": "Venus"},
            "8": {"lord": "Jupiter"},
            "9": {"lord": "Saturn"},
            "11": {"lord": "Jupiter"},
        },
        "planets": {
            "Mercury": {"house": 10},
            "Venus": {"house": 11},
            "Jupiter": {"house": 2},
            "Saturn": {"house": 9},
        },
        "dasha_periods": [
            {"start": "2021-01-01T00:00:00+00:00", "end": "2024-12-31T23:59:59+00:00", "major": "Venus", "sub": "Mercury"},
            {"start": "2025-01-01T00:00:00+00:00", "end": "2028-12-31T23:59:59+00:00", "major": "Jupiter", "sub": "Saturn"},
            {"start": "2029-01-01T00:00:00+00:00", "end": "2032-12-31T23:59:59+00:00", "major": "Mars", "sub": "Moon"},
        ],
        "transit_snapshots": {
            "2023": {
                "Jupiter": {"house": 11},
                "Venus": {"house": 2},
                "Mercury": {"house": 10},
                "Saturn": {"house": 9},
            },
            "2026": {
                "Jupiter": {"house": 9},
                "Venus": {"house": 11},
                "Mercury": {"house": 6},
                "Saturn": {"house": 10},
            },
            "2027": {
                "Jupiter": {"house": 11},
                "Venus": {"house": 10},
                "Mercury": {"house": 2},
                "Saturn": {"house": 9},
            },
        },
    }


def test_score_finance_moment_returns_components(chart):
    result = score_finance_moment_v1(chart, datetime(2026, 8, 20, tzinfo=timezone.utc))
    assert result["available"] is True
    assert 0.0 <= result["score"] <= 1.0
    assert set(result["components"]) == {"natal", "dasha", "transit"}


def test_finance_timing_has_past_present_future(chart):
    result = analyze_finance_timing_v1(
        chart,
        datetime(2026, 8, 20, tzinfo=timezone.utc),
        lookback_years=5,
        lookahead_years=5,
        step_days=30,
    )
    assert result["available"] is True
    assert result["past"]["available"] is True
    assert result["present"]["available"] is True
    assert result["future"]["available"] is True
    assert result["comparison"]["result"] in {
        "similar_strength", "future_stronger", "past_stronger", "future_only", "past_only"
    }


def test_no_dasha_or_transit_data_is_neutral_not_failure(chart):
    stripped = {"houses": chart["houses"], "planets": chart["planets"]}
    result = score_finance_moment_v1(stripped, datetime(2026, 8, 20, tzinfo=timezone.utc))
    assert result["available"] is True
    assert result["components"]["dasha"] == 0.5
    assert result["components"]["transit"] == 0.5


def test_naive_datetime_rejected(chart):
    with pytest.raises(ValueError):
        score_finance_moment_v1(chart, datetime(2026, 8, 20))


def test_invalid_horizon_rejected(chart):
    with pytest.raises(ValueError):
        analyze_finance_timing_v1(
            chart,
            datetime(2026, 8, 20, tzinfo=timezone.utc),
            lookback_years=0,
        )


def test_finance_timing_contains_non_advice_limitation(chart):
    result = analyze_finance_timing_v1(chart, datetime(2026, 8, 20, tzinfo=timezone.utc))
    limitation = result["limitation"].lower()
    assert "not financial advice" in limitation
    assert "does not guarantee" in limitation
