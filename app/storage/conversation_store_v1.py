from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4


class ConversationStoreV1:
    """Durable, user-owned conversation/message repository backed by SQLite."""

    def __init__(self, database_path: str) -> None:
        if not isinstance(database_path, str) or not database_path.strip():
            raise ValueError("database_path must not be empty.")
        self.database_path = database_path
        if database_path != ":memory:":
            Path(database_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    birth_profile_id TEXT,
                    title TEXT NOT NULL,
                    life_context_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_conversations_user_updated
                    ON conversations(user_id, updated_at DESC);

                CREATE TABLE IF NOT EXISTS conversation_messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user','assistant')),
                    content TEXT,
                    domain TEXT,
                    route TEXT,
                    reference_moment TEXT,
                    payload_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
                    ON conversation_messages(conversation_id, created_at ASC);
                """
            )

    @staticmethod
    def _loads(value: str | None) -> Any:
        if value is None:
            return None
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return None

    @staticmethod
    def _dumps(value: Any) -> str | None:
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)

    def _conversation(self, row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        value = dict(row)
        value["life_context"] = self._loads(value.pop("life_context_json", None))
        return value

    def _message(self, row: sqlite3.Row) -> dict[str, Any]:
        value = dict(row)
        value["payload"] = self._loads(value.pop("payload_json", None))
        return value

    def create_conversation(self, user_id: str, *, title: str, birth_profile_id: str | None = None, life_context: dict[str, Any] | None = None) -> dict[str, Any]:
        conversation_id = str(uuid4())
        now = self._now()
        with self._connect() as db:
            db.execute(
                "INSERT INTO conversations(conversation_id,user_id,birth_profile_id,title,life_context_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
                (conversation_id, user_id, birth_profile_id, title, self._dumps(life_context), now, now),
            )
            row = db.execute("SELECT * FROM conversations WHERE conversation_id=? AND user_id=?", (conversation_id, user_id)).fetchone()
        return self._conversation(row) or {}

    def list_conversations(self, user_id: str, *, limit: int = 50) -> list[dict[str, Any]]:
        bounded = max(1, min(int(limit), 100))
        with self._connect() as db:
            rows = db.execute(
                """SELECT c.*, (SELECT COUNT(*) FROM conversation_messages m WHERE m.conversation_id=c.conversation_id) AS message_count
                   FROM conversations c WHERE c.user_id=? ORDER BY c.updated_at DESC LIMIT ?""",
                (user_id, bounded),
            ).fetchall()
        return [self._conversation(row) or {} for row in rows]

    def get_conversation(self, user_id: str, conversation_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM conversations WHERE user_id=? AND conversation_id=?", (user_id, conversation_id)).fetchone()
        return self._conversation(row)

    def has_birth_profile_references(self, user_id: str, birth_profile_id: str) -> bool:
        with self._connect() as db:
            row = db.execute(
                "SELECT 1 FROM conversations WHERE user_id=? AND birth_profile_id=? LIMIT 1",
                (user_id, birth_profile_id),
            ).fetchone()
        return row is not None

    def update_conversation(self, user_id: str, conversation_id: str, *, title: str | None = None, life_context: dict[str, Any] | None = None, set_life_context: bool = False) -> dict[str, Any] | None:
        current = self.get_conversation(user_id, conversation_id)
        if current is None:
            return None
        assignments: list[str] = []
        values: list[Any] = []
        if title is not None:
            assignments.append("title=?")
            values.append(title)
        if set_life_context:
            assignments.append("life_context_json=?")
            values.append(self._dumps(life_context))
        assignments.append("updated_at=?")
        values.append(self._now())
        with self._connect() as db:
            db.execute(f"UPDATE conversations SET {', '.join(assignments)} WHERE user_id=? AND conversation_id=?", (*values, user_id, conversation_id))
            row = db.execute("SELECT * FROM conversations WHERE user_id=? AND conversation_id=?", (user_id, conversation_id)).fetchone()
        return self._conversation(row)

    def delete_conversation(self, user_id: str, conversation_id: str) -> bool:
        with self._connect() as db:
            cursor = db.execute("DELETE FROM conversations WHERE user_id=? AND conversation_id=?", (user_id, conversation_id))
            return cursor.rowcount > 0

    def delete_user_conversations(self, user_id: str) -> int:
        """Delete every conversation and cascaded message owned by one user."""
        with self._connect() as db:
            cursor = db.execute("DELETE FROM conversations WHERE user_id=?", (user_id,))
            return cursor.rowcount

    def add_message(self, user_id: str, conversation_id: str, *, role: str, content: str | None, domain: str | None = None, route: str | None = None, reference_moment: str | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if role not in {"user", "assistant"}:
            raise ValueError("role must be user or assistant.")
        if self.get_conversation(user_id, conversation_id) is None:
            raise KeyError("Conversation not found.")
        message_id = str(uuid4())
        now = self._now()
        with self._connect() as db:
            db.execute(
                "INSERT INTO conversation_messages(message_id,conversation_id,user_id,role,content,domain,route,reference_moment,payload_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (message_id, conversation_id, user_id, role, content, domain, route, reference_moment, self._dumps(payload), now),
            )
            db.execute("UPDATE conversations SET updated_at=? WHERE conversation_id=? AND user_id=?", (now, conversation_id, user_id))
            row = db.execute("SELECT * FROM conversation_messages WHERE message_id=? AND user_id=?", (message_id, user_id)).fetchone()
        if row is None:
            raise RuntimeError("Message insert failed.")
        return self._message(row)

    def list_messages(self, user_id: str, conversation_id: str, *, limit: int = 200) -> list[dict[str, Any]]:
        if self.get_conversation(user_id, conversation_id) is None:
            raise KeyError("Conversation not found.")
        bounded = max(1, min(int(limit), 500))
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM conversation_messages WHERE user_id=? AND conversation_id=? ORDER BY created_at ASC LIMIT ?",
                (user_id, conversation_id, bounded),
            ).fetchall()
        return [self._message(row) for row in rows]
