from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row


def is_postgres_target(database_target: str) -> bool:
    normalized = database_target.strip().lower()
    return normalized.startswith("postgresql://") or normalized.startswith("postgres://")


class DatabaseConnectionV1:
    """Small SQL compatibility layer for SQLite and PostgreSQL repositories."""

    def __init__(self, connection: Any, *, postgres: bool) -> None:
        self._connection = connection
        self.postgres = postgres

    def execute(self, statement: str, parameters: tuple[Any, ...] | list[Any] = ()):
        query = statement.replace("?", "%s") if self.postgres else statement
        return self._connection.execute(query, parameters)

    def executescript(self, script: str) -> None:
        if not self.postgres:
            self._connection.executescript(script)
            return
        for statement in script.split(";"):
            if statement.strip():
                self._connection.execute(statement)

    def commit(self) -> None:
        self._connection.commit()

    def rollback(self) -> None:
        self._connection.rollback()

    def close(self) -> None:
        self._connection.close()


@contextmanager
def connect_database(database_target: str) -> Iterator[DatabaseConnectionV1]:
    postgres = is_postgres_target(database_target)
    if postgres:
        raw_connection = psycopg.connect(
            database_target,
            connect_timeout=10,
            row_factory=dict_row,
        )
    else:
        if database_target != ":memory:":
            Path(database_target).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        raw_connection = sqlite3.connect(database_target, timeout=10)
        raw_connection.row_factory = sqlite3.Row
        raw_connection.execute("PRAGMA foreign_keys = ON")
        raw_connection.execute("PRAGMA busy_timeout = 10000")
        if database_target != ":memory:":
            raw_connection.execute("PRAGMA journal_mode = WAL")

    connection = DatabaseConnectionV1(raw_connection, postgres=postgres)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
