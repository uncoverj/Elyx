from functools import lru_cache
from pathlib import Path
from socket import create_connection
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


SQLITE_FALLBACK_URL = "sqlite+aiosqlite:///./elyx.db"
ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    app_name: str = "Elyx API"
    app_env: str = "dev"
    bot_token: str = ""
    service_token: str = "local-service-token"
    database_url: str = ""
    redis_url: str = "redis://redis:6379/0"
    cors_origin: str = "*"

    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _looks_like_docker_postgres_host(database_url: str) -> bool:
    lowered = database_url.lower()
    return "@postgres:" in lowered or "host=postgres" in lowered


def _can_connect_to_database_host(database_url: str, timeout_seconds: float = 1.2) -> bool:
    parsed = urlparse(database_url)
    host = parsed.hostname
    if not host:
        return False

    port = parsed.port or (5432 if parsed.scheme.startswith("postgres") else 0)
    if port <= 0:
        return False

    try:
        with create_connection((host, port), timeout=timeout_seconds):
            return True
    except OSError:
        return False


@lru_cache
def get_database_url() -> str:
    settings = get_settings()
    app_env = settings.app_env.lower().strip() or "dev"
    raw_database_url = settings.database_url.strip()

    if app_env == "prod":
        if not raw_database_url:
            raise RuntimeError("APP_ENV=prod requires DATABASE_URL to be set.")
        if raw_database_url.startswith("postgresql") and not _can_connect_to_database_host(raw_database_url):
            raise RuntimeError(
                "APP_ENV=prod requires a reachable PostgreSQL host from DATABASE_URL. "
                "Current host is unreachable."
            )
        return raw_database_url

    if not raw_database_url:
        return SQLITE_FALLBACK_URL

    if _looks_like_docker_postgres_host(raw_database_url):
        return SQLITE_FALLBACK_URL

    if raw_database_url.startswith("postgresql") and not _can_connect_to_database_host(raw_database_url):
        return SQLITE_FALLBACK_URL

    return raw_database_url
