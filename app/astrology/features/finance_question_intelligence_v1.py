from __future__ import annotations

import re
from typing import Any


FINANCE_INTENTS: dict[str, tuple[str, ...]] = {
    "wealth_potential": (
        "will i be rich", "will i become rich", "will i be wealthy", "become wealthy",
        "wealth potential", "financially successful", "financial success",
    ),
    "income_savings": (
        "income", "earnings", "earning", "salary", "job income", "job", "career income",
        "savings", "save money", "financial stability", "finance", "finances",
        "financial situation", "money situation",
    ),
    "business_wealth": (
        "business", "entrepreneur", "entrepreneurship", "self employed", "self-employed",
        "earn through business", "money through business",
    ),
    "gains_networks": (
        "gains", "network", "connections", "opportunities", "multiple income", "multiple incomes",
        "multiple income sources", "side income", "side incomes", "second income",
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
    "property_assets": (
        "property", "real estate", "house property", "land", "asset accumulation", "assets",
    ),
    "fortune_long_term_support": (
        "long term wealth", "long-term wealth", "prosperity", "financial growth", "wealth growth",
    ),
    "finance_timing": (
        "when", "what year", "which year", "best period", "strongest period", "financial period",
        "money period", "wealth period", "growth period", "improve", "improvement",
    ),
}

GENERIC_FINANCE_TERMS = {
    "finance", "finances", "financial situation", "money situation", "money",
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

    timing_requested = bool(matched.get("finance_timing"))
    substantive = {k: v for k, v in scores.items() if k != "finance_timing"}

    # Generic questions such as "When will my finances improve?" are timing
    # questions, even though generic finance vocabulary also overlaps the broad
    # income/savings bucket. More specific themes keep their substantive primary
    # intent and use timing as a modifier.
    income_hits = set(matched.get("income_savings", []))
    generic_income_only = bool(income_hits) and income_hits.issubset(GENERIC_FINANCE_TERMS)
    only_generic_substantive = set(substantive) == {"income_savings"} and generic_income_only

    if timing_requested and only_generic_substantive:
        primary_intent = "finance_timing"
    elif substantive:
        primary_intent = max(substantive, key=lambda key: (substantive[key], -list(FINANCE_INTENTS).index(key)))
    elif timing_requested and any(token in q for token in ("money", "wealth", "financial", "finance", "finances", "income", "earn")):
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
