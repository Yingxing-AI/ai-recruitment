from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Recruitment System"
    environment: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 8
    database_url: str = "sqlite:///./dev.db"
    redis_url: str = "redis://localhost:6379/0"
    upload_dir: str = "./uploads"
    storage_backend: str = "minio"
    minio_endpoint_url: str = "http://localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "resumes"
    minio_secure: bool = False
    backend_cors_origins: str = "http://localhost:5173"
    llm_provider: str = "mock"
    llm_model: str = "mock-recruitment"
    llm_api_key: str | None = None
    llm_base_url: str | None = None

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.backend_cors_origins.split(",") if item.strip()]


settings = Settings()
