from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    # Telegram Bot
    bot_token: SecretStr
    
    # Database (PostgreSQL 15)
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    database_url: str

    # Redis / Celery
    redis_url: str
    
    # API Keys
    riot_api_key: SecretStr | None = None
    steam_api_key: SecretStr | None = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
