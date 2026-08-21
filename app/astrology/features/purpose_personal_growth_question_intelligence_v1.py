from __future__ import annotations

import re
from typing import Any


INTENTS: dict[str, tuple[str, ...]] = {
    "self_development": (
        "personal growth", "self development", "self-development", "grow as a person", "become a better version of myself", "identity growth",
    ),
    "creative_expression": (
        "creative expression", "creativity", "creative purpose", "express myself", "creative contribution",
    ),
    "service_contribution": (
        "serve others", "service", "contribute", "contribution", "help people", "useful contribution", "social contribution",
    ),
    "knowledge_guidance": (
        "teach", "teaching", "mentor", "mentoring", "guide others", "guidance", "share knowledge", "philosophy",
    ),
    "public_contribution": (
        "leadership", "public contribution", "public role", "make an impact", "impact through work", "responsibility",
    ),
    "inner_growth": (
        "inner growth", "spiritual growth", "spiritual path", "reflection", "inner development", "meaning in life", "inner purpose",
    ),
    "purpose_overview": (
        "life purpose", "purpose in life", "what is my purpose", "what am i meant to do", "tell me about my purpose", "personal growth overview", "purpose overview",
    ),
    "purpose_timing": (
        "when", "what year", "which year", "best period", "strongest period", "purpose timing", "growth timing", "transformation timing",
    ),
}


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def analyze_purpose_personal_growth_question_v1(question: str) -> dict[str, Any]:
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

    timing_requested = "purpose_timing" in matched
    substantive = {key: value for key, value in scores.items() if key != "purpose_timing"}
    priority = [
        "purpose_overview", "self_development", "creative_expression", "service_contribution",
        "knowledge_guidance", "public_contribution", "inner_growth",
    ]
    primary = "unknown"
    if substantive:
        primary = max(substantive, key=lambda key: (substantive[key], -priority.index(key) if key in priority else -99))
    elif timing_requested and any(token in q for token in ("purpose", "growth", "calling", "meaning", "mentor", "teach", "contribut", "spiritual", "transform")):
        primary = "purpose_timing"

    available = primary != "unknown"
    return {
        "available": available,
        "event": "purpose_personal_growth" if available else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary,
        "timing_requested": timing_requested,
        "matched_signals": matched,
        "requires_timing_engine": timing_requested,
        "safety": {
            "fixed_destiny_claim_allowed": False,
            "singular_life_purpose_claim_allowed": False,
            "spiritual_status_claim_allowed": False,
            "moral_worth_inference_allowed": False,
            "mandatory_vocation_claim_allowed": False,
        },
    }
