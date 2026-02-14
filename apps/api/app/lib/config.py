"""Application configuration from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Firebase
    firebase_project_id: str = "mcontrol-dev"

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""

    # Credential encryption (base64-encoded 32-byte AES-256-GCM key)
    credential_encryption_key: str = ""

    # Development mode
    auth_disabled: bool = True

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_base_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
