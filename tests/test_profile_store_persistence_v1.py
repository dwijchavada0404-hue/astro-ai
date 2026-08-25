from pathlib import Path

from app.storage.profile_store_v1 import ProfileStoreV1, SCHEMA_VERSION


def _store(tmp_path: Path) -> ProfileStoreV1:
    return ProfileStoreV1(str(tmp_path / "profiles.db"))


def _user(store: ProfileStoreV1, user_id: str = "user_1") -> None:
    store.upsert_user(
        user_id,
        email=f"{user_id}@example.com",
        display_name="Astro User",
        locale="en-IN",
        timezone_name="Asia/Kolkata",
    )


def _birth(store: ProfileStoreV1, user_id: str, label: str, *, is_default: bool = False):
    return store.create_birth_profile(
        user_id,
        label=label,
        birth_date="2000-04-04",
        birth_time="14:04:00",
        place="Mumbai, India",
        is_default=is_default,
    )


def test_schema_version_is_recorded(tmp_path):
    store = _store(tmp_path)
    assert store.schema_version() == SCHEMA_VERSION == 1


def test_profiles_persist_across_store_instances(tmp_path):
    database_path = str(tmp_path / "profiles.db")
    first = ProfileStoreV1(database_path)
    _user(first)
    created = _birth(first, "user_1", "Me")

    second = ProfileStoreV1(database_path)
    loaded = second.get_birth_profile("user_1", created["profile_id"])
    assert loaded is not None
    assert loaded["label"] == "Me"
    assert loaded["is_default"] is True


def test_first_birth_profile_is_always_default(tmp_path):
    store = _store(tmp_path)
    _user(store)
    created = _birth(store, "user_1", "Me", is_default=False)
    assert created["is_default"] is True


def test_setting_new_default_demotes_previous_default(tmp_path):
    store = _store(tmp_path)
    _user(store)
    first = _birth(store, "user_1", "Me")
    second = _birth(store, "user_1", "Alternate", is_default=True)

    profiles = store.list_birth_profiles("user_1")
    defaults = [profile for profile in profiles if profile["is_default"]]
    assert len(defaults) == 1
    assert defaults[0]["profile_id"] == second["profile_id"]
    assert store.get_birth_profile("user_1", first["profile_id"])["is_default"] is False


def test_unsetting_default_promotes_another_profile(tmp_path):
    store = _store(tmp_path)
    _user(store)
    first = _birth(store, "user_1", "Me")
    second = _birth(store, "user_1", "Alternate")

    changed = store.update_birth_profile("user_1", first["profile_id"], {"is_default": False})
    assert changed is not None
    assert changed["is_default"] is False
    assert store.get_birth_profile("user_1", second["profile_id"])["is_default"] is True


def test_only_profile_cannot_be_left_without_default(tmp_path):
    store = _store(tmp_path)
    _user(store)
    only = _birth(store, "user_1", "Me")

    changed = store.update_birth_profile("user_1", only["profile_id"], {"is_default": False})
    assert changed is not None
    assert changed["is_default"] is True


def test_deleting_default_promotes_remaining_profile(tmp_path):
    store = _store(tmp_path)
    _user(store)
    first = _birth(store, "user_1", "Me")
    second = _birth(store, "user_1", "Alternate")

    assert store.delete_birth_profile("user_1", first["profile_id"]) is True
    remaining = store.get_birth_profile("user_1", second["profile_id"])
    assert remaining is not None
    assert remaining["is_default"] is True


def test_birth_profiles_are_strictly_owned_by_user(tmp_path):
    store = _store(tmp_path)
    _user(store, "user_1")
    _user(store, "user_2")
    profile = _birth(store, "user_1", "Private")

    assert store.get_birth_profile("user_2", profile["profile_id"]) is None
    assert store.update_birth_profile("user_2", profile["profile_id"], {"label": "Hijacked"}) is None
    assert store.delete_birth_profile("user_2", profile["profile_id"]) is False
    assert store.get_birth_profile("user_1", profile["profile_id"])["label"] == "Private"


def test_deleting_user_cascades_owned_birth_profiles(tmp_path):
    store = _store(tmp_path)
    _user(store)
    profile = _birth(store, "user_1", "Me")

    assert store.delete_user("user_1") is True
    assert store.get_user("user_1") is None
    assert store.get_birth_profile("user_1", profile["profile_id"]) is None


def test_birth_profile_requires_existing_owner(tmp_path):
    store = _store(tmp_path)
    try:
        _birth(store, "missing_user", "No owner")
    except ValueError as exc:
        assert "user profile must exist" in str(exc).lower()
    else:
        raise AssertionError("Expected owner validation error")
