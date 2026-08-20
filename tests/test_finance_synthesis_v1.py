from datetime import datetime, timezone

from app.astrology.features.finance_synthesis_v1 import analyze_finance_synthesis_v1


def _chart():
    return {
        "houses": {
            "2": {"lord": "Venus"}, "4": {"lord": "Sun"}, "5": {"lord": "Mercury"},
            "6": {"lord": "Venus"}, "8": {"lord": "Jupiter"}, "9": {"lord": "Saturn"},
            "10": {"lord": "Saturn"}, "11": {"lord": "Jupiter"}, "12": {"lord": "Mars"},
        },
        "planets": {
            "Venus": {"house": 2}, "Sun": {"house": 4}, "Mercury": {"house": 5},
            "Jupiter": {"house": 11}, "Saturn": {"house": 10}, "Mars": {"house": 3},
            "Rahu": {"house": 6}, "Ketu": {"house": 12},
        },
        "dasha_periods": [
            {"start": "2023-01-01T00:00:00+00:00", "end": "2025-01-01T00:00:00+00:00", "major_lord": "Mars", "sub_lord": "Rahu"},
            {"start": "2025-01-01T00:00:00+00:00", "end": "2028-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Mercury"},
            {"start": "2028-01-01T00:00:00+00:00", "end": "2031-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Venus"},
        ],
    }


def test_synthesis_combines_all_finance_dimensions():
    result = analyze_finance_synthesis_v1(_chart(), datetime(2026, 8, 20, tzinfo=timezone.utc))
    assert result["available"] is True
    assert result["event"] == "finance_synthesis"
    assert result["wealth_building_outlook"] in {"strong", "moderate", "limited"}
    assert result["primary_wealth_source"] is not None
    assert result["accumulation_pattern"] is not None
    assert result["primary_financial_challenge"] is not None
    assert result["current_timing_outlook"] in {"strong", "moderate", "limited", "timing unavailable"}
    assert set(result["components"]) == {
        "natal", "source_of_wealth", "trajectory", "timing", "challenges_recovery"
    }


def test_synthesis_exposes_past_and_future_windows():
    result = analyze_finance_synthesis_v1(_chart(), datetime(2026, 8, 20, tzinfo=timezone.utc))
    assert "strongest_past_window" in result
    assert "strongest_future_window" in result


def test_synthesis_preserves_financial_safety_boundary():
    result = analyze_finance_synthesis_v1(_chart(), datetime(2026, 8, 20, tzinfo=timezone.utc))
    limitation = result["limitation"].lower()
    assert "not financial advice" in limitation
    assert "guarantee" in limitation


def test_missing_finance_foundation_is_unavailable():
    result = analyze_finance_synthesis_v1(
        {"houses": {}, "planets": {}}, datetime(2026, 8, 20, tzinfo=timezone.utc)
    )
    assert result["available"] is False


def test_timezone_is_required():
    try:
        analyze_finance_synthesis_v1(_chart(), datetime(2026, 8, 20))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
