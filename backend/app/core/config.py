from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

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

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"{self.DATABASE_DRIVER}://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}/{self.DATABASE_NAME}"
        )


settings = Settings()
