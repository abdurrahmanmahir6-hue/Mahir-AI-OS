"""
core/config.py
Responsible for:
    - Loading environment variables from .env via python-dotenv.
    - Validating required fields (API keys, log levels).
    - Providing a single source of truth for all system settings.
MAFS (Mahir Agentic Framework Standard) Compliance:
    - Ch.2 (Truth Over Flattery): Fails fast if required keys are missing.
    - Ch.2 (Security): Implements masked_summary() to prevent log leaks.
"""

from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when the configuration is invalid or missing required fields."""

    pass


@dataclass
class Config:
    """
    Application-wide configuration.
    Access values via attributes (e.g., config.openai_api_key).
    Use Config.load() to instantiate from environment variables.
    """

    # System Settings
    app_name: str = "Mahir AI OS"
    app_version: str = "AR1"
    environment: str = "development"
    log_level: str = "INFO"

    # API Keys (Secrets)
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None

    @classmethod
    def load(cls, dotenv_path: Optional[str] = None) -> Config:
        """
        Factory method to load config from environment variables.
        Args:
            dotenv_path: Optional path to a .env file.
        Returns:
            A populated Config instance.
        """
        load_dotenv(dotenv_path=dotenv_path)

        return Config(
            app_name=os.getenv("APP_NAME", "Mahir AI OS"),
            app_version=os.getenv("APP_VERSION", "AR1"),
            environment=os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "development")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
        )

    def validate(self, strict: bool = False) -> None:
        """
        Ensure the configuration is valid.
        Args:
            strict: If True, raises ConfigError if NO provider API key is set.
                   (Sprint 2 behavior: any key is enough).
        Raises:
            ConfigError: If validation fails in strict mode.
        """
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level not in valid_log_levels:
            raise ConfigError(f"Invalid LOG_LEVEL: {self.log_level}")

        if strict:
            has_any_key = any(
                [self.openai_api_key, self.gemini_api_key, self.tavily_api_key]
            )
            if not has_any_key:
                raise ConfigError(
                    "No provider API keys found. Set at least one of "
                    "OPENAI_API_KEY, GEMINI_API_KEY, TAVILY_API_KEY in .env."
                )

    def masked_summary(self) -> dict:
        """
        Returns a dictionary of config values with secrets masked.
        Use this for logging startup configuration.
        """

        def _mask(val: Optional[str]) -> str:
            if not val:
                return "not set"
            # Show first 4 and last 4 chars, mask the middle
            if len(val) <= 8:
                return "set (********)"
            return f"set ({val[:4]}...{val[-4:]})"

        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "environment": self.environment,
            "log_level": self.log_level,
            "openai_api_key": _mask(self.openai_api_key),
            "gemini_api_key": _mask(self.gemini_api_key),
            "tavily_api_key": _mask(self.tavily_api_key),
        }
