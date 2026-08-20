from datetime import datetime, timezone

from app.astrology.features.finance_period_intelligence_v2 import (
    analyze_finance_period_v2,
    extract_finance_period_request_v2,
)


def _chart():
    return {
        "houses": {
            "2": {"lord": "Jupiter", "sign": "Taurus"},
            "5": {"lord": "Mercury", "sign": "Leo"},
            "8": {"lord": "Venus", "sign": "Libra"},
            "9": {"lord": "Saturn", "sign": "Capricorn"},
            "10": {"lord": "Saturn", "sign": "Aquarius"},
            "11": {"lord": "Jupiter", "sign": "Pisces"},
        },
        "planets": {
            "Jupiter": {"house": 11},
            "Mercury": {"house": 5},
            "Venus": {"house": 2},
            "Saturn": {"house": 9},
        },
        "dasha_periods": [
            {"start": "2023-01-01T00:00:00+00:00", "end": "2025-01-01T00:00:00+00:00", "major_lord": "Mars", "sub_lord": "Rahu"},
            {"start": "2025-01-01T00:00:00+00:00", "end": "2028-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Mercury"},
            {"start": "2028-01-01T00:00:00+00:00", "end": "2031-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Venus"},
        ],
    }


def test_extract_single_year():
    result = extract_finance_period_request_v2("How will 2027 be financially?")
    assert result["request_type"] == "single_year"
    assert result["years"] == [2027]


def test_extract_year_comparison():
    result = extract_finance_period_request_v2("Which is better for money growth, 2027 or 2028?")
    assert result["request_type"] == "year_comparison"
    assert result["years"] == [2027, 2028]


def test_extract_year_range():
    result = extract_finance_period_request_v2("How are my finances from 2028 to 2030?")
    assert result["request_type"] == "year_range"
    assert result["years"] == [2028, 2029, 2030]


def test_past_future_comparison_is_supported():
    result = analyze_finance_period_v2(
        _chart(),
        "Was 2023 stronger financially than 2026?",
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["available"] is True
    assert result["request"]["request_type"] == "year_comparison"
    assert {item["year"] for item in result["year_results"]} == {2023, 2026}
    assert result["comparison"] is not None


def test_range_identifies_strongest_year():
    result = analyze_finance_period_v2(
        _chart(),
        "How are my finances from 2027 to 2029?",
        datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert result["available"] is True
    assert len(result["year_results"]) == 3
    assert result["strongest_year"]["year"] in {2027, 2028, 2029}


def test_open_ended_question_is_left_for_v1_timing():
    result = extract_finance_period_request_v2("When will my finances improve?")
    assert result["available"] is False
    assert result["request_type"] == "open_ended"
