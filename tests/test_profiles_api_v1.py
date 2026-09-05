from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.auth_v1 import AuthenticatedUserProfile, get_current_user
from app.api import profiles_v1
from app.storage.conversation_store_v1 import ConversationStoreV1
from app.storage.profile_store_v1 import ProfileStoreV1


def _app(tmp_path: Path, user_id: str = "user_1") -> tuple[FastAPI, ProfileStoreV1]:
    app = FastAPI()
    app.include_router(profiles_v1.router)
    store = ProfileStoreV1(str(tmp_path / "profiles-api.db"))
    conversations = ConversationStoreV1(str(tmp_path / "profiles-api.db"))
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUserProfile(
        user_id=user_id,
        email=f"{user_id}@example.com",
        display_name="Token Name",
        locale="en-IN",
        timezone="Asia/Kolkata",
        email_verified=True,
    )
    app.dependency_overrides[profiles_v1._store] = lambda: store
    app.dependency_overrides[profiles_v1._conversation_store] = lambda: conversations
    return app, store


def test_profile_sync_and_update(tmp_path):
    app, _ = _app(tmp_path)
    client = TestClient(app)

    response = client.get("/api/v1/profile")
    assert response.status_code == 200
    assert response.json()["profile"]["display_name"] == "Token Name"

    updated = client.put("/api/v1/profile", json={"display_name": "Saved Name", "timezone": "Asia/Kolkata"})
    assert updated.status_code == 200
    assert updated.json()["profile"]["display_name"] == "Saved Name"

    again = client.get("/api/v1/profile")
    assert again.json()["profile"]["display_name"] == "Saved Name"


def test_personal_data_export_contains_only_the_authenticated_users_records(tmp_path):
    app, store = _app(tmp_path)
    client = TestClient(app)
    profile = client.post(
        "/api/v1/birth-profiles",
        json={"label": "Me", "date": "2000-04-04", "time": "14:04:00", "place": "Mumbai"},
    ).json()["birth_profile"]
    conversations = ConversationStoreV1(str(tmp_path / "profiles-api.db"))
    conversation = conversations.create_conversation("user_1", title="Private history", birth_profile_id=profile["profile_id"])
    conversations.add_message("user_1", conversation["conversation_id"], role="user", content="Private question")
    store.upsert_user("other", email="other@example.com", display_name="Other", locale="en-IN", timezone_name="Asia/Kolkata")
    other_profile = store.create_birth_profile("other", label="Other", birth_date="2001-01-01", birth_time="10:00:00", place="Pune", is_default=True)
    conversations.create_conversation("other", title="Other history", birth_profile_id=other_profile["profile_id"])

    response = client.get("/api/v1/profile/export")

    assert response.status_code == 200
    payload = response.json()
    assert payload["export_version"] == 1
    assert payload["profile"]["user_id"] == "user_1"
    assert [item["label"] for item in payload["birth_profiles"]] == ["Me"]
    assert len(payload["conversations"]) == 1
    assert payload["conversations"][0]["messages"][0]["content"] == "Private question"


def test_delete_personal_data_removes_profiles_conversations_and_messages(tmp_path):
    app, store = _app(tmp_path)
    client = TestClient(app)
    profile = client.post(
        "/api/v1/birth-profiles",
        json={"label": "Me", "date": "2000-04-04", "time": "14:04:00", "place": "Mumbai"},
    ).json()["birth_profile"]
    conversations = ConversationStoreV1(str(tmp_path / "profiles-api.db"))
    conversation = conversations.create_conversation(
        "user_1", title="Private history", birth_profile_id=profile["profile_id"]
    )
    conversations.add_message("user_1", conversation["conversation_id"], role="user", content="Private question")

    response = client.delete("/api/v1/profile")

    assert response.status_code == 204
    assert store.get_user("user_1") is None
    assert store.list_birth_profiles("user_1") == []
    assert conversations.list_conversations("user_1") == []
    assert conversations.get_conversation("user_1", conversation["conversation_id"]) is None


