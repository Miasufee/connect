from pydantic_settings import BaseSettings
from pydantic import (
    AnyUrl,
    PostgresDsn,
    EmailStr,
    field_validator,
    ValidationInfo
)
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Application Configuration
    APP_ENV: str = "production"
    APP_SECRET_KEY: str
    APP_DEBUG: bool = False

    # Database Configuration
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    DB_POOL_MIN: int = 2
    DB_POOL_MAX: int = 20
    DB_POOL_TIMEOUT: int = 30

    # API Superuser Configuration
    API_SUPERUSER_USERNAME: str
    API_SUPERUSER_PASSWORD: str
    API_SUPERUSER_EMAIL: EmailStr
    API_SUPERUSER_SECRET_KEY: str

    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Configuration
    CORS_ALLOWED_ORIGINS: str
    CORS_ALLOWED_METHODS: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    CORS_ALLOWED_HEADERS: str = "Authorization,Content-Type"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_EXPOSE_HEADERS: str = "Content-Disposition"

    # Constructed Settings
    DATABASE_URL: Optional[str] = None
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    CORS_ORIGINS: List[str] = []
    CORS_METHODS: List[str] = []
    CORS_HEADERS: List[str] = []

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: Optional[str], info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        values = info.data
        return (
            f"postgresql+psycopg://{values['POSTGRES_USER']}:{values['POSTGRES_PASSWORD']}@"
            f"{values['POSTGRES_HOST']}:{values['POSTGRES_PORT']}/{values['POSTGRES_DB']}"
        )

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_sqlalchemy_uri(cls, v: Optional[str], info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        values = info.data
        return (
            f"postgresql+asyncpg://{values['POSTGRES_USER']}:{values['POSTGRES_PASSWORD']}@"
            f"{values['POSTGRES_HOST']}:{values['POSTGRES_PORT']}/{values['POSTGRES_DB']}"
        )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Optional[List[str]], info: ValidationInfo) -> List[str]:
        if isinstance(v, list):
            return v
        return [origin.strip() for origin in info.data.get("CORS_ALLOWED_ORIGINS", "").split(",") if origin.strip()]

    @field_validator("CORS_METHODS", mode="before")
    @classmethod
    def assemble_cors_methods(cls, v: Optional[List[str]], info: ValidationInfo) -> List[str]:
        if isinstance(v, list):
            return v
        return [method.strip() for method in info.data.get("CORS_ALLOWED_METHODS", "").split(",") if method.strip()]

    @field_validator("CORS_HEADERS", mode="before")
    @classmethod
    def assemble_cors_headers(cls, v: Optional[List[str]], info: ValidationInfo) -> List[str]:
        if isinstance(v, list):
            return v
        return [header.strip() for header in info.data.get("CORS_ALLOWED_HEADERS", "").split(",") if header.strip()]

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
