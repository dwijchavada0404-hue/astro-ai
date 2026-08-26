from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import profiles_v1
from app.api.auth_v1 import AuthenticatedUserProfile
from app.storage.profile_store_v1 import ProfileStoreV1


NOW = datetime(2026, 8, 25, 10, 0, tzinfo=timezone.utc)


def _user(user_id: str = "user_123") -> AuthenticatedUserProfile:
    return AuthenticatedUserProfile(user_id=user_id, email="user@example.com", display_name="Astro User")


def _app(store: ProfileStoreV1, user_id: str = "user_123") -> FastAPI:
    app = FastAPI()
    app.include_router(profiles_v1.router)
    app.dependency_overrides[profiles_v1.get_current_user] = lambda: _user(user_id)
    app.dependency_overrides[profiles_v1._store] = lambda: store
    return app


def _saved_profile(store: ProfileStoreV1, user_id: str = "user_123") -> dict:
    store.upsert_user(user_id, email="user@example.com", display_name="Astro User", locale="en-IN", timezone_name="Asia/Kolkata")
    return store.create_birth_profile(
        user_id,
        label="My chart",
        birth_date="2000-04-04",
        birth_time="14:04:00",
        place="Borivali, Mumbai",
        is_default=True,
    )


def test_saved_profile_question_reuses_persisted_birth_data(tmp_path, monkeypatch):
    store = ProfileStoreV1(str(tmp_path / "profiles.db"))
    profile = _saved_profile(store)
    captured = {}

    def fake_build_chart(birth):
        captured["birth"] = birth
        return {"birth": {"ok": True}}

    def fake_answer(chart, question, reference_moment, life_context=None):
        captured["question"] = question
        captured["reference_moment"] = reference_moment
        captured["life_context"] = life_context
        return {"status": "answered", "answer": "saved profile answer"}

    monkeypatch.setattr(profiles_v1, "build_chart", fake_build_chart)
    monkeypatch.setattr(profiles_v1, "answer_unified_question_v1", fake_answer)

    response = TestClient(_app(store)).post(
        f"/api/v1/birth-profiles/{profile['profile_id']}/question",
        json={
            "question": "When is career growth stronger?",
            "reference_moment": NOW.isoformat(),
            "life_context": {"career_stability": {"status": "unknown"}},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["birth_profile"]["profile_id"] == profile["profile_id"]
    assert body["answer"]["answer"] == "saved profile answer"
    assert captured["birth"].date.isoformat() == "2000-04-04"
    assert captured["birth"].time.isoformat() == "14:04:00"
    assert captured["birth"].place == "Borivali, Mumbai"
    assert captured["question"] == "When is career growth stronger?"


def test_saved_profile_question_enforces_profile_ownership(tmp_path):
    store = ProfileStoreV1(str(tmp_path / "profiles.db"))
    profile = _saved_profile(store, "owner_user")
    response = TestClient(_app(store, "other_user")).post(
        f"/api/v1/birth-profiles/{profile['profile_id']}/question",
        json={"question": "How is my career?", "reference_moment": NOW.isoformat()},
    )
    assert response.status_code == 404


def test_first_saved_birth_profile_becomes_default(tmp_path):
    store = ProfileStoreV1(str(tmp_path / "profiles.db"))
    client = TestClient(_app(store))
    response = client.post(
        "/api/v1/birth-profiles",
        json={"label": "Primary", "date": "2000-04-04", "time": "14:04:00", "place": "Borivali, Mumbai"},
    )
    assert response.status_code == 201
    assert response.json()["birth_profile"]["is_default"] is True


def test_question_requires_timezone_aware_reference_moment(tmp_path, monkeypatch):
    store = ProfileStoreV1(str(tmp_path / "profiles.db"))
    profile = _saved_profile(store)
    monkeypatch.setattr(profiles_v1, "build_chart", lambda birth: {"birth": {"ok": True}})
    response = TestClient(_app(store)).post(
        f"/api/v1/birth-profiles/{profile['profile_id']}/question",
        json={"question": "How is my career?", "reference_moment": "2026-08-25T10:00:00"},
    )
    assert response.status_code == 400
    assert "timezone" in response.json()["detail"].lower()
