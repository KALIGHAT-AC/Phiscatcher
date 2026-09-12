"""Centralized, environment-driven application settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the backend foundation."""

    app_name: str = "Phiscatcher API"
    environment: str = "development"
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    frontend_origins: str = "http://localhost:5173"
    analysis_timeout_seconds: float = Field(default=300.0, gt=0)
    max_concurrent_analyses: int = Field(default=2, ge=1)
    session_retention_seconds: float = Field(default=3600.0, ge=0)
    log_level: str = "INFO"
    pcap_output_directory: str = "../packet-captures/raw"
    websocket_event_history_limit: int = Field(default=50, ge=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PHISCATCHER_",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        """Split the deliberately simple comma-separated environment value."""
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
