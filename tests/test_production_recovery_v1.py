import sqlite3
from pathlib import Path

import pytest

from app.core.runtime import _database_ready
from app.core.settings import Settings
from scripts.sqlite_recovery import create_backup, verify_sqlite


def _production_settings(**overrides):
    values = {
        "environment": "production",
        "cors_origins": "https://astroai.example",
        "trusted_hosts": "astroai.example,healthcheck.railway.app",
        "docs_enabled": False,
        "security_headers_enabled": True,
        "rate_limit_enabled": True,
        "request_logging_enabled": True,
        "auth_enabled": True,
        "api_auth_required": True,
        "auth_jwt_secret": "x" * 40,
        "geocoding_provider": "openmapquest",
        "geocoding_api_key": "test-api-key",
        "profile_database_path": "/data/astroai_profiles.db",
    }
    values.update(overrides)
    return Settings(**values)


def _seed_database(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.executescript(
            """
            CREATE TABLE user_profiles(user_id TEXT PRIMARY KEY);
            CREATE TABLE birth_profiles(profile_id TEXT PRIMARY KEY);
            CREATE TABLE conversations(conversation_id TEXT PRIMARY KEY);
            CREATE TABLE messages(message_id TEXT PRIMARY KEY);
            INSERT INTO user_profiles(user_id) VALUES('user-1');
            """
        )
        connection.commit()
    finally:
        connection.close()


def test_production_sqlite_requires_persistent_data_volume():
    with pytest.raises(ValueError, match="persistent path under /data"):
        _production_settings(profile_database_path="data/astroai_profiles.db")
    with pytest.raises(ValueError, match="mounted /data volume"):
        _production_settings(profile_database_path="/tmp/astroai_profiles.db")
    assert _production_settings().profile_database_path == "/data/astroai_profiles.db"


def test_production_postgres_is_not_subject_to_sqlite_mount_rule():
    settings = _production_settings(database_url="postgresql://user:pass@db.example/astroai")
    assert settings.database_target.startswith("postgresql://")


def test_readiness_checks_sqlite_integrity(tmp_path):
    database_path = tmp_path / "healthy.db"
    connection = sqlite3.connect(database_path)
    connection.execute("CREATE TABLE example(id INTEGER PRIMARY KEY)")
    connection.commit()
    connection.close()
    assert _database_ready(str(database_path)) is True

    corrupt_path = tmp_path / "corrupt.db"
    corrupt_path.write_bytes(b"not-a-sqlite-database")
    assert _database_ready(str(corrupt_path)) is False


def test_sqlite_backup_is_consistent_and_verifiable(tmp_path):
    source = tmp_path / "live.db"
    backup = tmp_path / "backups" / "astroai.db"
    _seed_database(source)

    created = create_backup(source, backup)
    assert created == backup.resolve()
    verify_sqlite(backup)

    restored = sqlite3.connect(backup)
    try:
        assert restored.execute("SELECT COUNT(*) FROM user_profiles").fetchone()[0] == 1
    finally:
        restored.close()


def test_recovery_verifier_rejects_incomplete_schema(tmp_path):
    database_path = tmp_path / "incomplete.db"
    connection = sqlite3.connect(database_path)
    connection.execute("CREATE TABLE user_profiles(user_id TEXT PRIMARY KEY)")
    connection.commit()
    connection.close()

    with pytest.raises(ValueError, match="missing required tables"):
        verify_sqlite(database_path)
