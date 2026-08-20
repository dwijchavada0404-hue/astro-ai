from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.finance_wealth_reasoning_v1 import analyze_finance_wealth_v1
from app.astrology.features.finance_question_intelligence_v1 import analyze_finance_question_v1
from app.astrology.features.finance_timing_v1 import analyze_finance_timing_v1
from app.astrology.features.finance_source_of_wealth_v1 import analyze_finance_source_of_wealth_v1
from app.astrology.features.finance_period_intelligence_v2 import (
    analyze_finance_period_v2,
    extract_finance_period_request_v2,
)


SOURCE_PHRASES: dict[str, tuple[str, ...]] = {
    "salary_career": ("job", "salary", "career income", "job income", "profession"),
    "business_entrepreneurship": ("business", "entrepreneur", "entrepreneurship", "self employed", "self-employed"),
    "investments_speculation": ("investment", "investments", "invest", "stocks", "stock market", "trading", "shares", "speculation"),
    "property_assets": ("property", "real estate", "land", "assets", "asset accumulation"),
    "inheritance_shared_wealth": ("inheritance", "inherit", "ancestral", "shared wealth", "joint assets", "spouse money", "partner money"),
    "networks_multiple_income": ("multiple income", "multiple incomes", "multiple income sources", "side income", "second income", "network", "connections"),
}


def _theme_for_intent(intent: str) -> str | None:
    mapping = {
        "income_savings": "income_savings",
        "gains_networks": "gains_networks",
        "speculation_creativity": "speculation_creativity",
        "joint_assets_inheritance": "joint_assets_inheritance",
        "property_assets": "fortune_long_term_support",
        "fortune_long_term_support": "fortune_long_term_support",
        "business_wealth": "gains_networks",
    }
    return mapping.get(intent)


def _requested_sources(question: str) -> list[str]:
    q = question.strip().lower()
    found: list[str] = []
    for source, phrases in SOURCE_PHRASES.items():
        if any(phrase in q for phrase in phrases):
            found.append(source)
    return found


def _is_source_of_wealth_question(question: str, requested_sources: list[str]) -> bool:
    q = question.strip().lower()
    comparison_words = ("or", "versus", "vs", "more from", "better source", "main source", "major source", "source of")
    explicit_source_question = any(token in q for token in comparison_words)
    multiple_source_theme = len(requested_sources) >= 2
    single_source_assessment = bool(requested_sources) and any(
        token in q for token in ("major", "strong", "important", "significant", "main", "source", "multiple")
    )
    return explicit_source_question or multiple_source_theme or single_source_assessment


def route_finance_question_v1(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
) -> dict[str, Any]:
    """Route a natural-language Finance question to natal, source or timing reasoning.

    Explicit calendar-year/range requests use the V2 precision layer. Source-of-
    wealth questions use comparative channel reasoning. Open-ended timing questions
    continue through the broader past/present/future V1 engine.
    """
    understanding = analyze_finance_question_v1(question)
    if not understanding.get("available"):
        return {
            "available": False,
            "route": "unsupported",
            "event": "unknown",
            "understanding": understanding,
            "reason": "The question was not identified as a Finance & Wealth question.",
        }

    natal = analyze_finance_wealth_v1(chart)
    intent = str(understanding.get("primary_intent") or "unknown")
    theme = _theme_for_intent(intent)

    period_request = extract_finance_period_request_v2(question)
    if period_request.get("available"):
        period = analyze_finance_period_v2(chart, question, reference_moment)
        return {
            "available": bool(period.get("available")),
            "route": "finance_period_v2",
            "event": "finance_wealth",
            "primary_intent": intent,
            "understanding": understanding,
            "natal": natal,
            "period": period,
            "answer": period.get("answer") if period.get("available") else period.get("reason"),
            "limitation": period.get("limitation") or natal.get("limitation"),
        }

    requested_sources = _requested_sources(question)
    if not understanding.get("requires_timing_engine") and _is_source_of_wealth_question(question, requested_sources):
        source = analyze_finance_source_of_wealth_v1(chart)
        source_scores = source.get("source_scores") if isinstance(source.get("source_scores"), dict) else {}
        requested = [
            {"source": item, "score": source_scores.get(item)}
            for item in requested_sources
        ]
        requested_ranked = sorted(
            requested,
            key=lambda item: float(item["score"] or 0.0),
            reverse=True,
        )
        return {
            "available": bool(source.get("available")),
            "route": "finance_source_of_wealth",
            "event": "finance_wealth",
            "primary_intent": intent,
            "understanding": understanding,
            "natal": natal,
            "source_of_wealth": source,
            "requested_sources": requested_ranked,
            "strongest_requested_source": requested_ranked[0] if requested_ranked else None,
            "answer": source.get("answer") if source.get("available") else source.get("reason"),
            "limitation": source.get("limitation") or natal.get("limitation"),
        }

    if understanding.get("requires_timing_engine"):
        timing = analyze_finance_timing_v1(chart, reference_moment)
        return {
            "available": bool(timing.get("available")),
            "route": "finance_timing",
            "event": "finance_wealth",
            "primary_intent": intent,
            "understanding": understanding,
            "natal": natal,
            "timing": timing,
            "answer": timing.get("answer") if timing.get("available") else timing.get("reason"),
            "limitation": timing.get("limitation") or natal.get("limitation"),
        }

    score = None
    if theme and isinstance(natal.get("theme_scores"), dict):
        score = natal["theme_scores"].get(theme)

    return {
        "available": bool(natal.get("available")),
        "route": "finance_natal",
        "event": "finance_wealth",
        "primary_intent": intent,
        "theme": theme,
        "theme_score": score,
        "understanding": understanding,
        "natal": natal,
        "answer": natal.get("summary") if natal.get("available") else natal.get("reason"),
        "limitation": natal.get("limitation"),
    }
