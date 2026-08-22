from __future__ import annotations

import re
from typing import Any


INTENTS: dict[str, tuple[str, ...]] = {
    "sibling_relationship": ("sibling", "siblings", "brother", "sister", "brothers", "sisters", "relationship with my brother", "relationship with my sister"),
    "communication_expression": ("communication", "communicate", "speaking", "writing", "expression", "express myself", "conversation"),
    "initiative_courage": ("initiative", "courage", "confidence to act", "take action", "assertive", "assertiveness"),
    "learning_skills": ("skill", "skills", "learning", "learn", "writing skill", "communication skill", "practice"),
    "collaboration_exchange": ("collaboration", "collaborate", "teamwork", "work with others", "peer exchange"),
    "boundaries_competition": ("boundary", "boundaries", "competition", "competitive", "conflict with sibling", "sibling conflict"),
    "siblings_communication_overview": ("siblings and communication", "sibling overview", "communication overview", "tell me about my siblings", "tell me about my communication"),
    "siblings_communication_timing": ("when", "what year", "which year", "best period", "strongest period", "timing"),
}


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def analyze_siblings_communication_question_v1(question: str) -> dict[str, Any]:
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

    timing_requested = "siblings_communication_timing" in matched
    substantive = {key: value for key, value in scores.items() if key != "siblings_communication_timing"}
    primary = "unknown"

    # Explicit overview language must win over its component words. For example,
    # "siblings and communication overview" also contains "siblings" and
    # "communication", but the user's requested scope is the combined synthesis.
    if "siblings_communication_overview" in substantive:
        primary = "siblings_communication_overview"
    elif substantive:
        priority = ["sibling_relationship", "communication_expression", "initiative_courage", "learning_skills", "collaboration_exchange", "boundaries_competition"]
        primary = max(substantive, key=lambda key: (substantive[key], -priority.index(key) if key in priority else -99))
    elif timing_requested and any(token in q for token in ("sibling", "brother", "sister", "communicat", "skill", "collabor", "assert")):
        primary = "siblings_communication_timing"

    available = primary != "unknown"
    return {
        "available": available,
        "event": "siblings_communication" if available else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary,
        "timing_requested": timing_requested,
        "matched_signals": matched,
        "requires_timing_engine": timing_requested,
        "safety": {
            "sibling_existence_inference_allowed": False,
            "specific_person_intention_inference_allowed": False,
            "loyalty_judgment_allowed": False,
            "estrangement_prediction_allowed": False,
            "reconciliation_guarantee_allowed": False,
        },
    }
