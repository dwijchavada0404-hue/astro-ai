from __future__ import annotations

from fastapi import HTTPException
import pytest

from app.api.auth_v1 import AuthenticatedUserProfile
from app.api import saved_profile_chart_v1 as module


class FakeProfileStore:
    def __init__(self, profiles: dict[tuple[str, str], dict]):
        self.profiles = profiles
        self.calls: list[tuple[str, str]] = []

    def get_birth_profile(self, user_id: str, profile_id: str):
        self.calls.append((user_id, profile_id))
        return self.profiles.get((user_id, profile_id))


def test_saved_profile_chart_uses_authenticated_owner_and_returns_deterministic_chart(monkeypatch):
    profile = {
        "profile_id": "profile-1",
        "label": "My chart",
        "birth_date": "2000-04-04",
        "birth_time": "14:04:00",
        "place": "Mumbai, India",
        "is_default": True,
    }
    store = FakeProfileStore({("user-1", "profile-1"): profile})
    captured = {}

    def fake_build_chart(birth):
        captured["birth"] = birth
        return {"birth": {"place": birth.place}, "ascendant": {"sign": "Leo"}}

    monkeypatch.setattr(module, "build_chart", fake_build_chart)

    response = module.get_saved_profile_chart(
        "profile-1",
        user=AuthenticatedUserProfile(user_id="user-1"),
        store=store,
    )

    assert store.calls == [("user-1", "profile-1")]
    assert captured["birth"].date.isoformat() == "2000-04-04"
    assert captured["birth"].time.isoformat() == "14:04:00"
    assert captured["birth"].place == "Mumbai, India"
    assert response["birth_source"] == "saved_profile"
    assert response["birth_profile"] == {
        "profile_id": "profile-1",
        "label": "My chart",
        "is_default": True,
    }
    assert response["chart"]["ascendant"]["sign"] == "Leo"


def test_saved_profile_chart_does_not_read_another_users_profile(monkeypatch):
    other_profile = {
        "profile_id": "profile-1",
        "label": "Other chart",
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "place": "Delhi, India",
        "is_default": False,
    }
    store = FakeProfileStore({("other-user", "profile-1"): other_profile})
    called = False

    def fake_build_chart(_birth):
        nonlocal called
        called = True
        return {}

    monkeypatch.setattr(module, "build_chart", fake_build_chart)

    with pytest.raises(HTTPException) as exc:
        module.get_saved_profile_chart(
            "profile-1",
            user=AuthenticatedUserProfile(user_id="user-1"),
            store=store,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Birth profile not found."
    assert called is False


def test_saved_profile_chart_rejects_corrupt_saved_birth_data(monkeypatch):
    store = FakeProfileStore({
        ("user-1", "profile-1"): {
            "profile_id": "profile-1",
            "label": "Broken chart",
            "birth_date": "not-a-date",
            "birth_time": "14:04:00",
            "place": "Mumbai, India",
            "is_default": False,
        }
    })
    called = False

    def fake_build_chart(_birth):
        nonlocal called
        called = True
        return {}

    monkeypatch.setattr(module, "build_chart", fake_build_chart)

    with pytest.raises(HTTPException) as exc:
        module.get_saved_profile_chart(
            "profile-1",
            user=AuthenticatedUserProfile(user_id="user-1"),
            store=store,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Saved birth profile contains invalid birth data."
    assert called is False
