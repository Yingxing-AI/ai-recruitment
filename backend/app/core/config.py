from __future__ import annotations

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Recruitment System"
    environment: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 8
    database_url: str = "sqlite:///./dev.db"
    database_startup_max_attempts: int = 10
    database_startup_retry_delay_seconds: float = 2.0
    redis_url: str = "redis://localhost:6379/0"
    upload_dir: str = "./uploads"
    storage_backend: str = "minio"
    minio_endpoint_url: str = "http://localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "resumes"
    minio_secure: bool = False
    backend_cors_origins: str = "http://localhost:3000,http://localhost:3001"
    llm_provider: str = "mock"
    llm_model: str = "mock-recruitment"
    llm_api_key: str | None = None
    llm_base_url: str | None = None

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.backend_cors_origins.split(",") if item.strip()]

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.environment.lower() != "production":
            return self

        if self.secret_key in {"change-me", "change-me-in-production"} or len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters in production")

        if self.database_url.startswith("sqlite"):
            raise ValueError("DATABASE_URL must not use SQLite in production")

        if not self.cors_origins:
            raise ValueError("BACKEND_CORS_ORIGINS must not be empty in production")

        if any(origin == "*" for origin in self.cors_origins):
            raise ValueError("BACKEND_CORS_ORIGINS must not allow wildcard origins in production")

        if self.storage_backend == "minio":
            invalid_minio_values = {"minioadmin", "replace-with-minio-access-key", "replace-with-minio-secret-key"}
            if self.minio_access_key in invalid_minio_values or self.minio_secret_key in invalid_minio_values:
                raise ValueError("MinIO credentials must be replaced in production")

        return self


settings = Settings()
