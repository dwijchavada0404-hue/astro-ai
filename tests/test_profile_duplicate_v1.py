from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.profiles_v1 import BirthProfileDuplicate, duplicate_birth_profile


class FakeProfileStore:
    def __init__(self, source=None):
        self.source = source
        self.created = []

    def get_birth_profile(self, user_id, profile_id):
        if self.source and user_id == "user-1" and profile_id == "source-1":
            return self.source
        return None

    def create_birth_profile(self, user_id, **values):
        created = {"profile_id": "copy-1", "user_id": user_id, **values}
        self.created.append(created)
        return created


def test_duplicate_birth_profile_creates_independent_non_default_copy():
    store = FakeProfileStore({
        "profile_id": "source-1",
        "label": "My chart",
        "birth_date": "2000-04-04",
        "birth_time": "14:04:00",
        "place": "Borivali, Mumbai",
        "is_default": True,
    })
    user = SimpleNamespace(user_id="user-1")

    result = duplicate_birth_profile(
        "source-1",
        BirthProfileDuplicate(),
        user=user,
        store=store,
    )

    assert result["birth_profile"]["label"] == "My chart copy"
    assert result["birth_profile"]["birth_date"] == "2000-04-04"
    assert result["birth_profile"]["birth_time"] == "14:04:00"
    assert result["birth_profile"]["place"] == "Borivali, Mumbai"
    assert result["birth_profile"]["is_default"] is False


def test_duplicate_birth_profile_accepts_a_correction_label():
    store = FakeProfileStore({
        "profile_id": "source-1",
        "label": "My chart",
        "birth_date": "2000-04-04",
        "birth_time": "14:04:00",
        "place": "Mumbai",
        "is_default": False,
    })

    result = duplicate_birth_profile(
        "source-1",
        BirthProfileDuplicate(label="Corrected chart"),
        user=SimpleNamespace(user_id="user-1"),
        store=store,
    )

    assert result["birth_profile"]["label"] == "Corrected chart"


def test_duplicate_birth_profile_enforces_owner_scope():
    store = FakeProfileStore({
        "profile_id": "source-1",
        "label": "Another user's chart",
        "birth_date": "2000-04-04",
        "birth_time": "14:04:00",
        "place": "Mumbai",
        "is_default": False,
    })

    with pytest.raises(HTTPException) as exc_info:
        duplicate_birth_profile(
            "source-1",
            BirthProfileDuplicate(),
            user=SimpleNamespace(user_id="user-2"),
            store=store,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Birth profile not found."
    assert store.created == []


def test_duplicate_birth_profile_keeps_generated_label_within_limit():
    store = FakeProfileStore({
        "profile_id": "source-1",
        "label": "A" * 80,
        "birth_date": "2000-04-04",
        "birth_time": "14:04:00",
        "place": "Mumbai",
        "is_default": False,
    })

    result = duplicate_birth_profile(
        "source-1",
        BirthProfileDuplicate(),
        user=SimpleNamespace(user_id="user-1"),
        store=store,
    )

    assert result["birth_profile"]["label"].endswith(" copy")
    assert len(result["birth_profile"]["label"]) <= 80
