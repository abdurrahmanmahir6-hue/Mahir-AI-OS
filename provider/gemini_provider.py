"""
gemini_provider.py

Skeleton for the Gemini provider.

Sprint 3 Task 1: structure only — no SDK import, no network calls, no
business logic. Sprint 3 Task 5 (future) will implement the TODO-marked
methods below using the actual Gemini SDK (google-genai).
"""

from __future__ import annotations

from typing import Any, Optional

from providers.base_provider import BaseProvider, ProviderConfig, ProviderResponse

PROVIDER_NAME = "gemini"


class GeminiProvider(BaseProvider):
    """
    Provider implementation for Google Gemini models.

    Currently a skeleton: no SDK import, no network calls. It implements
    the BaseProvider contract so it can be registered and swapped in/out
    without the Core Engine ever knowing this is specifically "Gemini".
    """

    def __init__(self) -> None:
        # TODO (Sprint 3 Task 5): store an SDK client instance here once
        # initialize() constructs it.
        self._config: Optional[ProviderConfig] = None
        self._client: Optional[Any] = None

    def initialize(self, config: ProviderConfig) -> None:
        # TODO (Sprint 3 Task 5): construct the Gemini SDK client using
        # config.api_key / config.model. Do not hardcode the model or key.
        self._config = config

    def generate(self, prompt: str, **kwargs: Any) -> ProviderResponse:
        # TODO (Sprint 3 Task 5): call the Gemini SDK and map its response
        # into ProviderResponse(content=..., provider_name=PROVIDER_NAME, raw=...).
        raise NotImplementedError("GeminiProvider.generate is not implemented yet.")

    def health_check(self) -> bool:
        # TODO (Sprint 3 Task 5): perform a lightweight call to confirm the
        # API key and network path are working.
        raise NotImplementedError("GeminiProvider.health_check is not implemented yet.")

    def close(self) -> None:
        # TODO (Sprint 3 Task 5): release/close the SDK client or session, if any.
        raise NotImplementedError("GeminiProvider.close is not implemented yet.")
