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
            environment=os.getenv("APP_ENV", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
        )

    def validate(self, strict: bool = False) -> None:
        """
        Ensure the configuration is valid.
        Args:
            strict: If True, raises ConfigError if any API key is missing.
                   If False (Sprint 2 default), only warns or logs.
        Raises:
            ConfigError: If validation fails in strict mode.
        """
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level not in valid_log_levels:
            raise ConfigError(f"Invalid LOG_LEVEL: {self.log_level}")

        if strict:
            missing = []
            if not self.openai_api_key: missing.append("OPENAI_API_KEY")
            if not self.gemini_api_key: missing.append("GEMINI_API_KEY")
            if not self.tavily_api_key: missing.append("TAVILY_API_KEY")
            
            if missing:
                raise ConfigError(f"Missing required API keys: {', '.join(missing)}")

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
            "app_version": self.app_version,
            "environment": self.environment,
            "log_level": self.log_level,
            "openai_api_key": _mask(self.openai_api_key),
            "gemini_api_key": _mask(self.gemini_api_key),
            "tavily_api_key": _mask(self.tavily_api_key),
        }
