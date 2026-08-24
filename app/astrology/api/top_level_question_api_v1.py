from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.astrology.features.life_context_v1 import merge_life_context_v1, normalize_life_context_v1
from app.models.chart import BirthInput
from app.services.chart_service import build_chart
from app.services.unified_question_service_v1 import answer_unified_question_v1


router = APIRouter(tags=["AstroAI Questions"])


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


@router.post("/api/v1/question")
def answer_astroai_question_v1(payload: AstroAIQuestionV1Request):
    """Production-facing natural-language endpoint across mature AstroAI domains."""
    try:
        chart = build_chart(payload.birth)
        effective_context = _effective_life_context(payload)
        response = answer_unified_question_v1(
            chart,
            payload.question,
            payload.reference_moment,
            life_context=effective_context,
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
