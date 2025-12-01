from functools import lru_cache
from typing import Optional

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="Novel System", env="APP_NAME")
    postgres_dsn: PostgresDsn = Field(
        default="postgresql+psycopg2://user:password@0.0.0.0:5432/novel_db",
        env="POSTGRES_DSN",
    )
    redis_url: RedisDsn = Field(
        default="redis://0.0.0.0:6379/0",
        env="REDIS_URL",
    )
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1", env="OPENAI_MODEL")
    environment: Optional[str] = Field(default="development", env="ENVIRONMENT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
