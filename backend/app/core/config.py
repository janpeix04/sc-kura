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


settings = Settings()
