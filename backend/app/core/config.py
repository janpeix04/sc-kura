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
    API_HOST: str = "localhost"

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

    EMAIL_TEMPLATE_PATH: str = "email_templates/build"
    EMAIL_TOKEN_EXPIRE_HOURS: int = 24

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

    @property
    def EMAIL_COLOR_PALETTE(self) -> dict:
        return {
            "primary": "rgba(43, 127, 255, 1)",  # main blue
            "primaryHigh": "rgba(81, 162, 255, 1)",  # lighter blue for hover, etc.
            "secondary": "rgba(255, 255, 255, 1)",  # white
            "background": "rgba(255, 255, 255, 1)",  # white section background
            "background2": "rgba(245, 245, 245, 1)",  # light gray body background
            "foreground": "rgba(0, 0, 0, 0.87)",  # default text color
            "foregroundLight": "rgba(255, 255, 255, 1)",  # text on primary buttons
            "mutedForeground": "rgba(100, 100, 100, 1)",  # muted text
            "footer": "rgba(230, 230, 230, 1)",  # footer background
        }

    @property
    def EMAIL_NEW_ACCOUNT_TEMPLATE(self) -> Path:
        return Path(self.EMAIL_TEMPLATE_PATH) / "new_account.html"


settings = Settings()
