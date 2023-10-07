from typing import Literal

from pydantic import root_validator
from pydantic_settings import BaseSettings


# Описание настроек приложения
class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"] # Режим работы приложения (DEV, TEST, PROD)
    LOG_LEVEL: str

    DB_HOST: str
    DB_USER: str
    DB_PASS: str
    DB_PORT: str
    DB_NAME: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str

    @property
    def TEST_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"

    # Настройки аутентификации и безопасности
    SECRET_KEY: str
    ALGORITHM: str

    # Настройки SMTP для отправки почты
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    # Настройки Redis
    REDIS_HOST: str
    REDIS_PORT: int

    SENTRY_DSN: str

    class Config:
        env_file = ".env"


settings = Settings()
