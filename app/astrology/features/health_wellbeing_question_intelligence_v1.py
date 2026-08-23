from __future__ import annotations

import re
from typing import Any


INTENTS: dict[str, tuple[str, ...]] = {
    "health_wellbeing_overview": ("health and wellbeing", "health & wellbeing", "wellbeing overview", "wellness overview", "my wellbeing", "wellbeing themes"),
    "vitality_energy": ("energy levels", "vitality", "energy management", "stamina themes"),
    "routine_discipline": ("health routine", "wellness routine", "routine discipline", "daily routine", "healthy habits"),
    "recovery_resilience": ("resilience", "recovery habits", "bounce back", "recovery pattern"),
    "stress_balance": ("stress balance", "stress management", "mental load", "burnout pattern"),
    "rest_restoration": ("rest", "restoration", "sleep routine", "recharge"),
    "preventive_self_care": ("self care", "self-care", "preventive habits", "preventive self care", "wellness habits"),
    "health_wellbeing_timing": ("when", "what year", "which year", "best period", "strongest period", "timing"),
}

MEDICAL_TERMS = (
    "disease", "diagnosis", "diagnose", "illness", "cancer", "tumor", "heart attack", "stroke", "diabetes",
    "blood pressure", "lifespan", "life span", "death", "die", "accident", "fertility", "pregnant", "pregnancy",
    "treatment", "medication", "medicine", "surgery", "operation", "test result", "medical test", "supplement",
    "doctor", "hospital", "prognosis", "recovery from", "will i recover", "will it cure", "will this cure",
)


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def analyze_health_wellbeing_question_v1(question: str) -> dict[str, Any]:
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

    timing_requested = "health_wellbeing_timing" in matched
    prohibited = any(term in q for term in MEDICAL_TERMS)
    substantive = {k: v for k, v in scores.items() if k != "health_wellbeing_timing"}

    primary = "unknown"
    if "health_wellbeing_overview" in substantive:
        primary = "health_wellbeing_overview"
    elif substantive:
        priority = [
            "vitality_energy", "routine_discipline", "recovery_resilience",
            "stress_balance", "rest_restoration", "preventive_self_care",
        ]
        primary = max(
            substantive,
            key=lambda key: (substantive[key], -priority.index(key) if key in priority else -99),
        )
    elif timing_requested and any(token in q for token in ("health", "wellbeing", "wellness", "energy", "stress", "rest", "routine")):
        primary = "health_wellbeing_timing"

    available = primary != "unknown" or prohibited
    return {
        "available": available,
        "event": "health_wellbeing" if available else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary,
        "timing_requested": timing_requested,
        "requires_timing_engine": timing_requested,
        "matched_signals": matched,
        "prohibited_request_detected": prohibited,
        "safety": {
            "medical_diagnosis_allowed": False,
            "disease_prediction_allowed": False,
            "lifespan_or_death_prediction_allowed": False,
            "accident_prediction_allowed": False,
            "fertility_prediction_allowed": False,
            "treatment_or_medication_recommendation_allowed": False,
        },
    }
