"""Typed, environment-backed application configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Process environment variables take precedence over values in the local .env file.
load_dotenv(PROJECT_ROOT / ".env", override=False)


class AppSettings(BaseSettings):
    """Configuration for the FastAPI application process."""

    model_config = SettingsConfigDict(env_prefix="APP_", extra="ignore", frozen=True)

    name: str
    environment: str
    debug: bool
    host: str
    port: int = Field(ge=1, le=65_535)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


class MongoDBSettings(BaseSettings):
    """MongoDB connection details and per-context logical database names."""

    model_config = SettingsConfigDict(env_prefix="MONGODB_", extra="ignore", frozen=True)

    uri: str
    catalog_database: str
    ordering_database: str
    inventory_database: str
    payment_database: str
    fulfillment_database: str


@dataclass(frozen=True, slots=True)
class Settings:
    """All validated process settings required by the application."""

    app: AppSettings
    mongodb: MongoDBSettings


def load_settings() -> Settings:
    """Create validated settings objects from the environment and local `.env`."""

    return Settings(app=AppSettings(), mongodb=MongoDBSettings())
