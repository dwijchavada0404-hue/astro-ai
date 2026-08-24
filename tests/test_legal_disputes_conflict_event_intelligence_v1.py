from datetime import datetime, timezone

import pytest

from app.astrology.features.legal_disputes_conflict_event_intelligence_v1 import analyze_legal_disputes_conflict_event_intelligence_v1

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {
            "6": {"lord": "Mars"},
            "7": {"lord": "Mercury"},
            "8": {"lord": "Saturn"},
            "9": {"lord": "Jupiter"},
        },
        "planets": {
            "Mars": {"house": 6},
            "Mercury": {"house": 7},
            "Saturn": {"house": 8},
            "Jupiter": {"house": 9},
            "Sun": {"house": 9},
            "Venus": {"house": 7},
            "Rahu": {"house": 8},
        },
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mars", "sub_lord": "Saturn"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Jupiter"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Venus"},
        ],
    }


def test_event_scores_are_bounded_and_complete():
    result = analyze_legal_disputes_conflict_event_intelligence_v1(_chart(), NOW)
    assert result["available"] is True
    assert set(result["events"]) == {
        "dispute_engagement",
        "negotiation_mediation",
        "complexity_endurance",
        "principles_fairness",
        "competition_assertiveness",
        "resolution_capacity",
    }
    for event in result["events"].values():
        assert 0.0 <= event["activation_score"] <= 1.0
        assert event["activation_level"] in {"light", "moderate", "strong"}


def test_strongest_future_event_is_symbolic_not_outcome_claim():
    result = analyze_legal_disputes_conflict_event_intelligence_v1(_chart(), NOW)
    assert result["strongest_future_event"]["event"] in result["events"]
    assert "rather than a predicted legal outcome" in result["answer"].lower()


def test_historical_reality_override_blocks_manufactured_legal_events():
    rule = analyze_legal_disputes_conflict_event_intelligence_v1(_chart(), NOW)["historical_validation"]["rule"].lower()
    assert "known legal history" in rule
    assert "actual outcomes override astrology" in rule
    assert "must not be treated as proof" in rule
    assert "arrest" in rule and "judgment" in rule and "regulatory action" in rule


def test_verdict_criminal_regulatory_and_settlement_predictions_are_disallowed():
    text = analyze_legal_disputes_conflict_event_intelligence_v1(_chart(), NOW)["limitation"].lower()
    assert "not legal advice" in text
    assert "guilt" in text and "liability" in text and "court verdicts" in text
    assert "arrest" in text and "imprisonment" in text and "criminal outcomes" in text
    assert "regulatory action" in text and "settlement amounts" in text
    assert "won or lost" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_legal_disputes_conflict_event_intelligence_v1(_chart(), datetime(2026, 8, 23))
