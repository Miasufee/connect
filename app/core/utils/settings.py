from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pydantic_settings import BaseSettings

@dataclass
class TokenConfig:
    secret: str
    algorithm: str
    expire_seconds: int
    allow_login: bool = False


class Settings(BaseSettings):
    # -----------------------
    # App
    # -----------------------
    APP_ENV: str = ""
    APP_SECRET_KEY: str = ""
    APP_DEBUG: bool = False
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    REDIRECT_URI: str = ""

    STORAGE_BACKEND: str = "local"

    # -----------------------
    # MongoDB
    # -----------------------
    MONGO_HOST: str = ""
    MONGO_PORT: int = 27017
    MONGO_USER: str = ""
    MONGO_PASSWORD: str = ""
    MONGO_DB: str = "mia"
    MONGO_AUTH_SOURCE: str = ""
    MONGO_URI: str | None = None

    # === API Security ===
    API_SUPERUSER_EMAIL: str = ""
    API_SUPERUSER_SECRET_KEY: str = ""

    FRONTEND_URL: str = ""

    MEDIA_BASE_URL: str = ""

    EMAIL_HOST: str = ""
    EMAIL_PORT: int = 587
    EMAIL_USE_TLS: bool = True
    EMAIL_HOST_USER: str = ""
    EMAIL_HOST_PASSWORD: str = ""
    DEFAULT_FROM_EMAIL: str = ""
    EMAIL_TIMEOUT: int = 30

    # -----------------------
    # JWT
    # -----------------------
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    PASSWORD_RESET_SECRET_KEY: str = ""
    PASSWORD_RESET_ALGORITHM: str = ""
    PASSWORD_RESET_MINUTES_EXPIRE: int = 15

    # -----------------------
    # CORS
    # -----------------------
    CORS_ALLOWED_ORIGINS: str = "*"
    CORS_ALLOWED_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS"
    CORS_ALLOWED_HEADERS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_EXPOSE_HEADERS: str = "*"

    # -----------------------
    # Redis (Optional)
    # -----------------------
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    # -----------------------
    # Logging
    # -----------------------
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    LOG_FILE: str | None = None
    log_level: str = "INFO"
    log_format: str = "json"
    otel_enabled: bool = False
    otel_exporter_endpoint: Optional[str] = None
    prometheus_multiproc_dir: str = "/tmp/prometheus_multiproc"

    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET_NAME: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    # -----------------------
    # Helper Properties
    # -----------------------
    @property
    def mongo_url(self) -> str:
        """Build the MongoDB URI if not explicitly set"""
        if self.MONGO_URI:
            return self.MONGO_URI
        if self.MONGO_USER and self.MONGO_PASSWORD:
            return (f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:"
                    f"{self.MONGO_PORT}/{self.MONGO_DB}?authSource={self.MONGO_AUTH_SOURCE}")
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"

    @property
    def redis_url(self) -> str:
        """Build the Redis connection URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def DEFAULT_TOKEN_CONFIGS(self) -> dict:
        """Centralized per-token security settings."""
        return {
            "access": TokenConfig(
                secret=self.JWT_SECRET_KEY,
                algorithm=self.JWT_ALGORITHM,
                expire_seconds=self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                allow_login=True,
            ),
            "refresh": TokenConfig(
                secret=self.JWT_SECRET_KEY,
                algorithm=self.JWT_ALGORITHM,
                expire_seconds=self.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
                allow_login=False,
            ),
            "password_reset": TokenConfig(
                secret=self.PASSWORD_RESET_SECRET_KEY,
                algorithm=self.PASSWORD_RESET_ALGORITHM,
                expire_seconds=self.PASSWORD_RESET_MINUTES_EXPIRE * 60,
                allow_login=False,
            ),
            "email_verification": TokenConfig(
                secret=self.JWT_SECRET_KEY,
                algorithm=self.JWT_ALGORITHM,
                expire_seconds=24 * 3600,
                allow_login=False,
            ),
        }

# Instantiate settings
settings = Settings()
