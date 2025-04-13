from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "auth"

    project_root: Path = Path(__file__).resolve().parent.parent

    CURRENT_KID: str = "2025-04-12"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int

    @property
    def RABBITMQ_URL(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}"

    REDIS_URL: str

    ACCESS_TOKEN_EXPIRES: int = 30 * 60  # 30 minutes
    REFRESH_TOKEN_EXPIRES: int = 90 * 24 * 60 * 60  # 90 days

    ALGORITHM: str = "RS256"

    @computed_field
    @property
    def __PRIVATE_KEY_PATH(self) -> Path:
        return self.project_root / "private_key.pem"

    @computed_field
    @property
    def PUBLIC_KEY_PATH(self) -> Path:
        return self.project_root / "public_key.pem"

    @computed_field
    @property
    def _PRIVATE_KEY(self) -> RSAPrivateKey:
        with open(self.__PRIVATE_KEY_PATH, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
            return private_key

    @computed_field
    @property
    def PUBLIC_KEY(self) -> RSAPublicKey:
        with open(self.PUBLIC_KEY_PATH, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
        return public_key

    ALLOWED_MIME_TYPES: set[str] = {"image/webp", "image/jpeg", "image/png"}
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5 МБ
    DEFAULT_PHOTO_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_ENDPOINT_URL: str
    S3_BUCKET_NAME: str
    S3_PUBLIC_DOMAIN: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
