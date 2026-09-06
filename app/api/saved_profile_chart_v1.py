from __future__ import annotations

from datetime import date, time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.auth_v1 import AuthenticatedUserProfile, get_current_user
from app.core.settings import Settings, get_settings
from app.models.chart import BirthInput
from app.services.chart_service import build_chart
from app.storage.profile_store_v1 import ProfileStoreV1


router = APIRouter(prefix="/api/v1", tags=["birth-charts"])


def _store(settings: Settings = Depends(get_settings)) -> ProfileStoreV1:
    return ProfileStoreV1(settings.database_target)


def _birth_input_from_saved_profile(profile: dict[str, Any]) -> BirthInput:
    try:
        return BirthInput(
            date=date.fromisoformat(str(profile["birth_date"])),
            time=time.fromisoformat(str(profile["birth_time"])),
            place=str(profile["place"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Saved birth profile contains invalid birth data.") from exc


@router.get("/birth-profiles/{profile_id}/chart")
def get_saved_profile_chart(
    profile_id: str,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
):
    """Calculate the deterministic birth chart owned by the authenticated user."""
    profile = store.get_birth_profile(user.user_id, profile_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Birth profile not found.")

    try:
        chart = build_chart(_birth_input_from_saved_profile(profile))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "birth_profile": {
            "profile_id": profile.get("profile_id"),
            "label": profile.get("label"),
            "is_default": bool(profile.get("is_default")),
        },
        "birth_source": "saved_profile",
        "chart": chart,
    }
