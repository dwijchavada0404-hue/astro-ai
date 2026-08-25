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
    auth_jwt_secret: str = ""
    auth_jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    auth_jwt_issuer: str = "astroai"
    auth_jwt_audience: str = "astroai-api"

    @property
    def cors_origin_list(self) -> list[str]:
        return _csv(self.cors_origins)

    @property
    def trusted_host_list(self) -> list[str]:
        return _csv(self.trusted_hosts)

    @model_validator(mode="after")
    def validate_production_safety(self) -> "Settings":
        if self.auth_enabled and len(self.auth_jwt_secret) < 32:
            raise ValueError("ASTROAI_AUTH_JWT_SECRET must contain at least 32 characters when authentication is enabled.")
        if self.environment == "production":
            if "*" in self.cors_origin_list:
                raise ValueError("Wildcard CORS origins are not allowed in production.")
            if not self.trusted_host_list or "*" in self.trusted_host_list:
                raise ValueError("Explicit trusted hosts are required in production.")
            if self.docs_enabled:
                raise ValueError("API docs must be disabled in production.")
            if not self.security_headers_enabled:
                raise ValueError("Security headers must be enabled in production.")
            if not self.auth_enabled:
                raise ValueError("Authentication must be enabled in production.")
            if not self.auth_jwt_issuer.strip() or not self.auth_jwt_audience.strip():
                raise ValueError("Explicit JWT issuer and audience are required in production.")
        return self


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
