from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.astrology.features.life_context_v1 import merge_life_context_v1, normalize_life_context_v1
from app.astrology.features.top_level_question_router_v1 import route_top_level_question_v1
from app.models.chart import BirthInput
from app.services.chart_service import build_chart
from app.services.unified_question_service_v1 import answer_unified_question_v1


router = APIRouter(tags=["AstroAI Questions"])

# Keep these identities so existing API-level tests/integrations that patch the
# historical router seam remain compatible while production requests use the
# hardened unified service by default.
_ORIGINAL_ROUTE_TOP_LEVEL_QUESTION_V1 = route_top_level_question_v1
_ORIGINAL_ANSWER_UNIFIED_QUESTION_V1 = answer_unified_question_v1


class MilestoneContextV1(BaseModel):
    state: Literal["unknown", "likely_pending", "user_confirmed_achieved"] = "unknown"
    achieved_date: date | None = None
    note: str | None = Field(default=None, max_length=500)


class LifeContextV1(BaseModel):
    milestones: dict[str, MilestoneContextV1] = Field(default_factory=dict)


class AstroAIQuestionV1Request(BaseModel):
    birth: BirthInput
    question: str = Field(min_length=1, max_length=1000)
    reference_moment: datetime
    life_context: LifeContextV1 | None = None
    life_context_updates: LifeContextV1 | None = None


def _effective_life_context(payload: AstroAIQuestionV1Request) -> dict | None:
    current_context = payload.life_context.model_dump(mode="json") if payload.life_context else None
    context_updates = (
        payload.life_context_updates.model_dump(mode="json")
        if payload.life_context_updates
        else None
    )
    if context_updates is not None:
        return merge_life_context_v1(current_context, context_updates)
    if current_context is not None:
        return normalize_life_context_v1(current_context)
    return None


def _validate_transport_basics(question: str, reference_moment: datetime) -> str:
    cleaned = " ".join(question.strip().split())
    if not cleaned:
        raise ValueError("question must not be empty.")
    if reference_moment.tzinfo is None or reference_moment.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")
    return cleaned


def _legacy_router_envelope(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
    life_context: dict[str, Any] | None,
) -> dict[str, Any]:
    """Compatibility adapter for the historical API router seam.

    The production path uses ``answer_unified_question_v1``. This adapter only
    activates when a caller/test explicitly replaces the module-level legacy
    router symbol, preserving the pre-hardening extension seam without changing
    normal production routing.
    """
    if life_context is None:
        routed = route_top_level_question_v1(chart, question, reference_moment)
    else:
        routed = route_top_level_question_v1(
            chart,
            question,
            reference_moment,
            life_context=life_context,
        )
    if not isinstance(routed, dict):
        raise RuntimeError("Top-level question router returned an invalid response.")
    available = bool(routed.get("available"))
    return {
        "api_contract_version": "v1",
        "status": "answered" if available else "unsupported",
        "question": question,
        "reference_moment": reference_moment.isoformat(),
        "domain": routed.get("domain"),
        "route": routed.get("route") or "unsupported",
        "answer": routed.get("answer") or routed.get("reason"),
        "limitation": routed.get("limitation"),
        "result": routed,
        "meta": {
            "deterministic_router": True,
            "reality_override_enabled": life_context is not None,
            "guaranteed_outcome": False,
        },
    }


def _answer_question_service(
    chart: dict[str, Any],
    question: str,
    reference_moment: datetime,
    life_context: dict[str, Any] | None,
) -> dict[str, Any]:
    # New hardening tests/integrations may replace the service seam directly.
    if answer_unified_question_v1 is not _ORIGINAL_ANSWER_UNIFIED_QUESTION_V1:
        return answer_unified_question_v1(
            chart,
            question,
            reference_moment,
            life_context=life_context,
        )
    # Preserve the legacy module-level router seam used by existing callers.
    if route_top_level_question_v1 is not _ORIGINAL_ROUTE_TOP_LEVEL_QUESTION_V1:
        return _legacy_router_envelope(
            chart,
            question,
            reference_moment,
            life_context,
        )
    return answer_unified_question_v1(
        chart,
        question,
        reference_moment,
        life_context=life_context,
    )


@router.post("/api/v1/question")
def answer_astroai_question_v1(payload: AstroAIQuestionV1Request):
    """Production-facing natural-language endpoint across mature AstroAI domains."""
    try:
        cleaned_question = _validate_transport_basics(
            payload.question,
            payload.reference_moment,
        )
        chart = build_chart(payload.birth)
        effective_context = _effective_life_context(payload)
        response = _answer_question_service(
            chart,
            cleaned_question,
            payload.reference_moment,
            effective_context,
        )

        routed = response.get("result", {})
        next_life_context = routed.get("life_context") or effective_context
        return {
            **response,
            "birth": chart.get("birth", {}),
            "life_context": routed.get("life_context"),
            "next_life_context": next_life_context,
            "reality_reconciliation": routed.get("reality_reconciliation"),
            "disclaimer": (
                "AstroAI provides symbolic astrological reasoning rather than guaranteed real-world outcomes. "
                "Known facts override predictive assumptions; only user-confirmed achieved milestones are treated as known facts, "
                "while likely_pending remains non-factual. Professional medical, legal, financial or other specialist advice "
                "takes priority where relevant."
            ),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AstroAI question routing failed: {exc}",
        ) from exc
