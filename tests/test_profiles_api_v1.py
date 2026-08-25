from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.auth_v1 import AuthenticatedUserProfile, get_current_user
from app.api import profiles_v1
from app.storage.profile_store_v1 import ProfileStoreV1


def _app(tmp_path: Path, user_id: str = "user_1") -> tuple[FastAPI, ProfileStoreV1]:
    app = FastAPI()
    app.include_router(profiles_v1.router)
    store = ProfileStoreV1(str(tmp_path / "profiles-api.db"))
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUserProfile(
        user_id=user_id,
        email=f"{user_id}@example.com",
        display_name="Token Name",
        locale="en-IN",
        timezone="Asia/Kolkata",
        email_verified=True,
    )
    app.dependency_overrides[profiles_v1._store] = lambda: store
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
