from pathlib import Path

from app.storage.profile_store_v1 import ProfileStoreV1


def _store(tmp_path: Path) -> ProfileStoreV1:
    return ProfileStoreV1(str(tmp_path / "profiles.db"))


def test_user_profile_persists_across_store_instances(tmp_path):
    first = _store(tmp_path)
    created = first.upsert_user(
        "user_1",
        email="u1@example.com",
        display_name="User One",
        locale="en-IN",
        timezone_name="Asia/Kolkata",
    )
    assert created["user_id"] == "user_1"

    second = _store(tmp_path)
    loaded = second.get_user("user_1")
    assert loaded is not None
    assert loaded["display_name"] == "User One"
    assert loaded["timezone"] == "Asia/Kolkata"


def test_birth_profiles_are_owned_and_isolated_by_user(tmp_path):
    store = _store(tmp_path)
    for user_id in ("user_1", "user_2"):
        store.upsert_user(user_id, email=None, display_name=None, locale=None, timezone_name=None)

    profile = store.create_birth_profile(
        "user_1",
        label="Me",
        birth_date="2000-04-04",
        birth_time="14:04:00",
        place="Borivali, Mumbai",
        is_default=True,
    )
    assert store.get_birth_profile("user_1", profile["profile_id"]) is not None
    assert store.get_birth_profile("user_2", profile["profile_id"]) is None
    assert store.list_birth_profiles("user_2") == []


def test_setting_new_default_unsets_previous_default(tmp_path):
    store = _store(tmp_path)
    store.upsert_user("user_1", email=None, display_name=None, locale=None, timezone_name=None)
    first = store.create_birth_profile(
        "user_1", label="Primary", birth_date="2000-04-04", birth_time="14:04:00", place="Mumbai", is_default=True
    )
    second = store.create_birth_profile(
        "user_1", label="Alternate", birth_date="2001-05-05", birth_time="09:30:00", place="Pune", is_default=True
    )
    profiles = store.list_birth_profiles("user_1")
    defaults = [p for p in profiles if p["is_default"]]
    assert len(defaults) == 1
    assert defaults[0]["profile_id"] == second["profile_id"]
    assert store.get_birth_profile("user_1", first["profile_id"])["is_default"] is False


def test_birth_profile_update_and_delete_are_owner_scoped(tmp_path):
    store = _store(tmp_path)
    for user_id in ("owner", "other"):
        store.upsert_user(user_id, email=None, display_name=None, locale=None, timezone_name=None)
    profile = store.create_birth_profile(
        "owner", label="Original", birth_date="2000-04-04", birth_time="14:04:00", place="Mumbai", is_default=True
    )

    assert store.update_birth_profile("other", profile["profile_id"], {"label": "Hacked"}) is None
    updated = store.update_birth_profile("owner", profile["profile_id"], {"label": "Updated", "place": "Borivali"})
    assert updated is not None
    assert updated["label"] == "Updated"
    assert updated["place"] == "Borivali"

    assert store.delete_birth_profile("other", profile["profile_id"]) is False
    assert store.delete_birth_profile("owner", profile["profile_id"]) is True
    assert store.get_birth_profile("owner", profile["profile_id"]) is None
