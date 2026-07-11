"""
providers package

Public exports for the Provider Layer.

Core Engine code should import from `providers` directly:

    from providers import BaseProvider, ProviderManager, ProviderRegistry

...instead of reaching into individual submodules. This keeps the internal
file layout free to change without breaking Core Engine imports.

Note: concrete providers (OpenAIProvider, GeminiProvider) are exported here
for convenience at the composition root (e.g. main.py, where providers are
constructed and registered) — but the Core Engine itself (Orchestrator,
Router, ProviderManager) should only ever type-hint against BaseProvider.
"""

from providers.base_provider import BaseProvider, ProviderConfig, ProviderResponse
from providers.gemini_provider import GeminiProvider
from providers.openai_provider import OpenAIProvider
from providers.provider_manager import ProviderManager
from providers.registry import ProviderRegistry
from providers.groq_provider import GroqProvider

__all__ = [
    "BaseProvider",
    "ProviderConfig",
    "ProviderResponse",
    "ProviderManager",
    "ProviderRegistry",
    "OpenAIProvider",
    "GeminiProvider",
    "GroqProvider",
]
