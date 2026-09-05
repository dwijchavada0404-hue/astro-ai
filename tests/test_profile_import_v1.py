from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.profiles_v1 import ProfileImportV1, import_personal_data


class FakeProfileStore:
    def __init__(self):
        self.user = None
        self.created = []

    def get_user(self, user_id):
        return self.user if self.user and self.user["user_id"] == user_id else None

    def upsert_user(self, user_id, *, email, display_name, locale, timezone_name):
        self.user = {
            "user_id": user_id,
            "email": email,
            "display_name": display_name,
            "locale": locale,
            "timezone": timezone_name,
        }
        return self.user

    def create_birth_profile(self, user_id, *, label, birth_date, birth_time, place, is_default):
        profile = {
            "profile_id": f"new-profile-{len(self.created) + 1}",
            "user_id": user_id,
            "label": label,
            "birth_date": birth_date,
            "birth_time": birth_time,
            "place": place,
            "is_default": bool(is_default or not self.created),
        }
        self.created.append(profile)
        return profile


class FakeConversationStore:
    def __init__(self):
        self.created = []
        self.messages = []

    def create_conversation(self, user_id, *, title, birth_profile_id=None, life_context=None):
        conversation = {
            "conversation_id": f"new-conversation-{len(self.created) + 1}",
            "user_id": user_id,
            "title": title,
            "birth_profile_id": birth_profile_id,
            "life_context": life_context,
        }
        self.created.append(conversation)
        return conversation

    def add_message(self, user_id, conversation_id, **message):
        stored = {"message_id": f"new-message-{len(self.messages) + 1}", "user_id": user_id, "conversation_id": conversation_id, **message}
        self.messages.append(stored)
        return stored


def user():
    return SimpleNamespace(
        user_id="current-user",
        email="current@example.com",
        display_name="Current User",
        locale="en-IN",
        timezone="Asia/Kolkata",
    )


def backup():
    return ProfileImportV1.model_validate({
        "export_version": 1,
        "birth_profiles": [
            {
                "profile_id": "old-profile-1",
                "label": "My chart",
                "birth_date": "2000-04-04",
                "birth_time": "14:04:00",
                "place": "Mumbai",
                "is_default": True,
            }
        ],
        "conversations": [
            {
                "conversation_id": "old-conversation-1",
                "title": "Career timing",
                "birth_profile_id": "old-profile-1",
                "life_context": {"focus": "career"},
                "messages": [
                    {"role": "user", "content": "What about my career?"},
                    {"role": "assistant", "content": "Reflective answer", "domain": "career", "payload": {"score": 2}},
                ],
            }
        ],
    })


def test_import_recreates_owned_records_with_fresh_ids_and_profile_mapping():
    profiles = FakeProfileStore()
    conversations = FakeConversationStore()

    result = import_personal_data(backup(), user(), profiles, conversations)

    assert result["imported"] == {
        "birth_profiles": 1,
        "conversations": 1,
        "messages": 2,
        "unlinked_conversations": 0,
    }
    assert profiles.created[0]["profile_id"] == "new-profile-1"
    assert profiles.created[0]["user_id"] == "current-user"
    assert conversations.created[0]["conversation_id"] == "new-conversation-1"
    assert conversations.created[0]["birth_profile_id"] == "new-profile-1"
    assert conversations.messages[0]["conversation_id"] == "new-conversation-1"
    assert conversations.messages[1]["payload"] == {"score": 2}


def test_import_never_uses_backup_identity_as_current_owner():
    profiles = FakeProfileStore()
    conversations = FakeConversationStore()
    payload = backup()

    import_personal_data(payload, user(), profiles, conversations)

    assert profiles.user["user_id"] == "current-user"
    assert all(item["user_id"] == "current-user" for item in profiles.created)
    assert all(item["user_id"] == "current-user" for item in conversations.created)
    assert all(item["user_id"] == "current-user" for item in conversations.messages)


def test_import_keeps_conversation_but_counts_missing_profile_reference_as_unlinked():
    profiles = FakeProfileStore()
    conversations = FakeConversationStore()
    payload = ProfileImportV1.model_validate({
        "export_version": 1,
        "birth_profiles": [],
        "conversations": [{
            "title": "Old conversation",
            "birth_profile_id": "missing-profile",
            "messages": [],
        }],
    })

    result = import_personal_data(payload, user(), profiles, conversations)

    assert result["imported"]["unlinked_conversations"] == 1
    assert conversations.created[0]["birth_profile_id"] is None


def test_import_rejects_unsupported_export_version_before_writing():
    profiles = FakeProfileStore()
    conversations = FakeConversationStore()
    payload = ProfileImportV1.model_validate({"export_version": 2})

    with pytest.raises(HTTPException) as exc:
        import_personal_data(payload, user(), profiles, conversations)

    assert exc.value.status_code == 400
    assert profiles.user is None
    assert profiles.created == []
    assert conversations.created == []
