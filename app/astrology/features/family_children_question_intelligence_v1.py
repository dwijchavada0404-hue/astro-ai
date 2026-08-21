from __future__ import annotations

import re
from typing import Any


INTENTS: dict[str, tuple[str, ...]] = {
    "children_parenting": (
        "have children", "have a child", "have kids", "children", "child", "kids", "parenthood", "parenting", "become a parent",
    ),
    "family_growth": (
        "family grow", "family growth", "family expansion", "expand my family", "family responsibilities",
    ),
    "family_change": (
        "family change", "family changes", "family structure", "domestic change", "family transition",
    ),
    "family_support": (
        "family support", "support from family", "support from parents", "support from relatives", "elders", "intergenerational",
    ),
    "family_direction": (
        "family stability", "family direction", "family prospects", "family life direction", "family potential",
    ),
    "family_timing": (
        "when", "what year", "which year", "best period", "strongest period", "family timing", "children timing",
    ),
    "family_overview": (
        "overall family", "family future", "family overview", "family and children", "children and family", "tell me about my family",
    ),
}


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def analyze_family_children_question_v1(question: str) -> dict[str, Any]:
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

    timing_requested = "family_timing" in matched
    substantive = {key: value for key, value in scores.items() if key != "family_timing"}
    priority = ["children_parenting", "family_growth", "family_change", "family_support", "family_overview", "family_direction"]

    primary = "unknown"
    if substantive:
        primary = max(substantive, key=lambda key: (substantive[key], -priority.index(key) if key in priority else -99))
    elif timing_requested and any(token in q for token in ("family", "child", "children", "kids", "parent")):
        primary = "family_timing"

    available = primary != "unknown"
    return {
        "available": available,
        "event": "family_children" if available else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary,
        "timing_requested": timing_requested,
        "matched_signals": matched,
        "requires_timing_engine": timing_requested,
        "safety": {
            "fertility_diagnosis_allowed": False,
            "pregnancy_or_childbirth_prediction_allowed": False,
            "child_count_or_sex_prediction_allowed": False,
            "unconfirmed_family_fact_inference_allowed": False,
        },
    }
