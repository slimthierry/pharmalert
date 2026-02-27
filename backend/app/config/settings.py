import json
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "PharmAlert"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://pharmalert:pharmalert_secret@localhost:5432/pharmalert"
    )

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "pharmalert-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours for hospital shifts

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3900"]

    # Webhooks
    WEBHOOK_URLS: List[str] = []
    WEBHOOK_SECRET: str = "webhook-secret-change-in-production"

    class Config:
        env_file = ".env"
        case_sensitive = True

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name in ("CORS_ORIGINS", "WEBHOOK_URLS"):
                try:
                    return json.loads(raw_val)
                except (json.JSONDecodeError, TypeError):
                    return [raw_val]
            return raw_val


settings = Settings()
