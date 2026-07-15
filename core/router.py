"""
core/router.py

Responsible for:
    - Determining which Agent should handle a given piece of user input.

Sprint 2 scope:
    - No AI is used for routing yet — routing is simple keyword
      matching.
    - No real Agents exist yet, so the router returns an *agent_id
      string* (per IB-AR Ch.4 agent_id convention) rather than an Agent
      instance. Sprint 3 can introduce a real Agent Layer and have the
      Orchestrator resolve agent_id -> Agent instance, without
      changing this file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Pattern

from core.logger import get_logger

logger = get_logger(__name__)

DEFAULT_AGENT_ID = "general_agent"


@dataclass
class RouteResult:
    """Result of a routing decision."""

    agent_id: str
    matched_keyword: Optional[str] = None


class Router:
    """
    Maps user intent to an agent_id using a simple, extensible registry.

    Extension point:
        Call `register(agent_id, keywords)` to add new routes without
        modifying this class. A future version can replace the
        keyword matcher with a real intent-classification model while
        keeping the same `route()` interface, so the Orchestrator
        never has to change.
    """

    def __init__(self) -> None:
        # agent_id -> list of (original_keyword, compiled_pattern)
        self._routes: Dict[str, List["tuple[str, Pattern[str]]"]] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register the initial, minimal set of routes."""
        self.register("coding_agent", ["code", "coding", "bug", "python", "script"])
        self.register("research_agent", ["research", "search", "find", "look up"])

    @staticmethod
    def _compile_keyword(keyword: str) -> Pattern[str]:
        """
        Compile a keyword/phrase into a whole-word regex pattern.

        Using `\\b` word boundaries (instead of naive substring search)
        prevents false positives where the keyword is only a fragment
        of an unrelated word. Keyword "code" correctly matches the
        standalone word "code" (e.g. "zip code") but no longer matches
        inside "encode", "decode", or "barcode". Likewise "search" no
        longer matches inside "research" or "researching".
        """
        return re.compile(r"\b" + re.escape(keyword.lower()) + r"\b")

    def register(self, agent_id: str, keywords: List[str]) -> None:
        """
        Register keywords that should route to a given agent_id.

        Args:
            agent_id: The agent_id to route matching input to.
            keywords: Keywords/phrases (case-insensitive) that trigger
                this route. Matched as whole words/phrases, not raw
                substrings.
        """
        self._routes[agent_id] = [
            (keyword, self._compile_keyword(keyword)) for keyword in keywords
        ]
        logger.debug("Registered route: %s -> %s", agent_id, keywords)

    def route(self, user_input: str) -> RouteResult:
        """
        Decide which agent_id should handle the given input.

        Args:
            user_input: Raw text from the user.

        Returns:
            RouteResult with the resolved agent_id. Falls back to
            DEFAULT_AGENT_ID when no keyword matches.
        """
        text = user_input.lower()
        for agent_id, keyword_patterns in self._routes.items():
            for keyword, pattern in keyword_patterns:
                if pattern.search(text):
                    logger.info(
                        "Routed input to '%s' (matched '%s')", agent_id, keyword
                    )
                    return RouteResult(agent_id=agent_id, matched_keyword=keyword)

        logger.info("No keyword match; falling back to '%s'", DEFAULT_AGENT_ID)
        return RouteResult(agent_id=DEFAULT_AGENT_ID, matched_keyword=None)
