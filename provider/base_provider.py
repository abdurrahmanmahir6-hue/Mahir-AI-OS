"""
base_provider.py

Defines the abstract contract that every AI provider (OpenAI, Gemini, Claude,
Grok, DeepSeek, Ollama, OpenRouter, ...) must implement.

This module contains NO implementation logic. It exists purely to define
the shape of a "Provider" so the Core Engine (Orchestrator / Router) can
depend on this abstraction instead of any concrete provider.

Design principle — Dependency Inversion Principle (DIP):
    - Core Engine depends on BaseProvider (an abstraction).
    - Concrete providers depend on BaseProvider (an abstraction).
    - Core Engine never depends on OpenAIProvider / GeminiProvider directly.

MAFS alignment:
    - Chapter 2 (Modular Design): each provider is a self-contained module.
    - Chapter 7 (Tool Rules): input/output schema is declared up front,
      before any provider is implemented.
    - Chapter 10 (Security): no credentials are ever hardcoded here; a
      config object is passed in from the outside (env vars / secret manager).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ProviderConfig:
    """
    Canonical configuration contract passed to a provider's initialize().

    Concrete providers may ignore fields they don't need, but the shape
    stays identical across all providers — so the Core Engine never has
    to special-case a specific provider's config format.

    Attributes:
        api_key: Secret credential for the provider. Sourced from
            environment variables / config.py — never hardcoded, never logged.
        model: Model identifier (e.g. "gpt-4o", "gemini-1.5-pro").
            Never hardcoded inside a provider class itself.
        extra: Provider-specific overrides that don't fit the common shape.
            Kept intentionally open-ended so a brand-new provider never
            forces a change to this dataclass.
    """

    api_key: Optional[str] = None
    model: Optional[str] = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderResponse:
    """
    Canonical response contract returned by generate().

    Every provider must translate its own native SDK/API response into
    this shape. This is what keeps the Orchestrator provider-agnostic:
    it only ever reads a ProviderResponse, never a raw OpenAI/Gemini object.

    Attributes:
        content: The generated text.
        provider_name: Which provider produced this response — used for
            logging and audit trails (MAFS Chapter 10 — Audit Trail).
        raw: The untouched original SDK/API response, kept for debugging
            only. Core Engine code must never depend on the shape of `raw`.
    """

    content: str
    provider_name: str
    raw: Any = None


class BaseProvider(ABC):
    """
    Abstract base class that every AI provider must implement.

    This class defines ONLY the public API surface. It contains no
    implementation — concrete behavior belongs to subclasses such as
    OpenAIProvider or GeminiProvider (implemented in a later Sprint 3 task).

    Lifecycle contract:
        1. initialize()   — set up a client/session using ProviderConfig.
        2. generate()      — perform a single generation call.
        3. health_check()  — verify the provider is reachable/usable.
        4. close()         — release any held resources (sessions, connections).
    """

    @abstractmethod
    def initialize(self, config: ProviderConfig) -> None:
        """
        Prepare the provider for use (e.g. construct an SDK client).

        Args:
            config: Canonical provider configuration (API key, model, etc).
        """
        raise NotImplementedError

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> ProviderResponse:
        """
        Generate a completion for the given prompt.

        Args:
            prompt: The input text/instruction to send to the provider.
            **kwargs: Provider-specific generation parameters (temperature,
                max_tokens, etc). Left open so new providers can accept new
                parameters without changing this method's signature.

        Returns:
            ProviderResponse: A canonical, provider-agnostic response.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check whether the provider is currently reachable and usable.

        Returns:
            bool: True if healthy, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """
        Release any resources held by the provider (sessions, connections).
        """
        raise NotImplementedError
