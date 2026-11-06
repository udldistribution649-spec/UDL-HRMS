import os

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = os.getenv("HRMS_ENV_FILE", ".env")


class Settings(BaseSettings):
    APP_NAME: str = "UDL HRMS API"
    APP_ENV: str = "development"

    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str = "udl_hrms_db"
    DB_USER: str = "udl_hrms_app"
    DB_PASSWORD: str
    SOURCE_DB_ENCRYPTION_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
