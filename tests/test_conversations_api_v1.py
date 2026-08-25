from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.auth_v1 import AuthenticatedUserProfile, get_current_user
from app.api import conversations_v1
from app.storage.conversation_store_v1 import ConversationStoreV1
from app.storage.profile_store_v1 import ProfileStoreV1


NOW = datetime(2026, 8, 25, 10, 0, tzinfo=timezone.utc)


def _app(tmp_path: Path, user_id: str = "user_1"):
    database = str(tmp_path / "conversation-api.db")
    conversations = ConversationStoreV1(database)
    profiles = ProfileStoreV1(database)
    profiles.upsert_user(user_id, email=f"{user_id}@example.com", display_name="User", locale="en-IN", timezone_name="Asia/Kolkata")
    app = FastAPI()
    app.include_router(conversations_v1.router)
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUserProfile(user_id=user_id)
    app.dependency_overrides[conversations_v1._conversation_store] = lambda: conversations
    app.dependency_overrides[conversations_v1._profile_store] = lambda: profiles
    return app, conversations, profiles


def _birth_profile(profiles: ProfileStoreV1, user_id: str = "user_1") -> str:
    return profiles.create_birth_profile(
        user_id,
        label="Me",
        birth_date="2000-04-04",
        birth_time="14:04:00",
        place="Borivali, Mumbai",
        is_default=True,
    )["profile_id"]


def test_conversation_crud_is_authenticated_and_owned(tmp_path):
    app, _, profiles = _app(tmp_path)
    profile_id = _birth_profile(profiles)
    client = TestClient(app)
    created = client.post("/api/v1/conversations", json={"title": "My reading", "birth_profile_id": profile_id})
    assert created.status_code == 201
    conversation_id = created.json()["conversation"]["conversation_id"]

    listed = client.get("/api/v1/conversations")
    assert listed.status_code == 200
    assert listed.json()["conversations"][0]["conversation_id"] == conversation_id

    updated = client.patch(f"/api/v1/conversations/{conversation_id}", json={"title": "Renamed"})
    assert updated.status_code == 200
    assert updated.json()["conversation"]["title"] == "Renamed"

    fetched = client.get(f"/api/v1/conversations/{conversation_id}")
    assert fetched.status_code == 200
    assert fetched.json()["messages"] == []

    deleted = client.delete(f"/api/v1/conversations/{conversation_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/conversations/{conversation_id}").status_code == 404


def test_other_users_birth_profile_cannot_be_linked(tmp_path):
    app, _, profiles = _app(tmp_path, "owner")
    owner_profile = _birth_profile(profiles, "owner")

    other_app = FastAPI()
    other_app.include_router(conversations_v1.router)
    conversations = ConversationStoreV1(profiles.database_path)
    other_app.dependency_overrides[get_current_user] = lambda: AuthenticatedUserProfile(user_id="other")
    other_app.dependency_overrides[conversations_v1._conversation_store] = lambda: conversations
    other_app.dependency_overrides[conversations_v1._profile_store] = lambda: profiles
    response = TestClient(other_app).post(
        "/api/v1/conversations",
        json={"title": "No access", "birth_profile_id": owner_profile},
    )
    assert response.status_code == 404


def test_ask_uses_saved_birth_profile_and_persists_both_turns(tmp_path, monkeypatch):
    app, conversations, profiles = _app(tmp_path)
    profile_id = _birth_profile(profiles)
    client = TestClient(app)
    conversation_id = client.post(
        "/api/v1/conversations",
        json={"title": "Career", "birth_profile_id": profile_id, "life_context": {"career_stability": "likely_pending"}},
    ).json()["conversation"]["conversation_id"]

    monkeypatch.setattr(conversations_v1, "build_chart", lambda birth: {"birth": birth.model_dump(mode="json"), "houses": {"10": {}}, "planets": {}})
    monkeypatch.setattr(
        conversations_v1,
        "answer_unified_question_v1",
        lambda chart, question, reference_moment, life_context=None: {
            "api_contract_version": "v1",
            "status": "answered",
            "question": question.strip(),
            "reference_moment": reference_moment.isoformat(),
            "domain": "career",
            "route": "top_level_to_career",
            "answer": "Career answer",
            "limitation": "bounded",
            "result": {"available": True},
            "meta": {"deterministic_router": True, "reality_override_enabled": True, "guaranteed_outcome": False},
        },
    )

    response = client.post(
        f"/api/v1/conversations/{conversation_id}/ask",
        json={"question": " When is career stability likely? ", "reference_moment": NOW.isoformat()},
    )
    assert response.status_code == 200
    assert response.json()["answer"]["domain"] == "career"

    messages = conversations.list_messages("user_1", conversation_id)
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["route"] == "top_level_to_career"
    assert messages[1]["payload"]["answer"] == "Career answer"
