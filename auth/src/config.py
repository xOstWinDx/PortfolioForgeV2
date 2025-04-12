from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "auth"

    project_root: Path = Path(__file__).resolve().parent.parent

    current_kid: str = "2025-04-12"

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
