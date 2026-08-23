from datetime import datetime, timezone

import pytest

from app.astrology.features.legal_disputes_conflict_synthesis_v1 import analyze_legal_disputes_conflict_synthesis_v1

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
            "Sun": {"house": 6},
            "Rahu": {"house": 8},
            "Venus": {"house": 7},
        },
        "dasha_periods": [
            {"start": "2024-01-01T00:00:00+00:00", "end": "2026-01-01T00:00:00+00:00", "major_lord": "Mars", "sub_lord": "Mercury"},
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Saturn", "sub_lord": "Jupiter"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Mercury", "sub_lord": "Venus"},
        ],
    }


def test_synthesis_scores_confidence_and_coverage_are_bounded():
    result = analyze_legal_disputes_conflict_synthesis_v1(_chart(), NOW)
    assert result["available"] is True
    assert 0.0 <= result["confidence"] <= 1.0
    assert 0.0 <= result["component_coverage"] <= 1.0
    assert all(0.0 <= score <= 1.0 for score in result["scores"].values())


def test_synthesis_exposes_outlook_and_future_context():
    result = analyze_legal_disputes_conflict_synthesis_v1(_chart(), NOW)
    assert result["outlook"]
    assert result["strongest_area"] in result["scores"]
    assert result["strongest_future_period"] is not None
    assert result["strongest_future_event"] is not None


def test_reality_override_prevents_manufactured_legal_events():
    rule = analyze_legal_disputes_conflict_synthesis_v1(_chart(), NOW)["historical_validation"]["rule"].lower()
    assert "known legal history" in rule
    assert "must never manufacture" in rule
    assert "arrests" in rule and "judgments" in rule
    assert "wins/losses" in rule


def test_verdict_liability_criminal_and_settlement_predictions_are_disallowed():
    text = analyze_legal_disputes_conflict_synthesis_v1(_chart(), NOW)["limitation"].lower()
    assert "not legal advice" in text
    assert "guilt" in text and "liability" in text
    assert "court verdicts" in text and "imprisonment" in text
    assert "regulatory action" in text and "settlement amounts" in text
    assert "won or lost" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_legal_disputes_conflict_synthesis_v1(_chart(), datetime(2026, 8, 23))
