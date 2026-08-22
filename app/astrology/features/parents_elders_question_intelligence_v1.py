from __future__ import annotations

import re
from typing import Any


INTENTS: dict[str, tuple[str, ...]] = {
    "parents_elders_overview": ("parents and elders", "parents overview", "elders overview", "tell me about my parents", "tell me about elders", "relationship with parents"),
    "emotional_support": ("emotional support", "support from parents", "support from family", "closeness with parents", "bond with parents"),
    "guidance_mentorship": ("guidance", "mentor", "mentorship", "advice from parents", "advice from elders", "guidance from parents"),
    "duty_responsibility": ("responsibility", "responsibilities", "duty", "duties", "care for parents", "family responsibility"),
    "authority_structure": ("authority", "strict parent", "strict parents", "discipline", "family authority"),
    "independence_boundaries": ("independence", "boundaries", "boundary", "space from parents", "separate from parents"),
    "family_continuity": ("family continuity", "family bond", "family connection", "family support", "connection with elders"),
    "parents_elders_timing": ("when", "what year", "which year", "best period", "strongest period", "timing"),
}

PROHIBITED_SIGNALS = (
    "will my mother die", "will my father die", "when will my mother die", "when will my father die",
    "parent die", "parents die", "lifespan of my mother", "lifespan of my father", "parent lifespan",
    "will my mother get sick", "will my father get sick", "parent illness", "parents illness",
    "what does my father think", "what does my mother think", "is my father good", "is my mother good",
)


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def analyze_parents_elders_question_v1(question: str) -> dict[str, Any]:
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

    domain_signal = any(token in q for token in ("parent", "mother", "father", "elder", "family"))
    timing_requested = "parents_elders_timing" in matched
    prohibited = [phrase for phrase in PROHIBITED_SIGNALS if phrase in q]
    substantive = {k: v for k, v in scores.items() if k != "parents_elders_timing"}
    primary = "unknown"

    if "parents_elders_overview" in substantive:
        primary = "parents_elders_overview"
    elif substantive:
        priority = ["emotional_support", "guidance_mentorship", "duty_responsibility", "authority_structure", "independence_boundaries", "family_continuity"]
        primary = max(substantive, key=lambda key: (substantive[key], -priority.index(key) if key in priority else -99))
    elif timing_requested and domain_signal:
        primary = "parents_elders_timing"
    elif domain_signal:
        primary = "parents_elders_overview"

    available = primary != "unknown"
    return {
        "available": available,
        "event": "parents_elders" if available else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary,
        "timing_requested": timing_requested,
        "matched_signals": matched,
        "requires_timing_engine": timing_requested,
        "prohibited_request_detected": bool(prohibited),
        "prohibited_signals": prohibited,
        "safety": {
            "health_diagnosis_or_prognosis_allowed": False,
            "lifespan_or_death_prediction_allowed": False,
            "specific_person_intention_or_character_inference_allowed": False,
            "caregiving_or_reconciliation_guarantee_allowed": False,
        },
    }
