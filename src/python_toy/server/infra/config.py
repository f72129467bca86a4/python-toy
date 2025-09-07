from __future__ import annotations

import functools
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingConfig(BaseModel):
    format: Literal["json", "text", "console"] = "console"
    level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"] = "INFO"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_prefix="APP_",
        env_nested_delimiter=".",
        env_file=".env",
    )

    env: Literal["local", "dev", "prod"] = "local"
    logging: LoggingConfig = LoggingConfig()


@functools.cache
def get_settings() -> Settings:
    return Settings()
