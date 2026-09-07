#!/usr/bin/env python3
"""Create and verify consistent SQLite backups for AstroAI operations."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def verify_sqlite(path: str | Path) -> None:
    database_path = Path(path).expanduser().resolve()
    if not database_path.is_file():
        raise ValueError(f"SQLite database does not exist: {database_path}")

    connection = sqlite3.connect(f"file:{database_path}?mode=ro", uri=True, timeout=10)
    try:
        result = connection.execute("PRAGMA quick_check").fetchone()
        if result is None or str(result[0]).strip().lower() != "ok":
            detail = result[0] if result else "no result"
            raise ValueError(f"SQLite integrity check failed: {detail}")
        required_tables = {"user_profiles", "birth_profiles", "conversations", "messages"}
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        existing_tables = {str(row[0]) for row in rows}
        missing = sorted(required_tables - existing_tables)
        if missing:
            raise ValueError(f"SQLite backup is missing required tables: {', '.join(missing)}")
    finally:
        connection.close()


def create_backup(source: str | Path, destination: str | Path) -> Path:
    source_path = Path(source).expanduser().resolve()
    destination_path = Path(destination).expanduser().resolve()
    if source_path == destination_path:
        raise ValueError("Backup destination must differ from the live database path.")
    if not source_path.is_file():
        raise ValueError(f"SQLite database does not exist: {source_path}")

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    if destination_path.exists():
        raise ValueError(f"Backup destination already exists: {destination_path}")

    source_db = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True, timeout=10)
    destination_db = sqlite3.connect(destination_path, timeout=10)
    try:
        source_db.backup(destination_db)
    finally:
        destination_db.close()
        source_db.close()

    try:
        verify_sqlite(destination_path)
    except Exception:
        destination_path.unlink(missing_ok=True)
        raise
    return destination_path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AstroAI SQLite recovery utility")
    subcommands = parser.add_subparsers(dest="command", required=True)

    backup = subcommands.add_parser("backup", help="Create and verify a consistent SQLite backup")
    backup.add_argument("source")
    backup.add_argument("destination")

    verify = subcommands.add_parser("verify", help="Verify integrity and required AstroAI tables")
    verify.add_argument("database")
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "backup":
        created = create_backup(args.source, args.destination)
        print(f"Verified backup created: {created}")
    else:
        verify_sqlite(args.database)
        print(f"Verified SQLite database: {Path(args.database).expanduser().resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
