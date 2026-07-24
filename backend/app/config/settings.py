from functools import lru_cache
import os
from typing import Annotated
from pydantic import AnyUrl, BeforeValidator, Field
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def parse_cors(value: str | list[str]) -> list[str]:
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

    PROJECT_NAME: str = "RouteMind AI"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = Field(min_length=16)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    DATABASE_URL: str = "postgresql+asyncpg://routemind:routemind@localhost:5432/routemind"
    REDIS_URL: str = "redis://localhost:6379/0"
    BACKEND_CORS_ORIGINS: Annotated[list[str], NoDecode, BeforeValidator(parse_cors)] = []
    LOG_LEVEL: str = "INFO"

    LLM_PROVIDER: str = "gemini"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4.1-mini"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY") or "your-api-key"
    AZURE_OPENAI_API_KEY: str | None = None
    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_API_VERSION: str = "2024-10-21"
    AZURE_OPENAI_DEPLOYMENT: str | None = None
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GOOGLE_MAPS_API_KEY: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
