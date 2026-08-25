from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4


class ProfileStoreV1:
    """Small durable repository for user metadata and owned birth profiles."""

    def __init__(self, database_path: str) -> None:
        if not database_path.strip():
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
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    email TEXT,
                    display_name TEXT,
                    locale TEXT,
                    timezone TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS birth_profiles (
                    profile_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    label TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    birth_time TEXT NOT NULL,
                    place TEXT NOT NULL,
                    is_default INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_birth_profiles_user_id ON birth_profiles(user_id);
                """
            )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _row(row: sqlite3.Row | None) -> dict[str, Any] | None:
        return dict(row) if row is not None else None

    def upsert_user(self, user_id: str, *, email: str | None, display_name: str | None, locale: str | None, timezone_name: str | None) -> dict[str, Any]:
        now = self._now()
        with self._connect() as db:
            db.execute(
                """
                INSERT INTO user_profiles(user_id,email,display_name,locale,timezone,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(user_id) DO UPDATE SET
                    email=excluded.email,
                    display_name=excluded.display_name,
                    locale=excluded.locale,
                    timezone=excluded.timezone,
                    updated_at=excluded.updated_at
                """,
                (user_id, email, display_name, locale, timezone_name, now, now),
            )
            row = db.execute("SELECT * FROM user_profiles WHERE user_id=?", (user_id,)).fetchone()
        return self._row(row) or {}

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            return self._row(db.execute("SELECT * FROM user_profiles WHERE user_id=?", (user_id,)).fetchone())

    def create_birth_profile(self, user_id: str, *, label: str, birth_date: str, birth_time: str, place: str, is_default: bool) -> dict[str, Any]:
        now = self._now()
        profile_id = str(uuid4())
        with self._connect() as db:
            if is_default:
                db.execute("UPDATE birth_profiles SET is_default=0, updated_at=? WHERE user_id=?", (now, user_id))
            db.execute(
                """INSERT INTO birth_profiles(profile_id,user_id,label,birth_date,birth_time,place,is_default,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (profile_id, user_id, label, birth_date, birth_time, place, int(is_default), now, now),
            )
            row = db.execute("SELECT * FROM birth_profiles WHERE profile_id=?", (profile_id,)).fetchone()
        return self._normalize_birth(self._row(row) or {})

    def list_birth_profiles(self, user_id: str) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM birth_profiles WHERE user_id=? ORDER BY is_default DESC, created_at ASC",
                (user_id,),
            ).fetchall()
        return [self._normalize_birth(dict(row)) for row in rows]

    def get_birth_profile(self, user_id: str, profile_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM birth_profiles WHERE user_id=? AND profile_id=?", (user_id, profile_id)).fetchone()
        return self._normalize_birth(dict(row)) if row else None

    def update_birth_profile(self, user_id: str, profile_id: str, changes: dict[str, Any]) -> dict[str, Any] | None:
        allowed = {"label", "birth_date", "birth_time", "place", "is_default"}
        updates = {k: v for k, v in changes.items() if k in allowed}
        current = self.get_birth_profile(user_id, profile_id)
        if current is None:
            return None
        if not updates:
            return current
        now = self._now()
        with self._connect() as db:
            if updates.get("is_default") is True:
                db.execute("UPDATE birth_profiles SET is_default=0, updated_at=? WHERE user_id=?", (now, user_id))
            assignments = ", ".join(f"{key}=?" for key in updates)
            values = [int(v) if key == "is_default" else v for key, v in updates.items()]
            db.execute(
                f"UPDATE birth_profiles SET {assignments}, updated_at=? WHERE user_id=? AND profile_id=?",
                (*values, now, user_id, profile_id),
            )
            row = db.execute("SELECT * FROM birth_profiles WHERE user_id=? AND profile_id=?", (user_id, profile_id)).fetchone()
        return self._normalize_birth(dict(row)) if row else None

    def delete_birth_profile(self, user_id: str, profile_id: str) -> bool:
        with self._connect() as db:
            cursor = db.execute("DELETE FROM birth_profiles WHERE user_id=? AND profile_id=?", (user_id, profile_id))
            return cursor.rowcount > 0

    @staticmethod
    def _normalize_birth(value: dict[str, Any]) -> dict[str, Any]:
        if value:
            value["is_default"] = bool(value.get("is_default"))
        return value
