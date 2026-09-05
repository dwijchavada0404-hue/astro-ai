from __future__ import annotations

from datetime import date as Date, datetime, time as Time, timezone
from functools import lru_cache
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.api.auth_v1 import AuthenticatedUserProfile, get_current_user
from app.core.settings import Settings, get_settings
from app.storage.conversation_store_v1 import ConversationStoreV1
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


class BirthProfileDuplicate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=80)


class BackupBirthProfileV1(BaseModel):
    profile_id: str | None = None
    label: str = Field(min_length=1, max_length=80)
    birth_date: Date
    birth_time: Time
    place: str = Field(min_length=2, max_length=200)
    is_default: bool = False


class BackupMessageV1(BaseModel):
    role: Literal["user", "assistant"]
    content: str | None = None
    domain: str | None = Field(default=None, max_length=80)
    route: str | None = Field(default=None, max_length=120)
    reference_moment: str | None = Field(default=None, max_length=100)
    payload: dict[str, Any] | None = None


class BackupConversationV1(BaseModel):
    conversation_id: str | None = None
    title: str = Field(min_length=1, max_length=120)
    birth_profile_id: str | None = None
    life_context: dict[str, Any] | None = None
    messages: list[BackupMessageV1] = Field(default_factory=list, max_length=500)


class ProfileImportV1(BaseModel):
    export_version: int
    birth_profiles: list[BackupBirthProfileV1] = Field(default_factory=list, max_length=100)
    conversations: list[BackupConversationV1] = Field(default_factory=list, max_length=100)


def _store(settings: Settings = Depends(get_settings)) -> ProfileStoreV1:
    return ProfileStoreV1(settings.database_target)


def _conversation_store(settings: Settings = Depends(get_settings)) -> ConversationStoreV1:
    return ConversationStoreV1(settings.database_target)


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


@router.get("/profile/export")
def export_personal_data(
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
    conversations: ConversationStoreV1 = Depends(_conversation_store),
):
    """Return a portable, user-owned snapshot without exposing other users' data."""
    profile = _sync_identity(store, user)
    saved_conversations = conversations.list_conversations(user.user_id, limit=100)
    return {
        "export_version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "birth_profiles": store.list_birth_profiles(user.user_id),
        "conversations": [
            {
                **conversation,
                "messages": conversations.list_messages(
                    user.user_id,
                    conversation["conversation_id"],
                    limit=500,
                ),
            }
            for conversation in saved_conversations
        ],
    }


@router.post("/profile/import", status_code=status.HTTP_201_CREATED)
def import_personal_data(
    payload: ProfileImportV1,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
    conversations: ConversationStoreV1 = Depends(_conversation_store),
):
    """Add a portable v1 backup to the current account without overwriting existing records."""
    if payload.export_version != 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported AstroAI export version.")

    _sync_identity(store, user)
    profile_id_map: dict[str, str] = {}
    imported_profiles = 0
    imported_conversations = 0
    imported_messages = 0
    unlinked_conversations = 0

    for source in payload.birth_profiles:
        created = store.create_birth_profile(
            user.user_id,
            label=source.label,
            birth_date=source.birth_date.isoformat(),
            birth_time=source.birth_time.isoformat(),
            place=source.place,
            is_default=False,
        )
        imported_profiles += 1
        if source.profile_id:
            profile_id_map[source.profile_id] = created["profile_id"]

    for source in payload.conversations:
        mapped_profile_id = profile_id_map.get(source.birth_profile_id) if source.birth_profile_id else None
        if source.birth_profile_id and mapped_profile_id is None:
            unlinked_conversations += 1
        created = conversations.create_conversation(
            user.user_id,
            title=source.title,
            birth_profile_id=mapped_profile_id,
            life_context=source.life_context,
        )
        imported_conversations += 1
        for message in source.messages:
            conversations.add_message(
                user.user_id,
                created["conversation_id"],
                role=message.role,
                content=message.content,
                domain=message.domain,
                route=message.route,
                reference_moment=message.reference_moment,
                payload=message.payload,
            )
            imported_messages += 1

    return {
        "imported": {
            "birth_profiles": imported_profiles,
            "conversations": imported_conversations,
            "messages": imported_messages,
            "unlinked_conversations": unlinked_conversations,
        }
    }


@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
def delete_personal_data(
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
    conversations: ConversationStoreV1 = Depends(_conversation_store),
):
    conversations.delete_user_conversations(user.user_id)
    store.delete_user(user.user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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


@router.post("/birth-profiles/{profile_id}/duplicate", status_code=status.HTTP_201_CREATED)
def duplicate_birth_profile(
    profile_id: str,
    payload: BirthProfileDuplicate,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
):
    """Create an independent copy so corrected birth details never rewrite historic chats."""
    source = store.get_birth_profile(user.user_id, profile_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Birth profile not found.")
    requested_label = payload.label.strip() if payload.label is not None else ""
    label = requested_label or f"{source['label'][:73].rstrip()} copy"
    profile = store.create_birth_profile(
        user.user_id,
        label=label,
        birth_date=source["birth_date"],
        birth_time=source["birth_time"],
        place=source["place"],
        is_default=False,
    )
    return {"birth_profile": profile}


@router.patch("/birth-profiles/{profile_id}")
def update_birth_profile(
    profile_id: str,
    payload: BirthProfileUpdate,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
    conversations: ConversationStoreV1 = Depends(_conversation_store),
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
    if {"birth_date", "birth_time", "place"} & changes.keys() and conversations.has_birth_profile_references(user.user_id, profile_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Create a new birth profile to change birth details used by existing conversations.",
        )
    profile = store.update_birth_profile(user.user_id, profile_id, changes)
    if profile is None:
        raise HTTPException(status_code=404, detail="Birth profile not found.")
    return {"birth_profile": profile}


@router.delete("/birth-profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_birth_profile(
    profile_id: str,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    store: ProfileStoreV1 = Depends(_store),
    conversations: ConversationStoreV1 = Depends(_conversation_store),
):
    if store.get_birth_profile(user.user_id, profile_id) is None:
        raise HTTPException(status_code=404, detail="Birth profile not found.")
    if conversations.has_birth_profile_references(user.user_id, profile_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Delete conversations linked to this birth profile before deleting the profile.",
        )
    if not store.delete_birth_profile(user.user_id, profile_id):
        raise HTTPException(status_code=404, detail="Birth profile not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)