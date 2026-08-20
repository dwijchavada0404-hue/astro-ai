from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.finance_wealth_reasoning_v1 import analyze_finance_wealth_v1
from app.astrology.features.finance_question_intelligence_v1 import analyze_finance_question_v1
from app.astrology.features.finance_timing_v1 import analyze_finance_timing_v1
from app.astrology.features.finance_period_intelligence_v2 import (
    analyze_finance_period_v2,
    extract_finance_period_request_v2,
)


def _theme_for_intent(intent: str) -> str | None:
    mapping = {
        "income_savings": "income_savings",
        "gains_networks": "gains_networks",
        "speculation_creativity": "speculation_creativity",
        "joint_assets_inheritance": "joint_assets_inheritance",
        "fortune_long_term_support": "fortune_long_term_support",
        "business_wealth": "gains_networks",
    }
    return mapping.get(intent)


def route_finance_question_v1(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
) -> dict[str, Any]:
    """Route a natural-language Finance question to natal and/or timing reasoning.

    Explicit calendar-year/range requests use the V2 precision layer. Open-ended
    timing questions continue through the broader past/present/future V1 engine.
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
