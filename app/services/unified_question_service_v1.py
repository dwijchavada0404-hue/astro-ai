from __future__ import annotations

from datetime import datetime
from typing import Any

from app.astrology.features.top_level_question_router_v1 import route_top_level_question_v1


MAX_QUESTION_LENGTH = 1000
API_CONTRACT_VERSION = "v1"


def _validate_reference_moment(reference_moment: datetime) -> None:
    if not isinstance(reference_moment, datetime):
        raise ValueError("reference_moment must be a datetime.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")


def _validate_question(question: str) -> str:
    if not isinstance(question, str):
        raise ValueError("question must be a string.")
    cleaned = " ".join(question.strip().split())
    if not cleaned:
        raise ValueError("question must not be empty.")
    if len(cleaned) > MAX_QUESTION_LENGTH:
        raise ValueError(f"question must not exceed {MAX_QUESTION_LENGTH} characters.")
    return cleaned


def _validate_chart(chart: dict[str, Any]) -> None:
    if not isinstance(chart, dict):
        raise ValueError("chart must be a dictionary.")
    if not chart:
        raise ValueError("chart must not be empty.")


def _validate_life_context(life_context: dict[str, Any] | None) -> None:
    if life_context is not None and not isinstance(life_context, dict):
        raise ValueError("life_context must be a dictionary when provided.")


def answer_unified_question_v1(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
    life_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Production-facing service contract for AstroAI's mature domain router.

    This layer intentionally does not alter astrology scores or domain decisions.
    It validates transport-facing inputs and normalizes router output into a stable
    envelope that a web/mobile client can consume consistently.
    """
    _validate_chart(chart)
    cleaned_question = _validate_question(question)
    _validate_reference_moment(reference_moment)
    _validate_life_context(life_context)

    routed = route_top_level_question_v1(
        chart,
        cleaned_question,
        reference_moment,
        life_context=life_context,
    )
    if not isinstance(routed, dict):
        raise RuntimeError("Top-level question router returned an invalid response.")

    available = bool(routed.get("available"))
    domain = routed.get("domain")
    route = routed.get("route") or "unsupported"
    answer = routed.get("answer") or routed.get("reason")

    status = "answered" if available else "unsupported"
    return {
        "api_contract_version": API_CONTRACT_VERSION,
        "status": status,
        "question": cleaned_question,
        "reference_moment": reference_moment.isoformat(),
        "domain": domain,
        "route": route,
        "answer": answer,
        "limitation": routed.get("limitation"),
        "result": routed,
        "meta": {
            "deterministic_router": True,
            "reality_override_enabled": life_context is not None,
            "guaranteed_outcome": False,
        },
    }
