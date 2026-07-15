"""
core/startup_validation.py

Sprint 3, Task 3 — Environment Validation.

Runs fail-fast checks against an already-built Config (and, optionally, a
live ProviderRegistry) before the application starts serving requests.
This module deliberately sits one layer above core/config.py:

    core/config.py             -> reads env vars, coerces types (permissive)
    core/startup_validation.py -> judges whether those values are usable
    providers/registry.py      -> (optional) cross-checked, never modified

Why a separate module instead of adding these checks to Config.validate()?
----------------------------------------------------------------------------
core/config.py is a frozen/stable file for this task. Its own docstring also
states it is intentionally the ONLY place that reads environment variables
and has zero dependency on the providers/ package. This module is the one
place deliberately allowed to depend on both core.config and
providers.registry — cross-cutting startup checks are their own concern,
distinct from "load config" (core/config.py) and "define a provider"
(providers/base_provider.py, providers/registry.py). Keeping this logic out
of config.py also means config.py's diff for Task 3 stayed to four new,
permissively-parsed fields — nothing existing there changed shape.

Security contract
------------------
Only presence/absence of an API key is ever checked. The raw secret string
is never read, printed, or included in an exception message (IB-AR Chapter 10
— Security; Chapter 2 — Transparency without leaking secrets).
"""

from __future__ import annotations

from typing import Optional

from core.config import Config, ConfigError, get_config
from providers.registry import ProviderRegistry


class StartupValidationError(ConfigError):
    """
    Raised when the environment loaded successfully but is not safe to run.

    Subclasses ConfigError so existing ``except ConfigError`` call sites
    (e.g. a future main.py startup handler) catch this without needing to
    know about a new exception type.
    """


# Providers this codebase is designed to support (MAFS Chapter 3: Modular
# Design / Open-Closed Principle). "tavily" is deliberately excluded: it is
# a search-tool credential (config.providers.tavily_api_key), not a
# selectable BaseProvider for generation, so it is not a valid
# ACTIVE_PROVIDER value.
KNOWN_LLM_PROVIDERS: frozenset[str] = frozenset(
    {"openai", "gemini", "claude", "grok", "deepseek", "openrouter", "ollama", "groq"}
)

# Providers that operate without an API key (e.g. a local Ollama server).
_NO_KEY_REQUIRED: frozenset[str] = frozenset({"ollama"})

# Conventional generation-temperature bounds shared by every major provider.
_MIN_TEMPERATURE = 0.0
_MAX_TEMPERATURE = 2.0


def validate_startup_environment(
    config: Optional[Config] = None,
    registry: Optional[ProviderRegistry] = None,
) -> Config:
    """
    Run every Sprint 3 Task 3 startup check. Fails fast on the first problem.

    Checks, in order:
        1. The Config object exists.
        2. ACTIVE_PROVIDER names a known provider.
        3. MODEL_NAME is set for that provider.
        4. PROVIDER_TIMEOUT_SECONDS is a positive, finite number.
        5. TEMPERATURE is within the conventional 0.0-2.0 range.
        6. An API key is present for the *selected* provider only.

    Args:
        config: Config instance to validate. Defaults to the process-wide
            ``get_config()`` singleton when omitted.
        registry: An optional, already-populated ProviderRegistry. When
            given, provider-name validity is *also* checked against what is
            actually registered at runtime (stricter). When omitted — the
            case throughout Sprint 3, since no provider is registered yet —
            validation falls back to the static KNOWN_LLM_PROVIDERS list.
            This makes the same function usable today and automatically
            stricter from Sprint 5/6 onward, with no change to this file.

    Returns:
        Config: the same config, unchanged, for convenient chaining, e.g.
        ``config = validate_startup_environment()``.

    Raises:
        StartupValidationError: On the first failed check. The message
            always names which *setting* is wrong, never a secret value.
    """
    if config is None:
        config = get_config()

    if config is None:
        # Defensive: get_config() cannot actually return None (it either
        # returns a Config or raises), but Task 3 explicitly requires
        # checking that "Configuration object exists" — this makes that
        # requirement an executable, testable check rather than an assumption.
        raise StartupValidationError(
            "Configuration object does not exist (get_config() returned None)."
        )

    _validate_provider_name(config, registry)
    _validate_model_name(config)
    _validate_timeout(config)
    _validate_temperature(config)
    _validate_required_api_key(config)

    return config


def _validate_provider_name(
    config: Config, registry: Optional[ProviderRegistry]
) -> None:
    """Provider name validity (structural, plus an optional registry check)."""
    name = config.providers.active_provider

    if not name or not name.strip():
        raise StartupValidationError(
            "ACTIVE_PROVIDER is empty. Set it to one of: "
            f"{', '.join(sorted(KNOWN_LLM_PROVIDERS))}."
        )

    if name not in KNOWN_LLM_PROVIDERS:
        raise StartupValidationError(
            f"ACTIVE_PROVIDER={name!r} is not a known provider. "
            f"Must be one of: {', '.join(sorted(KNOWN_LLM_PROVIDERS))}."
        )

    if registry is not None and not registry.is_registered(name):
        raise StartupValidationError(
            f"ACTIVE_PROVIDER={name!r} is not registered in the provider "
            "registry. Register it (registry.register(...)) before startup."
        )


def _validate_model_name(config: Config) -> None:
    """
    Model name validity (structural only).

    A live check against a provider's *actual* model list would require an
    API call, which is out of scope for Task 3 (no SDK calls are allowed
    yet). This checks only that a value is present and non-blank; a
    genuinely unknown model name surfaces as a provider-side error once
    generate() is implemented in Sprint 5/6.
    """
    model = config.providers.model
    if not model or not model.strip():
        raise StartupValidationError(
            "MODEL_NAME is empty. Set the model identifier for "
            f"ACTIVE_PROVIDER={config.providers.active_provider!r} "
            "(e.g. MODEL_NAME=gpt-4o)."
        )


def _validate_timeout(config: Config) -> None:
    """Timeout value must be a positive, finite number of seconds."""
    timeout = config.providers.timeout_seconds
    if timeout != timeout or timeout in (float("inf"), float("-inf")):  # NaN / inf guard
        raise StartupValidationError(
            f"PROVIDER_TIMEOUT_SECONDS={timeout!r} is not a finite number."
        )
    if timeout <= 0:
        raise StartupValidationError(
            f"PROVIDER_TIMEOUT_SECONDS must be > 0, got {timeout!r}."
        )


def _validate_temperature(config: Config) -> None:
    """Temperature must fall within the conventional 0.0-2.0 range."""
    temperature = config.providers.temperature
    if not (_MIN_TEMPERATURE <= temperature <= _MAX_TEMPERATURE):
        raise StartupValidationError(
            f"TEMPERATURE must be between {_MIN_TEMPERATURE} and "
            f"{_MAX_TEMPERATURE}, got {temperature!r}."
        )


def _validate_required_api_key(config: Config) -> None:
    """
    Required API key ONLY for the currently selected provider.

    Providers that are not selected are never checked — e.g. a missing
    GEMINI_API_KEY must not block startup when ACTIVE_PROVIDER=openai.
    """
    active = config.providers.active_provider
    if active in _NO_KEY_REQUIRED:
        return

    key = config.providers.get_key(active)
    if not key:
        raise StartupValidationError(
            f"ACTIVE_PROVIDER={active!r} requires an API key, but none is "
            f"set. Set {active.upper()}_API_KEY in .env."
        )
