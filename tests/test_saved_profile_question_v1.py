from datetime import datetime, timezone

import pytest

from app.services.saved_profile_question_v1 import answer_saved_profile_question_v1
from app.storage.profile_store_v1 import ProfileStoreV1

NOW = datetime(2026, 8, 25, tzinfo=timezone.utc)


def _store(tmp_path):
    store = ProfileStoreV1(str(tmp_path / "profiles.db"))
    store.upsert_user("user-1", email="u@example.com", display_name="User", locale="en-IN", timezone_name="Asia/Kolkata")
    return store


def _add_profile(store, *, label, place, is_default=False):
    return store.create_birth_profile(
        "user-1",
        label=label,
        birth_date="2000-04-04",
        birth_time="14:04:00",
        place=place,
        is_default=is_default,
    )


def test_uses_default_profile_when_id_not_supplied(tmp_path, monkeypatch):
    store = _store(tmp_path)
    _add_profile(store, label="Other", place="Delhi", is_default=False)
    default = _add_profile(store, label="Me", place="Borivali, Mumbai", is_default=True)

    monkeypatch.setattr(
        "app.services.saved_profile_question_v1.build_chart",
        lambda payload: {"birth": {"place_query": payload.place}, "houses": {"1": {}}, "planets": {"Sun": {}}},
    )
    monkeypatch.setattr(
        "app.services.saved_profile_question_v1.answer_unified_question_v1",
        lambda chart, question, reference_moment, life_context=None: {
            "status": "answered",
            "question": question,
            "result": {"available": True, "answer": "ok"},
        },
    )

    result = answer_saved_profile_question_v1(store, "user-1", "How is my career?", NOW)
    assert result["birth_profile"]["profile_id"] == default["profile_id"]
    assert result["birth"]["place_query"] == "Borivali, Mumbai"
    assert result["birth_source"] == "saved_profile"


def test_explicit_profile_must_belong_to_user(tmp_path):
    store = _store(tmp_path)
    store.upsert_user("user-2", email=None, display_name=None, locale=None, timezone_name=None)
    foreign = store.create_birth_profile(
        "user-2",
        label="Foreign",
        birth_date="1999-01-01",
        birth_time="12:00:00",
        place="Pune",
        is_default=True,
    )
    with pytest.raises(LookupError, match="not found"):
        answer_saved_profile_question_v1(store, "user-1", "How is my career?", NOW, profile_id=foreign["profile_id"])


def test_missing_saved_profile_is_clear_error(tmp_path):
    store = _store(tmp_path)
    with pytest.raises(LookupError, match="No saved birth profile"):
        answer_saved_profile_question_v1(store, "user-1", "How is my career?", NOW)


def test_explicit_profile_is_used_when_supplied(tmp_path, monkeypatch):
    store = _store(tmp_path)
    _add_profile(store, label="Default", place="Mumbai", is_default=True)
    chosen = _add_profile(store, label="Chosen", place="Pune", is_default=False)
    monkeypatch.setattr(
        "app.services.saved_profile_question_v1.build_chart",
        lambda payload: {"birth": {"place_query": payload.place}, "houses": {"1": {}}, "planets": {"Sun": {}}},
    )
    monkeypatch.setattr(
        "app.services.saved_profile_question_v1.answer_unified_question_v1",
        lambda chart, question, reference_moment, life_context=None: {"status": "answered", "result": {"available": True}},
    )
    result = answer_saved_profile_question_v1(store, "user-1", "How is my career?", NOW, profile_id=chosen["profile_id"])
    assert result["birth_profile"]["profile_id"] == chosen["profile_id"]
    assert result["birth"]["place_query"] == "Pune"
