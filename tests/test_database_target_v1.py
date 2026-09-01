from app.core.settings import Settings
from app.storage.database_v1 import DatabaseConnectionV1, is_postgres_target


class _RecordingConnection:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    def execute(self, statement: str, parameters: tuple[object, ...]):
        self.calls.append((statement, parameters))
        return self


def test_database_url_takes_precedence_over_legacy_sqlite_path() -> None:
    settings = Settings(
        database_url="postgresql://astroai:secret@db.example/astroai?sslmode=require",
        profile_database_path="data/ignored.db",
    )

    assert settings.database_target == "postgresql://astroai:secret@db.example/astroai?sslmode=require"


def test_sqlite_path_remains_the_default_database_target() -> None:
    settings = Settings(profile_database_path="data/profiles.db")

    assert settings.database_target == "data/profiles.db"


def test_postgres_target_detection_accepts_standard_connection_urls() -> None:
    assert is_postgres_target("postgresql://user:password@host/database")
    assert is_postgres_target("POSTGRES://user:password@host/database")
    assert not is_postgres_target("data/astroai_profiles.db")


def test_postgres_connection_translates_sqlite_placeholders() -> None:
    raw = _RecordingConnection()
    connection = DatabaseConnectionV1(raw, postgres=True)

    connection.execute("SELECT * FROM birth_profiles WHERE user_id=? AND profile_id=?", ("user", "profile"))

    assert raw.calls == [
        ("SELECT * FROM birth_profiles WHERE user_id=%s AND profile_id=%s", ("user", "profile"))
    ]
