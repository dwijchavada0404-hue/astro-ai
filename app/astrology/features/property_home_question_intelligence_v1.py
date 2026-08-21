from __future__ import annotations

import re
from typing import Any


INTENTS: dict[str, tuple[str, ...]] = {
    "property_acquisition": (
        "buy a house", "buy house", "buy a home", "buy home", "purchase property", "purchase a property",
        "own a house", "own house", "own a home", "own home", "property purchase", "home purchase",
    ),
    "property_sale_disposal": (
        "sell property", "sell my property", "sell house", "sell my house", "dispose property", "property sale",
    ),
    "relocation": (
        "relocate", "relocation", "move house", "move home", "change residence", "change home", "shift house",
    ),
    "inheritance_family_property": (
        "inherit property", "property inheritance", "ancestral property", "family property", "inherit a house",
    ),
    "renovation_construction": (
        "renovate", "renovation", "construct house", "construction", "build a house", "build house", "home improvement",
    ),
    "property_direction": (
        "property potential", "home potential", "property direction", "home direction", "property prospects",
        "property suitable", "home stability", "residential stability",
    ),
    "property_timing": (
        "when", "what year", "which year", "best period", "strongest period", "property timing", "home timing",
    ),
    "property_overview": (
        "overall property", "overall home", "property future", "home future", "property overview", "home overview",
        "tell me about my property", "tell me about my home", "property and home", "home and property",
    ),
}


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def analyze_property_home_question_v1(question: str) -> dict[str, Any]:
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

    timing_requested = "property_timing" in matched
    substantive = {k: v for k, v in scores.items() if k != "property_timing"}

    priority = [
        "property_acquisition", "property_sale_disposal", "relocation", "inheritance_family_property",
        "renovation_construction", "property_overview", "property_direction",
    ]
    primary = "unknown"
    if substantive:
        primary = max(substantive, key=lambda key: (substantive[key], -priority.index(key) if key in priority else -99))
    elif timing_requested and any(token in q for token in ("property", "house", "home", "residence")):
        primary = "property_timing"

    available = primary != "unknown"
    return {
        "available": available,
        "event": "property_home" if available else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary,
        "timing_requested": timing_requested,
        "matched_signals": matched,
        "requires_timing_engine": timing_requested,
        "safety": {
            "ownership_fact_inference_allowed": False,
            "guaranteed_transaction_language_allowed": False,
            "financial_or_legal_advice_allowed": False,
        },
    }
