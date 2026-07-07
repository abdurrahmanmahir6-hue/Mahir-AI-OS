"""
provider_manager.py

Coordinates access to registered providers on behalf of the Core Engine.

Sprint 3 Task 1: coordination skeleton only.
    - No provider-selection logic yet (deciding WHICH provider to use for
      a given request) — arrives in a later task.
    - No fallback logic yet (what to do if a provider fails) — arrives in
      a later task.

The Core Engine should depend on ProviderManager, never on a concrete
provider class directly. This keeps Orchestrator/Router provider-agnostic,
per MAFS Chapter 3 (Architecture) and Chapter 9 (Coding Standard).
"""

from __future__ import annotations

from providers.base_provider import BaseProvider
from providers.registry import ProviderRegistry


class ProviderManager:
    """
    Coordinates registered providers for the Core Engine.

    Responsibilities (current, Sprint 3 Task 1):
        - Hold a reference to a ProviderRegistry.
        - Expose a way to fetch a specific, named provider.

    Explicitly NOT this class's responsibility yet:
        - Deciding which provider to use for a given request
          (future task: selection logic).
        - Falling back to a secondary provider on failure
          (future task: fallback logic).
    """

    def __init__(self, registry: ProviderRegistry) -> None:
        """
        Args:
            registry: The ProviderRegistry used to look up providers by name.
        """
        self._registry = registry

    def get_provider(self, name: str) -> BaseProvider:
        """
        Retrieve a registered provider by name.

        Args:
            name: Registered provider name (e.g. "openai", "gemini").

        Returns:
            BaseProvider: The requested provider instance.
        """
        return self._registry.get(name)

    # Extension point (future task — provider selection):
    # def select_provider(self, criteria: Any) -> BaseProvider: ...

    # Extension point (future task — fallback handling):
    # def generate_with_fallback(self, prompt: str, **kwargs: Any) -> ProviderResponse: ...
