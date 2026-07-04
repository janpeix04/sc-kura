from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

envfile = Path(".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=envfile.as_posix(), env_file_encoding="utf-8", extra="ignore"
    )

    API_TITLE: str = "KURA"
    API_DESCRIPTION: str = "Kura API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    DEBUG: bool = True

    # driver://user:pass@localhost/dbname
    POSTGRES_DRIVER: str = "postgresql+psycopg"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"

    OWNER_FIRST_NAME: str = "Owner"
    OWNER_LAST_NAME: str = "Account"
    OWNER_EMAIL: str = "owner@example.com"
    OWNER_PASSWORD: str = "ownercontra"

    FRONTEND_PORT: int = 5173

    # redis://host:port/db
    REDIS_BROKER_URL: str = "redis://localhost:6379/0"
    REDIS_RESULT_BACKEND: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Security
    SECRET_KEY: str
    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Google Services
    MAIL_USERNAME: str
    MAIL_FROM: str
    MAIL_PASSWORD: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_USE_CREDENTIALS: bool = True
    MAIL_VALIDATE_CERTS: bool = True

    EMAIL_TEMPLATE_PATH: str = "email_templates/build"
    EMAIL_TOKEN_EXPIRE_HOURS: int = 48

    STORAGE_ROOT: str = "./assets"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"{self.POSTGRES_DRIVER}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"
        )

    @property
    def EMAIL_VERIFY_EMAIL_ADDRESS_TEMPLATE(self) -> dict:
        return {
            "en": Path(self.EMAIL_TEMPLATE_PATH) / "en_verify_email.html",
            "es": Path(self.EMAIL_TEMPLATE_PATH) / "es_verify_email.html",
            "ca": Path(self.EMAIL_TEMPLATE_PATH) / "ca_verify_email.html",
        }

    @property
    def EMAIL_RESET_PASSWORD_TEMPLATE(self) -> dict:
        return {
            "en": Path(self.EMAIL_TEMPLATE_PATH) / "en_reset_password.html",
            "es": Path(self.EMAIL_TEMPLATE_PATH) / "es_reset_password.html",
            "ca": Path(self.EMAIL_TEMPLATE_PATH) / "ca_reset_password.html",
        }

    @property
    def STORAGE_UPLOADS(self) -> Path:
        return Path(self.STORAGE_ROOT) / "uploads"

    @property
    def STORAGE_CHUNK(self) -> Path:
        return Path(self.STORAGE_ROOT) / "chunk"


settings = Settings()
