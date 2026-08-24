from __future__ import annotations

import re
from typing import Any


INTENTS: dict[str, tuple[str, ...]] = {
    "legal_disputes_overview": (
        "legal disputes", "legal conflict", "disputes and conflict", "legal matters", "conflict themes", "dispute themes",
    ),
    "dispute_engagement": ("dispute", "conflict", "litigation", "legal battle", "contested matter"),
    "negotiation_mediation": ("negotiate", "negotiation", "mediation", "mediate", "amicable settlement", "settle a dispute"),
    "complexity_endurance": ("complex dispute", "long dispute", "protracted dispute", "endurance", "legal pressure"),
    "principles_fairness": ("fairness", "justice", "principles", "ethical conflict"),
    "competition_assertiveness": ("competition", "assertive", "stand my ground", "fight back"),
    "resolution_capacity": ("resolution", "resolve conflict", "resolve dispute", "settlement tendency"),
    "legal_disputes_timing": ("when", "what year", "which year", "best period", "strongest period", "timing"),
}

PROHIBITED_TERMS = (
    "will i win", "will i lose", "win the case", "lose the case", "court verdict", "verdict", "judgment", "judgement",
    "guilty", "guilt", "liable", "liability", "arrest", "arrested", "imprisonment", "jail", "prison", "criminal outcome",
    "regulatory action", "penalty amount", "fine amount", "settlement amount", "how much settlement", "exact settlement",
    "legal advice", "what should i file", "should i sue", "should i appeal", "what legal action", "which section", "which law",
)


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def analyze_legal_disputes_conflict_question_v1(question: str) -> dict[str, Any]:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string.")

    q = _normalise(question)
    matched: dict[str, list[str]] = {}
    scores: dict[str, int] = {}
    for intent, phrases in INTENTS.items():
        hits = [phrase for phrase in phrases if phrase in q]
        if hits:
            matched[intent] = hits
            scores[intent] = len(hits)

    timing_requested = "legal_disputes_timing" in matched
    prohibited = any(term in q for term in PROHIBITED_TERMS)
    substantive = {k: v for k, v in scores.items() if k != "legal_disputes_timing"}

    primary = "unknown"
    if "legal_disputes_overview" in substantive:
        primary = "legal_disputes_overview"
    elif substantive:
        priority = [
            "negotiation_mediation", "resolution_capacity", "dispute_engagement",
            "complexity_endurance", "principles_fairness", "competition_assertiveness",
        ]
        primary = max(substantive, key=lambda key: (substantive[key], -priority.index(key) if key in priority else -99))
    elif timing_requested and any(token in q for token in ("legal", "dispute", "conflict", "case", "litigation")):
        primary = "legal_disputes_timing"

    available = primary != "unknown" or prohibited
    return {
        "available": available,
        "event": "legal_disputes_conflict" if available else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary,
        "timing_requested": timing_requested,
        "requires_timing_engine": timing_requested,
        "matched_signals": matched,
        "prohibited_request_detected": prohibited,
        "safety": {
            "legal_advice_allowed": False,
            "guilt_or_liability_prediction_allowed": False,
            "verdict_prediction_allowed": False,
            "arrest_or_imprisonment_prediction_allowed": False,
            "criminal_or_regulatory_outcome_prediction_allowed": False,
            "exact_settlement_amount_prediction_allowed": False,
        },
    }
