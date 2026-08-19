from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.marriage_context_guard import guard_marriage_question
from app.astrology.features.marriage_bidirectional_timing_reasoning_v1 import (
    analyze_marriage_timing_bidirectional_v1,
)
from app.astrology.features.marriage_forecast_router_v3 import route_marriage_question_v3


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _is_open_ended_marriage_timing(question_analysis: dict[str, Any]) -> bool:
    event = str(question_analysis.get("primary_event") or question_analysis.get("event") or "")
    intent = _safe_dict(question_analysis.get("intent"))
    qtype = str(intent.get("question_type") or "")
    horizon = _safe_dict(question_analysis.get("forecast_horizon"))
    horizon_type = str(horizon.get("type") or "")
    question = str(
        question_analysis.get("normalised_question")
        or question_analysis.get("original_question")
        or ""
    ).lower()

    timing_like = event == "marriage_timing" or (
        qtype == "timing" and ("marri" in question or "wedding" in question)
    )
    explicit_horizon = bool(horizon_type) or any(
        token in question
        for token in (
            "this month", "next month", "this year", "next year",
            "next 1 year", "next 2 years", "next 3 years",
        )
    ) or any(str(year) in question for year in range(2020, 2101))

    return timing_like and not explicit_horizon


def route_marriage_question_contextual_v1(
    chart: dict[str, Any],
    question_analysis: dict[str, Any],
    reference_moment: datetime,
    relationship_status: str | None = None,
    previous_context: dict[str, Any] | None = None,
    lookback_years: int = 5,
    lookahead_years: int = 5,
) -> dict[str, Any]:
    """Apply real-world relationship context before Marriage V3 routing.

    Open-ended marriage-timing questions automatically receive a bidirectional
    past + future scan. Explicit date/year questions keep the existing V3 route.
    Known status conflicts are clarified before astrology is run.
    """
    guard = guard_marriage_question(question_analysis, relationship_status)

    if guard.get("action") == "clarify":
        return {
            "available": False,
            "route": "context_guard",
            "requires_clarification": True,
            "context_guard": guard,
            "relationship_status": guard.get("relationship_status"),
            "answer": guard.get("message"),
        }

    effective_status = str(guard.get("relationship_status") or "unknown")

    if _is_open_ended_marriage_timing(question_analysis):
        result = analyze_marriage_timing_bidirectional_v1(
            chart,
            reference_moment,
            relationship_status=effective_status,
            lookback_years=lookback_years,
            lookahead_years=lookahead_years,
        )
        result["route"] = "bidirectional_marriage_timing"
        result["context_guard"] = guard
        if guard.get("action") == "reinterpret":
            result["context_interpretation"] = guard.get("interpretation")
        return result

    result = route_marriage_question_v3(
        chart,
        question_analysis,
        reference_moment,
        previous_context=previous_context,
    )
    if isinstance(result, dict):
        result["context_guard"] = guard
        result["relationship_status"] = effective_status
        if guard.get("action") == "reinterpret":
            result["context_interpretation"] = guard.get("interpretation")
    return result
