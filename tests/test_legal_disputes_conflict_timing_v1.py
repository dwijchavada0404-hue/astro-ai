from datetime import datetime, timezone

import pytest

from app.astrology.features.legal_disputes_conflict_timing_v1 import analyze_legal_disputes_conflict_timing_v1

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {
            "6": {"lord": "Mercury"},
            "7": {"lord": "Venus"},
            "8": {"lord": "Saturn"},
            "9": {"lord": "Jupiter"},
        },
        "planets": {
            "Mars": {"house": 6},
            "Saturn": {"house": 8},
            "Mercury": {"house": 7},
            "Jupiter": {"house": 9},
            "Sun": {"house": 10},
            "Rahu": {"house": 6},
            "Ketu": {"house": 12},
            "Venus": {"house": 7},
        },
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mars", "sub_lord": "Saturn"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Jupiter"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Venus"},
        ],
    }


def test_timing_separates_past_present_future_and_bounds_scores():
    result = analyze_legal_disputes_conflict_timing_v1(_chart(), NOW)
    assert result["available"] is True
    assert result["past"]["strongest_period"] is not None
    assert result["present"]["active_period"] is not None
    assert result["future"]["strongest_period"] is not None
    for phase, key in (("past", "strongest_period"), ("present", "active_period"), ("future", "strongest_period")):
        period = result[phase][key]
        for score_key in (
            "dispute_activation_score",
            "negotiation_support_score",
            "complexity_endurance_score",
            "principles_fairness_score",
            "competition_assertiveness_score",
            "resolution_support_score",
            "overall_activation_score",
        ):
            assert 0.0 <= period[score_key] <= 1.0


def test_historical_activation_is_unconfirmed_and_reality_overrides():
    result = analyze_legal_disputes_conflict_timing_v1(_chart(), NOW)
    assert result["past"]["historical_status"] == "unconfirmed"
    rule = result["historical_validation"]["rule"].lower()
    assert "known legal history" in rule
    assert "not proof" in rule


def test_verdict_criminal_regulatory_and_amount_predictions_are_disallowed():
    text = analyze_legal_disputes_conflict_timing_v1(_chart(), NOW)["limitation"].lower()
    for phrase in ("guilt", "liability", "court verdicts", "arrest", "imprisonment", "criminal outcomes", "regulatory action", "settlement amounts"):
        assert phrase in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_legal_disputes_conflict_timing_v1(_chart(), datetime(2026, 8, 23))


def test_missing_dasha_is_unavailable_not_invented():
    chart = _chart(); chart.pop("dasha_periods")
    result = analyze_legal_disputes_conflict_timing_v1(chart, NOW)
    assert result["available"] is False
    assert "dasha" in result["reason"].lower()
