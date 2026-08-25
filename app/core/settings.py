from __future__ import annotations

from functools import lru_cache
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

    auth_enabled: bool = False
    api_auth_required: bool = False
    auth_jwt_secret: str = ""
    auth_jwks_url: str = ""
    auth_jwt_algorithm: Literal[
        "HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"
    ] = "HS256"
    auth_jwt_issuer: str = "astroai"
    auth_jwt_audience: str = "astroai-api"
    profile_database_path: str = "data/astroai_profiles.db"

    @property
    def cors_origin_list(self) -> list[str]:
        return _csv(self.cors_origins)

    @property
    def trusted_host_list(self) -> list[str]:
        return _csv(self.trusted_hosts)

    @model_validator(mode="after")
    def validate_production_safety(self) -> "Settings":
        if not self.profile_database_path.strip():
            raise ValueError("ASTROAI_PROFILE_DATABASE_PATH must not be empty.")
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
        return self


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
