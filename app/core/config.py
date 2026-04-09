from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """настройки приложения"""

    app_name: str = "Bookmarks API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+psycopg://bookmarks:bookmarks@localhost:5432/bookmarks"
    )
    page_size_default: int = 10
    page_size_max: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """возвращает кэшированные настройки"""

    return Settings()
