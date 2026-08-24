from datetime import datetime, timezone

import pytest

from app.astrology.features.legal_disputes_conflict_trajectory_v1 import analyze_legal_disputes_conflict_trajectory_v1

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _chart():
    return {"houses": {"6": {"lord": "Mars"}, "7": {"lord": "Venus"}, "8": {"lord": "Saturn"}, "9": {"lord": "Jupiter"}}, "planets": {"Mars": {"house": 6}, "Venus": {"house": 7}, "Saturn": {"house": 8}, "Jupiter": {"house": 9}, "Mercury": {"house": 7}, "Sun": {"house": 9}}, "dasha_periods": [{"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Mars", "sub_lord": "Mercury"}, {"start": "2027-01-01T00:00:00+00:00", "end": "2030-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Venus"}]}


def test_trajectory_scores_are_bounded_and_patterned():
    result = analyze_legal_disputes_conflict_trajectory_v1(_chart(), NOW)
    assert result["available"] is True
    for key in ("dispute_engagement_score", "negotiation_mediation_score", "complexity_endurance_score", "principles_fairness_score", "competition_assertiveness_score", "resolution_capacity_score"):
        assert 0.0 <= result[key] <= 1.0
    assert result["trajectory_pattern"]
    assert result["near_term_direction"]


def test_trajectory_uses_all_lower_layers():
    result = analyze_legal_disputes_conflict_trajectory_v1(_chart(), NOW)
    assert result["timing_available"] is True
    assert result["events_available"] is True
    assert set(result["components"]) == {"natal", "timing", "events"}


def test_reality_override_prevents_manufactured_legal_history():
    rule = analyze_legal_disputes_conflict_trajectory_v1(_chart(), NOW)["historical_validation"]["rule"].lower()
    assert "known legal history" in rule
    assert "must not manufacture" in rule
    assert "judgments" in rule and "settlements" in rule


def test_verdict_criminal_regulatory_and_win_loss_claims_are_disallowed():
    text = analyze_legal_disputes_conflict_trajectory_v1(_chart(), NOW)["limitation"].lower()
    assert "court verdicts" in text and "imprisonment" in text
    assert "regulatory action" in text and "settlement amounts" in text
    assert "won or lost" in text


def test_timezone_required():
    with pytest.raises(ValueError, match="timezone-aware"):
        analyze_legal_disputes_conflict_trajectory_v1(_chart(), datetime(2026, 8, 23))
