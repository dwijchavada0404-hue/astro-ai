from __future__ import annotations

import re
from typing import Any


INTENTS: dict[str, tuple[str, ...]] = {
    "friendship_connection": (
        "friendship", "friends", "close friends", "make friends", "new friends", "friend circle", "peer connection",
    ),
    "network_collaboration": (
        "networking", "network", "collaboration", "collaborate", "professional network", "social network", "connections",
    ),
    "community_participation": (
        "community", "group", "social group", "belonging", "club", "association", "peer group", "community participation",
    ),
    "social_boundary_reset": (
        "boundaries", "social boundaries", "selective friends", "distance from friends", "friend circle change", "social reset", "cut off people",
    ),
    "social_overview": (
        "social life", "social overview", "friends and social life", "friendship overview", "community life", "social connections overview",
    ),
    "social_timing": (
        "when", "what year", "which year", "best period", "strongest period", "friendship timing", "social timing", "networking timing",
    ),
}


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def analyze_friends_social_community_question_v1(question: str) -> dict[str, Any]:
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

    timing_requested = "social_timing" in matched
    substantive = {key: value for key, value in scores.items() if key != "social_timing"}
    priority = ["social_overview", "friendship_connection", "network_collaboration", "community_participation", "social_boundary_reset"]
    primary = "unknown"
    if substantive:
        primary = max(substantive, key=lambda key: (substantive[key], -priority.index(key) if key in priority else -99))
    elif timing_requested and any(token in q for token in ("friend", "social", "network", "community", "group", "peer")):
        primary = "social_timing"

    available = primary != "unknown"
    return {
        "available": available,
        "event": "friends_social_community" if available else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary,
        "timing_requested": timing_requested,
        "matched_signals": matched,
        "requires_timing_engine": timing_requested,
        "safety": {
            "specific_person_loyalty_inference_allowed": False,
            "trustworthiness_inference_allowed": False,
            "betrayal_prediction_allowed": False,
            "enemy_identification_allowed": False,
            "popularity_guarantee_allowed": False,
        },
    }
