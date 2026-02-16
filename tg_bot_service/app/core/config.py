from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LOG_LEVEL: Literal["ERROR", "WARNING", "INFO", "DEBUG"]
    MODE: Literal["DEV", "TEST", "PROD"]

    BOT_TOKEN: str
    BOT_USERNAME: Optional[str] = None
    TG_ID_ADMIN: int

    SCHEDULE_URL: str

    DB_HOST: str
    DB_PORT: int
    DB_PASS: str
    DB_USER: str
    DB_NAME: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


    RMQ_HOST: str
    RMQ_USER: str
    RMQ_PASS: str
    RMQ_PORT: int

    @property
    def RABBITMQ_URL(self) -> str:
        return f"amqp://{self.RMQ_USER}:{self.RMQ_PASS}@{self.RMQ_HOST}:{self.RMQ_PORT}//"


    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str = ""
    REDIS_DB: int = 1

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings: Settings = Settings()