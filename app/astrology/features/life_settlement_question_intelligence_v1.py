from __future__ import annotations

import re
from typing import Any


INTENTS: dict[str, tuple[str, ...]] = {
    "settlement_overview": (
        "settled in life", "settle in life", "life settled", "life stable", "life become stable",
        "everything fall into place", "overall life", "life settlement", "settlement in life",
    ),
    "settlement_timing": (
        "when will i settle", "when will i be settled", "when will life become stable", "when will everything stabilize",
        "when will everything fall into place", "what year will i settle", "which year will i settle", "settlement timing",
    ),
    "settlement_age": (
        "what age will i settle", "at what age will i settle", "what age will i be settled", "settled by age",
        "settled at age", "by what age", "which age",
    ),
    "target_age_outlook": (
        "what will my life look like at", "life at age", "life when i am", "how will my life be at",
    ),
    "multi_domain_stability": (
        "career money marriage", "career finance marriage", "career and money and marriage", "career + money + marriage",
        "career wealth marriage", "career property marriage", "career money relationship",
    ),
}


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def _extract_target_age(q: str) -> int | None:
    patterns = (
        r"(?:at|by|age)\s+(\d{1,3})\b",
        r"when i am\s+(\d{1,3})\b",
        r"when i'm\s+(\d{1,3})\b",
    )
    for pattern in patterns:
        match = re.search(pattern, q)
        if match:
            age = int(match.group(1))
            if 1 <= age <= 120:
                return age
    return None


def analyze_life_settlement_question_v1(question: str) -> dict[str, Any]:
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

    target_age = _extract_target_age(q)
    if target_age is not None:
        matched.setdefault("target_age_outlook", []).append(f"age:{target_age}")
        scores["target_age_outlook"] = scores.get("target_age_outlook", 0) + 1

    settlement_tokens = any(token in q for token in ("settle", "settled", "stable", "stability", "fall into place"))
    timing_tokens = any(token in q for token in ("when", "what year", "which year", "what age", "at what age", "by what age"))

    priority = ["settlement_age", "target_age_outlook", "settlement_timing", "multi_domain_stability", "settlement_overview"]
    if scores:
        primary = max(scores, key=lambda key: (scores[key], -priority.index(key) if key in priority else -99))
    elif settlement_tokens and timing_tokens:
        primary = "settlement_timing"
    elif settlement_tokens:
        primary = "settlement_overview"
    else:
        primary = "unknown"

    available = primary != "unknown"
    return {
        "available": available,
        "event": "life_settlement" if available else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary,
        "target_age": target_age,
        "timing_requested": primary in {"settlement_timing", "settlement_age", "target_age_outlook"} or timing_tokens,
        "matched_signals": matched,
        "requires_timing_engine": primary in {"settlement_timing", "settlement_age", "target_age_outlook"} or timing_tokens,
        "requires_cross_domain_synthesis": available,
        "safety": {
            "guaranteed_settlement_date_allowed": False,
            "single_domain_equals_settlement_allowed": False,
            "known_reality_override_required": True,
            "medical_financial_legal_advice_replacement_allowed": False,
        },
    }
