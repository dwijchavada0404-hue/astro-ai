from datetime import datetime, timezone

from app.astrology.features.finance_challenges_recovery_v1 import analyze_finance_challenges_recovery_v1


def _chart():
    return {
        "houses": {
            "2": {"lord": "Venus"},
            "4": {"lord": "Sun"},
            "5": {"lord": "Mercury"},
            "6": {"lord": "Mars"},
            "8": {"lord": "Jupiter"},
            "9": {"lord": "Saturn"},
            "10": {"lord": "Saturn"},
            "11": {"lord": "Jupiter"},
            "12": {"lord": "Mars"},
        },
        "planets": {
            "Venus": {"house": 2},
            "Sun": {"house": 4},
            "Mercury": {"house": 5},
            "Jupiter": {"house": 11},
            "Saturn": {"house": 10},
            "Mars": {"house": 8},
            "Rahu": {"house": 5},
            "Ketu": {"house": 12},
        },
        "dasha_periods": [
            {"start": "2022-01-01T00:00:00+00:00", "end": "2025-01-01T00:00:00+00:00", "major_lord": "Mars", "sub_lord": "Rahu"},
            {"start": "2025-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Mercury"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Venus"},
        ],
    }


def test_returns_challenge_profile_and_recovery_scan():
    result = analyze_finance_challenges_recovery_v1(
        _chart(), datetime(2026, 8, 20, tzinfo=timezone.utc)
    )
    assert result["available"] is True
    assert result["event"] == "finance_challenges_recovery"
    assert result["primary_challenge"] in result["challenge_scores"]
    assert 0.0 <= result["primary_challenge_score"] <= 1.0
    assert result["current_state"] in {
        "recovery_or_expansion_support",
        "mixed_or_stabilising",
        "higher_financial_pressure",
        "timing_unavailable",
    }
    assert result["recovery_outlook"] in {
        "strong_recovery_support_ahead",
        "moderate_recovery_support_ahead",
        "limited_recovery_support_in_scan",
        "timing_unavailable",
    }


def test_finance_house_nodes_raise_speculative_volatility():
    result = analyze_finance_challenges_recovery_v1(
        _chart(), datetime(2026, 8, 20, tzinfo=timezone.utc)
    )
    assert result["challenge_scores"]["speculative_volatility"] >= 0.18


def test_missing_dasha_keeps_natal_challenge_analysis_available():
    chart = _chart()
    chart.pop("dasha_periods")
    result = analyze_finance_challenges_recovery_v1(
        chart, datetime(2026, 8, 20, tzinfo=timezone.utc)
    )
    assert result["available"] is True
    assert result["current_state"] == "timing_unavailable"
    assert result["recovery_outlook"] == "timing_unavailable"


def test_missing_natal_data_returns_unavailable():
    result = analyze_finance_challenges_recovery_v1(
        {"houses": {}, "planets": {}}, datetime(2026, 8, 20, tzinfo=timezone.utc)
    )
    assert result["available"] is False


def test_timezone_required():
    try:
        analyze_finance_challenges_recovery_v1(_chart(), datetime(2026, 8, 20))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
