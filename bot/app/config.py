from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
BOT_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    bot_token: str = ""
    backend_url: str = "http://127.0.0.1:8000"
    service_token: str = "local-service-token"
    webapp_url: str = "http://localhost:3000"
    redis_url: str = ""
    admin_ids: str = ""
    strict_backend_check: bool = False
    drop_pending_updates: bool = True

    model_config = SettingsConfigDict(
        env_file=(ROOT_ENV_FILE, BOT_ENV_FILE),
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_admin_ids() -> set[int]:
    raw = get_settings().admin_ids
    admin_ids: set[int] = set()
    for chunk in raw.split(","):
        value = chunk.strip()
        if value.isdigit():
            admin_ids.add(int(value))
    return admin_ids
