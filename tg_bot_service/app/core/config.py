from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LOG_LEVEL: Literal["ERROR", "WARNING", "INFO", "DEBUG"]
    MODE: Literal["DEV", "TEST", "PROD"]

    BOT_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings: Settings = Settings()