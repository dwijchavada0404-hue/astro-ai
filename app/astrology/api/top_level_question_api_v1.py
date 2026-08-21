from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.astrology.features.life_context_v1 import merge_life_context_v1, normalize_life_context_v1
from app.astrology.features.top_level_question_router_v1 import route_top_level_question_v1
from app.models.chart import BirthInput
from app.services.chart_service import build_chart


router = APIRouter(tags=["AstroAI Questions"])


class MilestoneContextV1(BaseModel):
    state: Literal["unknown", "likely_pending", "user_confirmed_achieved"] = "unknown"
    achieved_date: date | None = None
    note: str | None = Field(default=None, max_length=500)


class LifeContextV1(BaseModel):
    milestones: dict[str, MilestoneContextV1] = Field(default_factory=dict)


class AstroAIQuestionV1Request(BaseModel):
    birth: BirthInput
    question: str
    reference_moment: datetime
    life_context: LifeContextV1 | None = None
    life_context_updates: LifeContextV1 | None = None


def _require_timezone(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("reference_moment must include a timezone offset.")


@router.post("/api/v1/question")
def answer_astroai_question_v1(payload: AstroAIQuestionV1Request):
    """Top-level natural-language question endpoint across mature AstroAI domains."""
    try:
        question = payload.question.strip()
        if not question:
            raise ValueError("question must not be empty.")
        _require_timezone(payload.reference_moment)

        chart = build_chart(payload.birth)
        current_context = payload.life_context.model_dump(mode="json") if payload.life_context else None
        context_updates = (
            payload.life_context_updates.model_dump(mode="json")
            if payload.life_context_updates
            else None
        )

        if context_updates is not None:
            effective_context = merge_life_context_v1(current_context, context_updates)
        elif current_context is not None:
            effective_context = normalize_life_context_v1(current_context)
        else:
            effective_context = None

        if effective_context is None:
            result = route_top_level_question_v1(
                chart,
                question,
                payload.reference_moment,
            )
        else:
            result = route_top_level_question_v1(
                chart,
                question,
                payload.reference_moment,
                life_context=effective_context,
            )

        next_life_context = result.get("life_context") or effective_context
        return {
            "birth": chart.get("birth", {}),
            "question": question,
            "reference_moment": payload.reference_moment.isoformat(),
            "domain": result.get("domain"),
            "route": result.get("route"),
            "answer": result.get("answer") or result.get("reason"),
            "life_context": result.get("life_context"),
            "next_life_context": next_life_context,
            "reality_reconciliation": result.get("reality_reconciliation"),
            "result": result,
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
