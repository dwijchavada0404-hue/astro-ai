from __future__ import annotations

from datetime import datetime
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.auth_v1 import AuthenticatedUserProfile, get_current_user
from app.astrology.features.life_context_v1 import merge_life_context_v1, normalize_life_context_v1
from app.astrology.api.top_level_question_api_v1 import LifeContextV1
from app.core.settings import Settings, get_settings
from app.services.saved_profile_question_v1 import answer_saved_profile_question_v1
from app.storage.profile_store_v1 import ProfileStoreV1


router = APIRouter(prefix="/api/v1", tags=["saved-profile-questions"])


class SavedProfileQuestionV1Request(BaseModel):
    birth_profile_id: str | None = Field(default=None, min_length=1, max_length=100)
    question: str = Field(min_length=1, max_length=1000)
    reference_moment: datetime
    life_context: LifeContextV1 | None = None
    life_context_updates: LifeContextV1 | None = None


def _store(settings: Settings = Depends(get_settings)) -> ProfileStoreV1:
    return ProfileStoreV1(settings.profile_database_path)


def _effective_life_context(payload: SavedProfileQuestionV1Request) -> dict | None:
    current = payload.life_context.model_dump(mode="json") if payload.life_context else None
    updates = payload.life_context_updates.model_dump(mode="json") if payload.life_context_updates else None
    if updates is not None:
        return merge_life_context_v1(current, updates)
    if current is not None:
        return normalize_life_context_v1(current)
    return None


@router.post("/profile-question")
def answer_profile_question_v1(
    payload: SavedProfileQuestionV1Request,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
):
    try:
        result = answer_saved_profile_question_v1(
            store,
            user.user_id,
            payload.question,
            payload.reference_moment,
            profile_id=payload.birth_profile_id,
            life_context=_effective_life_context(payload),
        )
        return {
            **result,
            "disclaimer": (
                "AstroAI provides symbolic astrological reasoning rather than guaranteed real-world outcomes. "
                "Known facts override predictive assumptions, and professional medical, legal, financial or other "
                "specialist advice takes priority where relevant."
            ),
        }
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Saved-profile question routing failed: {exc}") from exc
