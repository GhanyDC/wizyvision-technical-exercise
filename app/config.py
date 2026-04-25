from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"


class Settings(BaseSettings):
    app_name: str = Field(default="WizyVision Technical Exercise", alias="APP_NAME")
    environment: str = Field(default="development", alias="APP_ENVIRONMENT")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    model_name: str = Field(default="gemini-2.5-flash", alias="MODEL_NAME")
    agentic_model_name: str = Field(
        default="gemini-3-flash-preview",
        alias="AGENTIC_MODEL_NAME",
    )
    max_upload_size_bytes: int = Field(
        default=5 * 1024 * 1024,
        alias="MAX_UPLOAD_SIZE_BYTES",
    )
    request_timeout_seconds: float = Field(
        default=30.0,
        alias="REQUEST_TIMEOUT_SECONDS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def max_upload_size_megabytes(self) -> int:
        return self.max_upload_size_bytes // (1024 * 1024)


@lru_cache
def get_settings() -> Settings:
    return Settings()
