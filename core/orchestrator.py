"""
core/orchestrator.py

Responsible for:
    - Owning the top-level workflow:
          User -> Router -> Agent (future) -> Tool (future) -> Output
    - Wiring together Config, Logger, State, and Router.

Sprint 2 scope:
    - No Agent Layer or Tool Layer exists yet, so `process_input()`
      routes the input and returns a placeholder response describing
      what *would* happen, rather than executing an agent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.config import Config
from core.interfaces import ToolDispatcher
from core.logger import get_logger
from core.router import RouteResult, Router
from core.state import AppState, TaskStatus

logger = get_logger(__name__)


@dataclass
class OrchestratorResponse:
    """Structured result returned to the caller of the Orchestrator."""

    agent_id: str
    status: TaskStatus
    message: str


class Orchestrator:
    """
    Central coordinator for the system.

    Extension points:
        - `_dispatch_to_agent` is the single seam where the future
          Agent Layer plugs in (Sprint 3+). Nothing outside this
          method needs to change when real agents are added.
        - `_dispatch_to_tool` is reserved for the future Tool Layer
          and intentionally left unimplemented in Sprint 2.
    """

    def __init__(
        self,
        config: Config,
        state: Optional[AppState] = None,
        tool_dispatcher: Optional[ToolDispatcher] = None,
    ) -> None:
        """
        Args:
            config: Loaded application configuration.
            state: Optional existing AppState; a fresh one is created
                if not provided.
            tool_dispatcher: Optional Tool Layer implementation
                (see core/interfaces.py). None in Sprint 2, since no
                Tool Layer exists yet — `_dispatch_to_tool` degrades
                gracefully instead of raising when it's absent.
        """
        self.config = config
        self.state = state or AppState()
        self.router = Router()
        self.tool_dispatcher = tool_dispatcher
        logger.info("Orchestrator initialized (env=%s)", config.environment)

    def process_input(self, user_input: str) -> OrchestratorResponse:
        """
        Run one full pass of the workflow for a single piece of user input.

        Args:
            user_input: Raw text from the user.

        Returns:
            OrchestratorResponse describing the routing decision and
            current (placeholder) outcome.
        """
        self.state.task_status = TaskStatus.ROUTING
        route: RouteResult = self.router.route(user_input)
        self.state.selected_agent = route.agent_id

        return self._dispatch_to_agent(route, user_input)

    def _dispatch_to_agent(
        self, route: RouteResult, user_input: str
    ) -> OrchestratorResponse:
        """
        Placeholder dispatch step.

        Sprint 3 will replace this method's body with real Agent
        instantiation and execution, resolving route.agent_id to an
        Agent per its MAFS Ch.4 metadata (allowed_tools,
        allowed_memory_scope, max_autonomy_level, escalation_rule).
        """
        self.state.task_status = TaskStatus.WAITING_ON_HUMAN
        logger.warning(
            "Agent Layer not implemented yet (Sprint 3+). Would have routed to '%s'.",
            route.agent_id,
        )
        return OrchestratorResponse(
            agent_id=route.agent_id,
            status=self.state.task_status,
            message=(
                f"[Sprint 2 placeholder] Input would be handled by "
                f"'{route.agent_id}'. No Agent Layer exists yet."
            ),
        )

    def _dispatch_to_tool(self, tool_name: str, **kwargs: object) -> object:
        """
        Reserved seam for the future Tool Layer.

        Delegates to `self.tool_dispatcher` (a `ToolDispatcher`,
        see core/interfaces.py) if one was provided. If none was
        configured — the normal case in Sprint 2, since no Tool Layer
        exists yet — this logs a warning and returns None instead of
        crashing the whole pipeline with an unhandled exception.
        """
        if self.tool_dispatcher is None:
            logger.warning(
                "No ToolDispatcher configured; cannot dispatch to tool '%s'.",
                tool_name,
            )
            return None
        return self.tool_dispatcher.dispatch(tool_name, **kwargs)
