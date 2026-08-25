from __future__ import annotations

from datetime import date as Date, datetime, time as Time

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from app.api.auth_v1 import AuthenticatedUserProfile, get_current_user
from app.core.settings import Settings, get_settings
from app.models.chart import BirthInput
from app.services.chart_service import build_chart
from app.services.unified_question_service_v1 import answer_unified_question_v1
from app.storage.conversation_store_v1 import ConversationStoreV1
from app.storage.profile_store_v1 import ProfileStoreV1


router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


class ConversationCreate(BaseModel):
    title: str = Field(default="New conversation", min_length=1, max_length=120)
    birth_profile_id: str | None = None
    life_context: dict | None = None


class ConversationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    life_context: dict | None = None


class ConversationQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    reference_moment: datetime


def _conversation_store(settings: Settings = Depends(get_settings)) -> ConversationStoreV1:
    return ConversationStoreV1(settings.profile_database_path)


def _profile_store(settings: Settings = Depends(get_settings)) -> ProfileStoreV1:
    return ProfileStoreV1(settings.profile_database_path)


def _ensure_birth_profile_owned(
    store: ProfileStoreV1,
    user_id: str,
    birth_profile_id: str | None,
) -> dict | None:
    if birth_profile_id is None:
        return None
    profile = store.get_birth_profile(user_id, birth_profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Birth profile not found.")
    return profile


def _birth_input(profile: dict) -> BirthInput:
    try:
        return BirthInput(
            date=Date.fromisoformat(profile["birth_date"]),
            time=Time.fromisoformat(profile["birth_time"]),
            place=profile["place"],
        )
    except (KeyError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail="Saved birth profile is invalid.") from exc


@router.post("", status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreate,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    conversations: ConversationStoreV1 = Depends(_conversation_store),
    profiles: ProfileStoreV1 = Depends(_profile_store),
):
    _ensure_birth_profile_owned(profiles, user.user_id, payload.birth_profile_id)
    value = conversations.create_conversation(
        user.user_id,
        title=payload.title.strip(),
        birth_profile_id=payload.birth_profile_id,
        life_context=payload.life_context,
    )
    return {"conversation": value}


@router.get("")
def list_conversations(
    limit: int = Query(default=50, ge=1, le=100),
    user: AuthenticatedUserProfile = Depends(get_current_user),
    conversations: ConversationStoreV1 = Depends(_conversation_store),
):
    return {"conversations": conversations.list_conversations(user.user_id, limit=limit)}


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str,
    message_limit: int = Query(default=200, ge=1, le=500),
    user: AuthenticatedUserProfile = Depends(get_current_user),
    conversations: ConversationStoreV1 = Depends(_conversation_store),
):
    value = conversations.get_conversation(user.user_id, conversation_id)
    if value is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    messages = conversations.list_messages(user.user_id, conversation_id, limit=message_limit)
    return {"conversation": value, "messages": messages}


@router.patch("/{conversation_id}")
def update_conversation(
    conversation_id: str,
    payload: ConversationUpdate,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    conversations: ConversationStoreV1 = Depends(_conversation_store),
):
    raw = payload.model_dump(exclude_unset=True)
    value = conversations.update_conversation(
        user.user_id,
        conversation_id,
        title=raw.get("title"),
        life_context=raw.get("life_context"),
        set_life_context="life_context" in raw,
    )
    if value is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"conversation": value}


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    conversations: ConversationStoreV1 = Depends(_conversation_store),
):
    if not conversations.delete_conversation(user.user_id, conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{conversation_id}/ask")
def ask_in_conversation(
    conversation_id: str,
    payload: ConversationQuestion,
    user: AuthenticatedUserProfile = Depends(get_current_user),
    conversations: ConversationStoreV1 = Depends(_conversation_store),
    profiles: ProfileStoreV1 = Depends(_profile_store),
):
    conversation = conversations.get_conversation(user.user_id, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    birth_profile_id = conversation.get("birth_profile_id")
    if not birth_profile_id:
        raise HTTPException(
            status_code=422,
            detail="Conversation must be linked to a saved birth profile before asking astrology questions.",
        )
    profile = _ensure_birth_profile_owned(profiles, user.user_id, birth_profile_id)
    assert profile is not None
    try:
        chart = build_chart(_birth_input(profile))
        answer = answer_unified_question_v1(
            chart,
            payload.question,
            payload.reference_moment,
            life_context=conversation.get("life_context"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    user_message = conversations.add_message(
        user.user_id,
        conversation_id,
        role="user",
        content=answer.get("question") or payload.question,
        reference_moment=payload.reference_moment.isoformat(),
    )
    assistant_message = conversations.add_message(
        user.user_id,
        conversation_id,
        role="assistant",
        content=answer.get("answer"),
        domain=answer.get("domain"),
        route=answer.get("route"),
        reference_moment=answer.get("reference_moment"),
        payload=answer,
    )
    return {
        "conversation_id": conversation_id,
        "user_message": user_message,
        "assistant_message": assistant_message,
        "answer": answer,
    }
