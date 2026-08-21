import pytest

from app.astrology.features.life_context_v1 import (
    normalize_life_context_v1,
    reconcile_answer_with_life_context_v1,
)


def test_confirmed_achieved_milestone_overrides_predictive_assumption():
    routed = {
        "available": True,
        "domain": "property_home",
        "answer": "A future property-support window is present.",
    }
    context = {
        "milestones": {
            "home_property": {
                "state": "user_confirmed_achieved",
                "achieved_date": "2025-01-15",
            }
        }
    }

    result = reconcile_answer_with_life_context_v1(routed, context)

    assert result["reality_reconciliation"]["applied"] is True
    assert result["life_context"]["confirmed_achieved"] == ["home_property"]
    assert result["answer"].startswith("Reality override:")
    assert "already achieved" in result["answer"]
    assert "interpreted historically or contextually" in result["answer"]


def test_likely_pending_is_not_promoted_to_fact():
    routed = {
        "available": True,
        "domain": "career",
        "answer": "Career development remains active.",
    }
    context = {
        "milestones": {
            "career_stability": {"state": "likely_pending"}
        }
    }

    result = reconcile_answer_with_life_context_v1(routed, context)

    assert result["reality_reconciliation"]["applied"] is False
    assert result["answer"] == routed["answer"]
    assert result["life_context"]["likely_pending"] == ["career_stability"]
    assert result["life_context"]["confirmed_achieved"] == []


def test_cross_domain_context_reports_partial_achievement():
    routed = {
        "available": True,
        "domain": "life_settlement",
        "answer": "Cross-domain support is developing.",
    }
    context = {
        "milestones": {
            "career_stability": "user_confirmed_achieved",
            "financial_stability": "likely_pending",
            "committed_relationship": "unknown",
        }
    }

    result = reconcile_answer_with_life_context_v1(routed, context)
    summary = result["reality_reconciliation"]["life_settlement_context"]

    assert summary["status"] == "partially_confirmed_achieved"
    assert summary["confirmed_achieved_count"] == 1
    assert summary["likely_pending_count"] == 1
    assert summary["unknown_count"] == 1


def test_unsupported_milestone_is_rejected():
    with pytest.raises(ValueError, match="Unsupported life milestone"):
        normalize_life_context_v1(
            {"milestones": {"private_jet": {"state": "user_confirmed_achieved"}}}
        )


def test_invalid_state_is_rejected():
    with pytest.raises(ValueError, match="state must be one of"):
        normalize_life_context_v1(
            {"milestones": {"career_stability": {"state": "definitely_pending"}}}
        )


def test_no_context_preserves_existing_contract():
    routed = {"available": True, "domain": "finance", "answer": "Existing answer."}
    assert reconcile_answer_with_life_context_v1(routed, None) == routed
