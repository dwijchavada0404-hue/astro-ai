from pathlib import Path

from app.storage.conversation_store_v1 import ConversationStoreV1


def test_conversation_and_messages_persist_across_store_instances(tmp_path: Path):
    database = str(tmp_path / "conversation.db")
    first = ConversationStoreV1(database)
    conversation = first.create_conversation(
        "user_1",
        title="Marriage timing",
        birth_profile_id="birth_1",
        life_context={"marriage": "likely_pending"},
    )
    conversation_id = conversation["conversation_id"]
    first.add_message("user_1", conversation_id, role="user", content="When will I marry?")
    first.add_message(
        "user_1",
        conversation_id,
        role="assistant",
        content="A symbolic timing answer",
        domain="marriage",
        route="top_level_to_marriage",
        payload={"status": "answered"},
    )

    reopened = ConversationStoreV1(database)
    saved = reopened.get_conversation("user_1", conversation_id)
    assert saved is not None
    assert saved["title"] == "Marriage timing"
    assert saved["life_context"] == {"marriage": "likely_pending"}
    messages = reopened.list_messages("user_1", conversation_id)
    assert [item["role"] for item in messages] == ["user", "assistant"]
    assert messages[1]["domain"] == "marriage"
    assert messages[1]["payload"]["status"] == "answered"


def test_user_ownership_is_enforced(tmp_path: Path):
    store = ConversationStoreV1(str(tmp_path / "ownership.db"))
    conversation = store.create_conversation("owner", title="Private")
    conversation_id = conversation["conversation_id"]
    store.add_message("owner", conversation_id, role="user", content="Private question")

    assert store.get_conversation("other", conversation_id) is None
    assert store.delete_conversation("other", conversation_id) is False
    try:
        store.list_messages("other", conversation_id)
    except KeyError:
        pass
    else:
        raise AssertionError("Expected ownership isolation to hide messages")


def test_delete_cascades_messages(tmp_path: Path):
    store = ConversationStoreV1(str(tmp_path / "delete.db"))
    conversation_id = store.create_conversation("user", title="Disposable")["conversation_id"]
    store.add_message("user", conversation_id, role="user", content="Hello")
    assert store.delete_conversation("user", conversation_id) is True
    assert store.get_conversation("user", conversation_id) is None
