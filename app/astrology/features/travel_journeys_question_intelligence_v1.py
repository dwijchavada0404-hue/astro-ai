from __future__ import annotations

import re
from typing import Any


INTENTS: dict[str, tuple[str, ...]] = {
    "travel_overview": ("travel overview", "travel and journeys", "my travel", "journeys in my life", "travel prospects"),
    "short_journeys": ("short trip", "short trips", "short journey", "short journeys", "local travel", "nearby travel"),
    "long_distance_travel": ("long distance travel", "long-distance travel", "long journey", "long journeys", "distant travel"),
    "international_travel": ("international travel", "foreign travel", "overseas travel", "travel abroad", "go abroad", "visit abroad"),
    "work_study_travel": ("work travel", "business travel", "travel for work", "study travel", "travel for study", "academic travel"),
    "recurring_mobility": ("frequent travel", "travel frequently", "recurring travel", "regular travel", "mobility"),
    "travel_adaptability": ("adapt to travel", "travel adaptability", "comfortable travelling", "comfortable traveling"),
    "travel_timing": ("when", "what year", "which year", "best period", "strongest period", "timing"),
}

SETTLEMENT_TERMS = ("settle abroad", "foreign settlement", "permanent settlement", "permanent relocation", "relocate abroad", "immigrate", "immigration")
SAFETY_TERMS = (
    "accident", "safe trip", "trip be safe", "travel safe", "travel be safe", "crash", "will my flight",
    "visa approved", "visa be approved", "visa get approved", "visa approval", "will i get a visa", "will my visa",
)


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def analyze_travel_journeys_question_v1(question: str) -> dict[str, Any]:
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

    timing_requested = "travel_timing" in matched
    settlement_requested = any(term in q for term in SETTLEMENT_TERMS)
    safety_or_visa_requested = any(term in q for term in SAFETY_TERMS)
    substantive = {k: v for k, v in scores.items() if k != "travel_timing"}
    primary = "unknown"
    if "travel_overview" in substantive:
        primary = "travel_overview"
    elif substantive:
        priority = ["international_travel", "work_study_travel", "long_distance_travel", "short_journeys", "recurring_mobility", "travel_adaptability"]
        primary = max(substantive, key=lambda key: (substantive[key], -priority.index(key) if key in priority else -99))
    elif timing_requested and any(token in q for token in ("travel", "trip", "journey", "abroad", "overseas")):
        primary = "travel_timing"

    # Restricted travel questions still belong to this domain so the router can
    # return a safe bounded response instead of falling through as unsupported.
    available = (primary != "unknown" or safety_or_visa_requested) and not settlement_requested
    return {
        "available": available,
        "event": "travel_journeys" if available else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary,
        "timing_requested": timing_requested,
        "matched_signals": matched,
        "requires_timing_engine": timing_requested,
        "handoff_to_location_settlement": settlement_requested,
        "restricted_outcome_requested": safety_or_visa_requested,
        "safety": {
            "exact_destination_prediction_allowed": False,
            "visa_approval_prediction_allowed": False,
            "permanent_settlement_inference_allowed": False,
            "travel_safety_prediction_allowed": False,
            "accident_prediction_allowed": False,
        },
    }
