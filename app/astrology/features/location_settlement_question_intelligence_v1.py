from __future__ import annotations

import re
from typing import Any


INTENTS: dict[str, tuple[str, ...]] = {
    "foreign_settlement": (
        "settle abroad", "settle overseas", "foreign settlement", "settle in another country",
        "live abroad permanently", "permanent residence abroad", "move abroad permanently",
    ),
    "foreign_travel_exposure": (
        "travel abroad", "foreign travel", "go abroad", "international travel", "work abroad",
        "study abroad", "foreign work", "international work", "overseas work",
    ),
    "long_distance_residence": (
        "live abroad", "living abroad", "reside abroad", "stay abroad", "live overseas", "reside overseas",
        "live away from home", "live away from birthplace", "live far from home",
    ),
    "domestic_relocation": (
        "relocate", "relocation", "move city", "move to another city", "change city", "shift city",
        "move away from home", "change residence",
    ),
    "return_or_re_rooting": (
        "return home", "move back home", "come back home", "return to my country", "move back to my country",
        "return from abroad", "come back from abroad",
    ),
    "location_overview": (
        "location future", "location overview", "foreign prospects", "abroad prospects", "relocation prospects",
        "where will i settle", "where am i likely to settle", "tell me about my location", "location and settlement",
    ),
    "location_timing": (
        "when", "what year", "which year", "best period", "strongest period", "location timing",
        "relocation timing", "foreign timing", "abroad timing",
    ),
}


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def analyze_location_settlement_question_v1(question: str) -> dict[str, Any]:
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

    timing_requested = "location_timing" in matched
    substantive = {key: value for key, value in scores.items() if key != "location_timing"}
    priority = [
        "foreign_settlement", "return_or_re_rooting", "foreign_travel_exposure",
        "long_distance_residence", "domestic_relocation", "location_overview",
    ]
    primary = "unknown"
    if substantive:
        primary = max(substantive, key=lambda key: (substantive[key], -priority.index(key) if key in priority else -99))
    elif timing_requested and any(token in q for token in ("abroad", "foreign", "overseas", "relocat", "location", "residen", "city", "country")):
        primary = "location_timing"

    available = primary != "unknown"
    return {
        "available": available,
        "event": "location_settlement" if available else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary,
        "timing_requested": timing_requested,
        "matched_signals": matched,
        "requires_timing_engine": timing_requested,
        "safety": {
            "migration_fact_inference_allowed": False,
            "visa_or_citizenship_prediction_allowed": False,
            "specific_country_guarantee_allowed": False,
            "foreign_exposure_equals_settlement": False,
        },
    }
