from __future__ import annotations

import re
from typing import Any


FINANCE_INTENTS: dict[str, tuple[str, ...]] = {
    "wealth_potential": (
        "will i be rich", "will i become rich", "will i be wealthy", "become wealthy",
        "wealth potential", "financially successful", "financial success",
    ),
    "income_savings": (
        "income", "earnings", "earning", "salary", "savings", "save money", "financial stability",
    ),
    "business_wealth": (
        "business", "entrepreneur", "entrepreneurship", "self employed", "self-employed",
        "earn through business", "money through business",
    ),
    "gains_networks": (
        "gains", "network", "connections", "opportunities", "multiple income", "side income",
    ),
    "speculation_creativity": (
        "speculation", "speculative", "trading", "trade", "stock market", "stocks", "stock",
        "shares", "share market", "investment", "investments", "invest", "investing",
        "creative income", "risky investment",
    ),
    "joint_assets_inheritance": (
        "inheritance", "inherit", "ancestral", "joint assets", "shared assets", "partner money",
        "spouse money", "family wealth",
    ),
    "fortune_long_term_support": (
        "long term wealth", "long-term wealth", "prosperity", "financial growth", "wealth growth",
    ),
    "finance_timing": (
        "when", "what year", "which year", "best period", "strongest period", "financial period",
        "money period", "wealth period", "growth period",
    ),
}


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def analyze_finance_question_v1(question: str) -> dict[str, Any]:
    """Classify natural-language Finance & Wealth questions.

    This layer identifies what the user is asking before natal/timing reasoning is
    invoked. It does not itself provide investment advice or financial forecasts.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string.")

    q = _normalise(question)
    scores: dict[str, int] = {}
    matched: dict[str, list[str]] = {}

    for intent, phrases in FINANCE_INTENTS.items():
        hits = [phrase for phrase in phrases if phrase in q]
        if hits:
            matched[intent] = hits
            scores[intent] = len(hits)

    # Timing words modify the substantive financial intent rather than replacing
    # it when the question clearly names a financial topic.
    timing_requested = bool(matched.get("finance_timing"))
    substantive = {k: v for k, v in scores.items() if k != "finance_timing"}

    if substantive:
        primary_intent = max(substantive, key=lambda key: (substantive[key], -list(FINANCE_INTENTS).index(key)))
    elif timing_requested and any(token in q for token in ("money", "wealth", "financial", "income", "earn")):
        primary_intent = "finance_timing"
    else:
        primary_intent = "unknown"

    finance_relevant = primary_intent != "unknown"
    return {
        "available": finance_relevant,
        "event": "finance_wealth" if finance_relevant else "unknown",
        "model_version": "v1",
        "original_question": question,
        "normalised_question": q,
        "primary_intent": primary_intent,
        "timing_requested": timing_requested,
        "matched_signals": matched,
        "requires_timing_engine": timing_requested,
        "requires_natal_engine": finance_relevant,
        "safety": {
            "financial_advice_allowed": False,
            "investment_instruction_allowed": False,
            "guaranteed_return_language_allowed": False,
        },
    }
