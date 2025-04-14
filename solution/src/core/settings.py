from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_host: str
    database_port: int
    database_user: str
    database_password: str
    database_db_name: str
    database_debug: bool = False
    database_provider: str = "postgresql+asyncpg"

    redis_host: str
    redis_port: int
    redis_password: str
    redis_db: int = 0
    redis_provider: str = "redis://"

    telegram_bot_token: str

    current_day: str = "2025-02-14"

    ai_api_key: str
    ai_moderation_enabled: bool = False
    ai_check_profanity: bool = False
    ai_check_offensive: bool = False
    ai_check_inappropriate: bool = False

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_secure: bool = False
    minio_bucket_name: str
    minio_public_host: str

    yandex_token: str
    yandex_sandbox_mode: bool = True

    cloudflare_api_token: str
    cloudflare_account_id: str
    cloudflare_model: str = "@cf/bytedance/stable-diffusion-xl-lightning"

    @property
    def minio_public_url(self) -> str:
        protocol = "https" if self.minio_secure else "http"
        return f"{protocol}://{self.minio_public_host}"

    @property
    def database_url(self) -> str:
        return f"{self.database_provider}://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_db_name}"

    @property
    def redis_url(self) -> str:
        return f"{self.redis_provider}{self.redis_host}:{self.redis_port}"


def get_settings() -> Settings:
    settings = Settings()  # type: ignore

    return settings


settings = get_settings()

SettingsService = Annotated[Settings, Depends(get_settings)]
