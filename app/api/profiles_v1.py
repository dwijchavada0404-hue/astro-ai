from __future__ import annotations

from datetime import date as Date, time as Time
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.api.auth_v1 import AuthenticatedUserProfile, get_current_user
from app.core.settings import Settings, get_settings
from app.storage.profile_store_v1 import ProfileStoreV1


router = APIRouter(prefix="/api/v1", tags=["profiles"])


class UserProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    locale: str | None = Field(default=None, max_length=35)
    timezone: str | None = Field(default=None, max_length=100)


class BirthProfileCreate(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    date: Date
    time: Time
    place: str = Field(min_length=2, max_length=200)
    is_default: bool = False


class BirthProfileUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=80)
    date: Date | None = None
    time: Time | None = None
    place: str | None = Field(default=None, min_length=2, max_length=200)
    is_default: bool | None = None


def _store(settings: Settings = Depends(get_settings)) -> ProfileStoreV1:
    return ProfileStoreV1(settings.profile_database_path)


def _sync_identity(store: ProfileStoreV1, user: AuthenticatedUserProfile) -> dict:
    existing = store.get_user(user.user_id)
    return store.upsert_user(
        user.user_id,
        email=user.email,
        display_name=(existing or {}).get("display_name") or user.display_name,
        locale=(existing or {}).get("locale") or user.locale,
        timezone_name=(existing or {}).get("timezone") or user.timezone,
    )


@router.get("/profile")
def get_profile(
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
):
    return {"profile": _sync_identity(store, user)}


@router.put("/profile")
def update_profile(
    payload: UserProfileUpdate,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
):
    current = _sync_identity(store, user)
    return {
        "profile": store.upsert_user(
            user.user_id,
            email=user.email,
            display_name=payload.display_name if payload.display_name is not None else current.get("display_name"),
            locale=payload.locale if payload.locale is not None else current.get("locale"),
            timezone_name=payload.timezone if payload.timezone is not None else current.get("timezone"),
        )
    }


@router.post("/birth-profiles", status_code=status.HTTP_201_CREATED)
def create_birth_profile(
    payload: BirthProfileCreate,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
):
    _sync_identity(store, user)
    existing = store.list_birth_profiles(user.user_id)
    is_default = payload.is_default or not existing
    profile = store.create_birth_profile(
        user.user_id,
        label=payload.label,
        birth_date=payload.date.isoformat(),
        birth_time=payload.time.isoformat(),
        place=payload.place,
        is_default=is_default,
    )
    return {"birth_profile": profile}


@router.get("/birth-profiles")
def list_birth_profiles(
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
):
    _sync_identity(store, user)
    return {"birth_profiles": store.list_birth_profiles(user.user_id)}


@router.get("/birth-profiles/{profile_id}")
def get_birth_profile(
    profile_id: str,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
):
    profile = store.get_birth_profile(user.user_id, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Birth profile not found.")
    return {"birth_profile": profile}


@router.patch("/birth-profiles/{profile_id}")
def update_birth_profile(
    profile_id: str,
    payload: BirthProfileUpdate,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
):
    raw = payload.model_dump(exclude_unset=True)
    changes = {
        "label": raw.get("label"),
        "birth_date": raw["date"].isoformat() if "date" in raw else None,
        "birth_time": raw["time"].isoformat() if "time" in raw else None,
        "place": raw.get("place"),
        "is_default": raw.get("is_default"),
    }
    changes = {key: value for key, value in changes.items() if value is not None}
    profile = store.update_birth_profile(user.user_id, profile_id, changes)
    if profile is None:
        raise HTTPException(status_code=404, detail="Birth profile not found.")
    return {"birth_profile": profile}


@router.delete("/birth-profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_birth_profile(
    profile_id: str,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
):
    if not store.delete_birth_profile(user.user_id, profile_id):
        raise HTTPException(status_code=404, detail="Birth profile not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
