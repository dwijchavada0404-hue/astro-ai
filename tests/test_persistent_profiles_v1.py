from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.auth_v1 import AuthenticatedUserProfile, get_current_user
from app.api.profiles_v1 import _store, router
from app.storage.profile_store_v1 import ProfileStoreV1


def _user(user_id: str = "user_123") -> AuthenticatedUserProfile:
    return AuthenticatedUserProfile(
        user_id=user_id,
        email=f"{user_id}@example.com",
        display_name="Astro User",
        locale="en-IN",
        timezone="Asia/Kolkata",
        email_verified=True,
    )


def _client(tmp_path: Path, user_id: str = "user_123") -> TestClient:
    store = ProfileStoreV1(str(tmp_path / "profiles.db"))
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: _user(user_id)
    app.dependency_overrides[_store] = lambda: store
    return TestClient(app)


def test_store_persists_across_repository_instances(tmp_path):
    path = str(tmp_path / "profiles.db")
    first = ProfileStoreV1(path)
    first.upsert_user("u1", email="u1@example.com", display_name="One", locale="en-IN", timezone_name="Asia/Kolkata")
    created = first.create_birth_profile(
        "u1",
        label="My chart",
        birth_date="2000-04-04",
        birth_time="14:04:00",
        place="Mumbai",
        is_default=True,
    )

    second = ProfileStoreV1(path)
    assert second.get_user("u1")["display_name"] == "One"
    fetched = second.get_birth_profile("u1", created["profile_id"])
    assert fetched is not None
    assert fetched["place"] == "Mumbai"
    assert fetched["is_default"] is True


def test_first_birth_profile_becomes_default(tmp_path):
    client = _client(tmp_path)
    response = client.post(
        "/api/v1/birth-profiles",
        json={"label": "Primary", "date": "2000-04-04", "time": "14:04:00", "place": "Mumbai"},
    )
    assert response.status_code == 201
    assert response.json()["birth_profile"]["is_default"] is True


def test_setting_new_default_unsets_previous_default(tmp_path):
    client = _client(tmp_path)
    first = client.post(
        "/api/v1/birth-profiles",
        json={"label": "One", "date": "2000-04-04", "time": "14:04:00", "place": "Mumbai"},
    ).json()["birth_profile"]
    second = client.post(
        "/api/v1/birth-profiles",
        json={"label": "Two", "date": "2001-01-01", "time": "10:00:00", "place": "Delhi", "is_default": True},
    ).json()["birth_profile"]

    profiles = client.get("/api/v1/birth-profiles").json()["birth_profiles"]
    defaults = [p for p in profiles if p["is_default"]]
    assert len(defaults) == 1
    assert defaults[0]["profile_id"] == second["profile_id"]
    assert defaults[0]["profile_id"] != first["profile_id"]


def test_profiles_are_isolated_by_authenticated_user(tmp_path):
    path = tmp_path / "profiles.db"
    first_client = _client(tmp_path, "owner_a")
    created = first_client.post(
        "/api/v1/birth-profiles",
        json={"label": "Private", "date": "2000-04-04", "time": "14:04:00", "place": "Mumbai"},
    ).json()["birth_profile"]

    second_client = _client(tmp_path, "owner_b")
    response = second_client.get(f"/api/v1/birth-profiles/{created['profile_id']}")
    assert response.status_code == 404
    assert second_client.get("/api/v1/birth-profiles").json()["birth_profiles"] == []
    assert path.exists()


def test_user_profile_and_birth_profile_update_delete(tmp_path):
    client = _client(tmp_path)
    profile = client.put(
        "/api/v1/profile",
        json={"display_name": "Dwij", "locale": "en-IN", "timezone": "Asia/Kolkata"},
    ).json()["profile"]
    assert profile["display_name"] == "Dwij"

    created = client.post(
        "/api/v1/birth-profiles",
        json={"label": "Old", "date": "2000-04-04", "time": "14:04:00", "place": "Mumbai"},
    ).json()["birth_profile"]
    profile_id = created["profile_id"]

    updated = client.patch(
        f"/api/v1/birth-profiles/{profile_id}",
        json={"label": "Updated", "place": "Borivali, Mumbai"},
    ).json()["birth_profile"]
    assert updated["label"] == "Updated"
    assert updated["place"] == "Borivali, Mumbai"

    assert client.delete(f"/api/v1/birth-profiles/{profile_id}").status_code == 204
    assert client.get(f"/api/v1/birth-profiles/{profile_id}").status_code == 404
