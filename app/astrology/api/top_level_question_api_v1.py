from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.astrology.features.top_level_question_router_v1 import route_top_level_question_v1
from app.models.chart import BirthInput
from app.services.chart_service import build_chart


router = APIRouter(tags=["AstroAI Questions"])


class AstroAIQuestionV1Request(BaseModel):
    birth: BirthInput
    question: str
    reference_moment: datetime


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
        result = route_top_level_question_v1(
            chart,
            question,
            payload.reference_moment,
        )

        return {
            "birth": chart.get("birth", {}),
            "question": question,
            "reference_moment": payload.reference_moment.isoformat(),
            "domain": result.get("domain"),
            "route": result.get("route"),
            "answer": result.get("answer") or result.get("reason"),
            "result": result,
            "disclaimer": (
                "AstroAI provides symbolic astrological reasoning rather than guaranteed real-world outcomes. "
                "Known facts override predictive assumptions, and professional medical, legal, financial or other "
                "specialist advice takes priority where relevant."
            ),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AstroAI question routing failed: {exc}",
        ) from exc
