from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LOG_LEVEL: Literal["ERROR", "WARNING", "INFO", "DEBUG"]
    MODE: Literal["DEV", "TEST", "PROD"]

    HOST: str
    PORT: int
    WORKERS: int

    SCRAP_URL: str
    GROUP: int = 90002595

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str = ""
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    RMQ_HOST: str
    RMQ_USER: str
    RMQ_PASS: str
    RMQ_PORT: int

    @property
    def RABBITMQ_URL(self) -> str:
        return f"amqp://{self.RMQ_USER}:{self.RMQ_PASS}@{self.RMQ_HOST}:{self.RMQ_PORT}//"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings: Settings = Settings()