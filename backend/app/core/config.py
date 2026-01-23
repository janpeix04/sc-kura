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


settings = Settings()
