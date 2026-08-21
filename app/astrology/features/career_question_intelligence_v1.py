from __future__ import annotations

import re
from typing import Any


CAREER_INTENTS: dict[str, tuple[str, ...]] = {
    "career_overview": (
        "career", "profession", "professional life", "career overview", "career future",
        "career progress", "career progression", "career growth", "career path",
    ),
    "career_direction": (
        "which career", "what career", "career suits", "career suitable", "profession suits",
        "best profession", "best career", "career field", "profession field", "career direction",
    ),
    "job_vs_business": (
        "job or business", "business or job", "job vs business", "job versus business",
        "employment or business", "business", "entrepreneur", "self employed", "self-employed",
    ),
    "promotion": (
        "promotion", "promoted", "recognition", "increased responsibility", "higher role",
    ),
    "job_change": (
        "job change", "change job", "switch job", "switch jobs", "career change",
        "professional transition", "change company", "switch company",
    ),
    "new_job": (
        "new job", "get a job", "find a job", "employment", "job offer", "next job",
    ),
    "foreign_work": (
        "foreign work", "work abroad", "job abroad", "overseas job", "international work",
        "multinational", "mnc", "remote international",
    ),
    "career_challenges": (
        "career challenge", "career challenges", "job loss", "lose my job", "unemployment",
        "career pressure", "career disruption", "career setback", "career recovery",
    ),
    "career_timing": (
        "when", "what year", "which year", "best period", "strongest period", "career timing",
        "job timing", "promotion timing", "future", "next year", "this year",
    ),
}

EVENT_INTENTS = {"promotion", "job_change", "new_job", "foreign_work", "career_challenges"}


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def analyze_career_question_v1(question: str) -> dict[str, Any]:
    """Classify natural-language Career & Profession questions for the V1 stack."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string.")

    q = _normalise(question)
    matched: dict[str, list[str]] = {}
    scores: dict[str, int] = {}
    for intent, phrases in CAREER_INTENTS.items():
        hits = [phrase for phrase in phrases if phrase in q]
        if hits:
            matched[intent] = hits
            scores[intent] = len(hits)

    timing_requested = bool(matched.get("career_timing"))
    substantive = {key: value for key, value in scores.items() if key != "career_timing"}
    priority = [
        "promotion", "new_job", "job_change", "foreign_work", "career_challenges",
        "job_vs_business", "career_direction", "career_overview",
    ]
    if substantive:
        primary_intent = max(substantive, key=lambda key: (substantive[key], -priority.index(key)))
    elif timing_requested and any(token in q for token in ("career", "job", "profession", "promotion", "work")):
        primary_intent = "career_timing"
    else:
        primary_intent = "unknown"

    available = primary_intent != "unknown"
    return {
        "available": available,
        "event": "career_profession" if available else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary_intent,
        "timing_requested": timing_requested,
        "matched_signals": matched,
        "requires_timing_engine": timing_requested,
        "requires_event_engine": primary_intent in EVENT_INTENTS,
        "requires_natal_engine": available,
        "safety": {
            "guaranteed_outcome_language_allowed": False,
            "termination_prediction_allowed": False,
            "historical_event_assumption_allowed": False,
            "career_advice_replacement_allowed": False,
        },
    }