def test_birth_profile_crud_and_first_profile_defaults(tmp_path):
    app, _ = _app(tmp_path)
    client = TestClient(app)

    created = client.post(
        "/api/v1/birth-profiles",
        json={"label": "Me", "date": "2000-04-04", "time": "14:04:00", "place": "Borivali, Mumbai"},
    )
    assert created.status_code == 201
    profile = created.json()["birth_profile"]
    assert profile["is_default"] is True
    profile_id = profile["profile_id"]

    listed = client.get("/api/v1/birth-profiles")
    assert listed.status_code == 200
    assert len(listed.json()["birth_profiles"]) == 1

    patched = client.patch(f"/api/v1/birth-profiles/{profile_id}", json={"label": "Primary chart"})
    assert patched.status_code == 200
    assert patched.json()["birth_profile"]["label"] == "Primary chart"

    fetched = client.get(f"/api/v1/birth-profiles/{profile_id}")
    assert fetched.status_code == 200
    assert fetched.json()["birth_profile"]["place"] == "Borivali, Mumbai"

    deleted = client.delete(f"/api/v1/birth-profiles/{profile_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/birth-profiles/{profile_id}").status_code == 404


def test_user_cannot_access_another_users_birth_profile(tmp_path):
    app_owner, store = _app(tmp_path, "owner")
    owner_client = TestClient(app_owner)
    profile_id = owner_client.post(
        "/api/v1/birth-profiles",
        json={"label": "Owner", "date": "2000-04-04", "time": "14:04:00", "place": "Mumbai"},
    ).json()["birth_profile"]["profile_id"]

    app_other = FastAPI()
    app_other.include_router(profiles_v1.router)
    app_other.dependency_overrides[get_current_user] = lambda: AuthenticatedUserProfile(user_id="other")
    app_other.dependency_overrides[profiles_v1._store] = lambda: store
    other_client = TestClient(app_other)

    assert other_client.get(f"/api/v1/birth-profiles/{profile_id}").status_code == 404
    assert other_client.patch(f"/api/v1/birth-profiles/{profile_id}", json={"label": "Nope"}).status_code == 404
    assert other_client.delete(f"/api/v1/birth-profiles/{profile_id}").status_code == 404


def test_birth_profile_linked_to_conversation_cannot_be_deleted(tmp_path):
    app, _ = _app(tmp_path)
    client = TestClient(app)
    profile_id = client.post(
        "/api/v1/birth-profiles",
        json={"label": "Me", "date": "2000-04-04", "time": "14:04:00", "place": "Mumbai"},
    ).json()["birth_profile"]["profile_id"]
    ConversationStoreV1(str(tmp_path / "profiles-api.db")).create_conversation(
        "user_1", title="Protected history", birth_profile_id=profile_id
    )

    response = client.delete(f"/api/v1/birth-profiles/{profile_id}")

    assert response.status_code == 409
    assert response.json()["detail"] == "Delete conversations linked to this birth profile before deleting the profile."
    assert client.get(f"/api/v1/birth-profiles/{profile_id}").status_code == 200


def test_birth_details_linked_to_conversation_cannot_be_changed(tmp_path):
    app, _ = _app(tmp_path)
    client = TestClient(app)
    profile_id = client.post(
        "/api/v1/birth-profiles",
        json={"label": "Me", "date": "2000-04-04", "time": "14:04:00", "place": "Mumbai"},
    ).json()["birth_profile"]["profile_id"]
    ConversationStoreV1(str(tmp_path / "profiles-api.db")).create_conversation(
        "user_1", title="Protected history", birth_profile_id=profile_id
    )

    blocked = client.patch(f"/api/v1/birth-profiles/{profile_id}", json={"place": "Pune"})
    renamed = client.patch(f"/api/v1/birth-profiles/{profile_id}", json={"label": "Primary chart"})

    assert blocked.status_code == 409
    assert blocked.json()["detail"] == "Create a new birth profile to change birth details used by existing conversations."
    assert renamed.status_code == 200
    assert renamed.json()["birth_profile"]["label"] == "Primary chart"
