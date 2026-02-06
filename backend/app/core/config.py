from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

import secrets

envfile = Path(".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=envfile.as_posix(), env_file_encoding="utf-8", extra="ignore"
    )

    API_TITLE: str = "Kura"
    API_DESCRIPTION: str = "Kura API"
    API_VERSION: str = "0.0.1"
    API_V1_PREFIX: str = "/api"

    # driver://user:pass@localhost/dbname
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_NAME: str = "postgres"
    DATABASE_HOST: str = "localhost"
    DATABASE_DRIVER: str = "postgresql+psycopg"

    FRONTEND_PORT: int = 5173

    REDIS_BROKER_URL: str = "redis://localhost:6379/0"
    REDIS_RESULT_BACKEND: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 2

    MAIL_USERNAME: str
    MAIL_FROM: str
    MAIL_PASSWORD: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"{self.DATABASE_DRIVER}://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}/{self.DATABASE_NAME}"
        )


settings = Settings()
