import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_settings_reject_placeholder_secret_key() -> None:
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(
            environment="production",
            secret_key="change-me-in-production",
            database_url="postgresql+psycopg://user:pass@postgres:5432/app",
            backend_cors_origins="https://example.com",
            minio_access_key="prod-access",
            minio_secret_key="prod-secret",
        )


def test_production_settings_accepts_hardened_values() -> None:
    settings = Settings(
        environment="production",
        secret_key="0123456789abcdef0123456789abcdef",
        database_url="postgresql+psycopg://user:pass@postgres:5432/app",
        backend_cors_origins="https://hr.example.com,https://ops.example.com",
        minio_access_key="prod-access",
        minio_secret_key="prod-secret",
    )

    assert settings.environment == "production"
    assert settings.cors_origins == ["https://hr.example.com", "https://ops.example.com"]
