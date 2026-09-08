from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven runtime configuration for deployable AstroAI instances."""

    model_config = SettingsConfigDict(
        env_prefix="ASTROAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "test", "staging", "production"] = "development"
    app_name: str = "AstroAI"
    app_version: str = "1.0.0-beta.1"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    trusted_hosts: str = "localhost,127.0.0.1,testserver"
    docs_enabled: bool = True
    request_id_header: str = "X-Request-ID"
    max_request_body_bytes: int = Field(default=1_048_576, ge=1, le=10_485_760)
    security_headers_enabled: bool = True
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = Field(default=120, ge=1, le=10_000)
    request_logging_enabled: bool = True
    slow_request_threshold_ms: int = Field(default=2_000, ge=100, le=120_000)

    auth_enabled: bool = False
    api_auth_required: bool = False
    auth_jwt_secret: str = ""
    auth_jwks_url: str = ""
    auth_jwt_algorithm: Literal[
        "HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"
    ] = "HS256"
    auth_jwt_issuer: str = "astroai"
    auth_jwt_audience: str = "astroai-api"
    database_url: str = ""
    profile_database_path: str = "data/astroai_profiles.db"

    geocoding_provider: Literal["nominatim", "openmapquest", "geoapify"] = "nominatim"
    geocoding_api_key: str = ""
    geocoding_timeout_seconds: int = Field(default=10, ge=1, le=30)
    geocoding_user_agent: str = "astro-ai/1.0"

    @property
    def database_target(self) -> str:
        return self.database_url.strip() or self.profile_database_path

    @property
    def cors_origin_list(self) -> list[str]:
        return _csv(self.cors_origins)

    @property
    def trusted_host_list(self) -> list[str]:
        return _csv(self.trusted_hosts)

    @model_validator(mode="after")
    def validate_production_safety(self) -> "Settings":
        database_target = self.database_target.strip()
        if not database_target:
            raise ValueError("ASTROAI_DATABASE_URL or ASTROAI_PROFILE_DATABASE_PATH must not be empty.")
        if self.auth_enabled:
            uses_jwks = bool(self.auth_jwks_url.strip())
            uses_symmetric_algorithm = self.auth_jwt_algorithm.startswith("HS")
            if uses_jwks and uses_symmetric_algorithm:
                raise ValueError("ASTROAI_AUTH_JWT_ALGORITHM must be asymmetric when ASTROAI_AUTH_JWKS_URL is configured.")
            if not uses_jwks and not uses_symmetric_algorithm:
                raise ValueError("ASTROAI_AUTH_JWKS_URL is required for asymmetric JWT algorithms.")
            if not uses_jwks and len(self.auth_jwt_secret) < 32:
                raise ValueError("ASTROAI_AUTH_JWT_SECRET must contain at least 32 characters when symmetric authentication is enabled.")
            if uses_jwks and self.environment in {"staging", "production"} and not self.auth_jwks_url.startswith("https://"):
                raise ValueError("ASTROAI_AUTH_JWKS_URL must use HTTPS in deployed environments.")
            if not self.auth_jwt_issuer.strip() or not self.auth_jwt_audience.strip():
                raise ValueError("Explicit JWT issuer and audience are required when authentication is enabled.")
        if self.api_auth_required and not self.auth_enabled:
            raise ValueError("ASTROAI_API_AUTH_REQUIRED requires ASTROAI_AUTH_ENABLED=true.")
        if self.geocoding_provider in {"openmapquest", "geoapify"} and not self.geocoding_api_key.strip():
            raise ValueError("ASTROAI_GEOCODING_API_KEY is required when a keyed geocoding provider is selected.")
        if self.environment == "production":
            if "*" in self.cors_origin_list:
                raise ValueError("Wildcard CORS origins are not allowed in production.")
            if not self.trusted_host_list or "*" in self.trusted_host_list:
                raise ValueError("Explicit trusted hosts are required in production.")
            if self.docs_enabled:
                raise ValueError("API docs must be disabled in production.")
            if not self.security_headers_enabled:
                raise ValueError("Security headers must be enabled in production.")
            if not self.api_auth_required:
                raise ValueError("API bearer authentication must be required in production.")
            if not self.rate_limit_enabled:
                raise ValueError("API rate limiting must be enabled in production.")
            if not self.request_logging_enabled:
                raise ValueError("Structured request logging must be enabled in production.")
            if self.geocoding_provider == "nominatim":
                raise ValueError("Public Nominatim geocoding is not allowed in production; configure a keyed provider.")
            if not _is_postgres_target(database_target):
                sqlite_path = Path(database_target).expanduser()
                if not sqlite_path.is_absolute():
                    raise ValueError("Production SQLite must use an absolute persistent path under /data.")
                try:
                    sqlite_path.relative_to(Path("/data"))
                except ValueError as exc:
                    raise ValueError("Production SQLite must be stored under the mounted /data volume.") from exc
                if sqlite_path == Path("/data"):
                    raise ValueError("Production SQLite path must name a database file under /data.")
            if not self.auth_jwks_url.strip():
                raise ValueError("Production authentication must use an HTTPS JWKS endpoint; symmetric JWT secrets are not allowed.")
            if self.auth_jwt_algorithm.startswith("HS"):
                raise ValueError("Production authentication must use an asymmetric JWT algorithm.")
            if not self.auth_jwks_url.startswith("https://"):
                raise ValueError("Production JWKS endpoint must use HTTPS.")
            if not self.auth_jwt_issuer.startswith("https://"):
                raise ValueError("Production JWT issuer must be an explicit HTTPS issuer URL.")
            if self.auth_jwt_issuer.rstrip("/") == "https://astroai":
                raise ValueError("Production JWT issuer must not use the AstroAI placeholder value.")
            if self.auth_jwt_audience.strip() == "astroai-api":
                raise ValueError("Production JWT audience must be explicitly configured for the production API.")
        return self


def _is_postgres_target(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized.startswith("postgresql://") or normalized.startswith("postgres://")


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
