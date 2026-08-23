from datetime import datetime, timezone

from app.astrology.features.legal_disputes_conflict_question_intelligence_v1 import analyze_legal_disputes_conflict_question_v1
from app.astrology.features.legal_disputes_conflict_router_v1 import route_legal_disputes_conflict_question_v1

NOW = datetime(2026, 8, 23, tzinfo=timezone.utc)


def _chart():
    return {
        "houses": {"6": {"lord": "Mars"}, "7": {"lord": "Venus"}, "8": {"lord": "Saturn"}, "9": {"lord": "Jupiter"}},
        "planets": {
            "Mars": {"house": 6}, "Saturn": {"house": 8}, "Mercury": {"house": 7},
            "Jupiter": {"house": 9}, "Sun": {"house": 6}, "Venus": {"house": 7}, "Rahu": {"house": 8},
        },
        "dasha_periods": [
            {"start": "2026-01-01T00:00:00+00:00", "end": "2027-01-01T00:00:00+00:00", "major_lord": "Mars", "sub_lord": "Mercury"},
            {"start": "2027-01-01T00:00:00+00:00", "end": "2029-01-01T00:00:00+00:00", "major_lord": "Jupiter", "sub_lord": "Venus"},
        ],
    }


def test_overview_is_recognized():
    result = analyze_legal_disputes_conflict_question_v1("Give me an overview of my legal disputes and conflict themes")
    assert result["available"] is True
    assert result["primary_intent"] == "legal_disputes_overview"


def test_timing_language_routes_to_timing_engine():
    result = route_legal_disputes_conflict_question_v1(
        _chart(), "When is a stronger period for negotiation in a dispute?", NOW
    )
    assert result["available"] is True
    assert result["route"] == "legal_disputes_conflict_timing_v1"


def test_negotiation_question_routes_to_event_intelligence():
    result = route_legal_disputes_conflict_question_v1(
        _chart(), "What are my negotiation and mediation themes?", NOW
    )
    assert result["available"] is True
    assert result["route"] == "legal_disputes_conflict_event_v1"
    assert result["primary_intent"] == "negotiation_mediation"


def test_verdict_win_loss_and_liability_questions_are_blocked():
    for question in (
        "Will I win the case?",
        "What will the court verdict be?",
        "Will I be held liable?",
        "Will I be arrested?",
    ):
        result = route_legal_disputes_conflict_question_v1(_chart(), question, NOW)
        assert result["available"] is True
        assert result["route"] == "legal_disputes_conflict_safety_boundary_v1"
        text = result["answer"].lower()
        assert "cannot" in text


def test_legal_advice_and_exact_settlement_amount_are_blocked():
    for question in (
        "What legal action should I take?",
        "Should I sue them?",
        "How much settlement will I receive?",
    ):
        result = route_legal_disputes_conflict_question_v1(_chart(), question, NOW)
        assert result["route"] == "legal_disputes_conflict_safety_boundary_v1"


def test_unrelated_question_stays_unsupported():
    result = route_legal_disputes_conflict_question_v1(_chart(), "What colour should I paint my room?", NOW)
    assert result["available"] is False
    assert result["route"] == "unsupported"
