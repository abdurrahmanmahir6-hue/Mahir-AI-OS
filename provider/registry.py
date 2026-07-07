"""
registry.py

A simple registry mapping provider names to provider instances.

Responsibilities:
    - register(name, provider): add a provider under a unique name.
    - get(name): retrieve a previously registered provider.
    - is_registered(name): check whether a name is already taken.

Design goal — Open/Closed Principle:
    New providers (Claude, Grok, DeepSeek, Ollama, OpenRouter, ...) register
    themselves under a name. Nothing in this file, in ProviderManager, or
    in the Core Engine needs to change when a new provider is added.
"""

from __future__ import annotations

from providers.base_provider import BaseProvider


class ProviderRegistry:
    """
    Holds all known provider instances, keyed by name.

    This class does not decide which provider is "best" for a request —
    it is a plain lookup table. Selection/fallback logic lives one layer
    up, in ProviderManager (added in a later task).
    """

    def __init__(self) -> None:
        self._providers: dict[str, BaseProvider] = {}

    def register(self, name: str, provider: BaseProvider) -> None:
        """
        Register a provider under a unique name.

        Args:
            name: Unique identifier for the provider (e.g. "openai", "gemini").
            provider: A BaseProvider instance.

        Raises:
            ValueError: If `name` is already registered.
        """
        if name in self._providers:
            raise ValueError(f"Provider '{name}' is already registered.")
        self._providers[name] = provider

    def get(self, name: str) -> BaseProvider:
        """
        Retrieve a registered provider by name.

        Args:
            name: The provider's registered name.

        Returns:
            BaseProvider: The registered provider instance.

        Raises:
            KeyError: If no provider is registered under `name`.
        """
        if name not in self._providers:
            raise KeyError(f"Provider '{name}' is not registered.")
        return self._providers[name]

    def is_registered(self, name: str) -> bool:
        """
        Check whether a provider name is already registered.

        Args:
            name: The provider name to check.

        Returns:
            bool: True if registered, False otherwise.
        """
        return name in self._providers
