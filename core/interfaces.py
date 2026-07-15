"""
core/interfaces.py

Responsible for:
    - Defining abstract contracts (ABCs) for layers that don't exist
      yet, so the Orchestrator can depend on a stable interface
      instead of a bare `raise NotImplementedError`.

Sprint 2 scope:
    - Only the Tool Layer contract is defined here (`ToolDispatcher`),
      since that's the seam `Orchestrator._dispatch_to_tool` needs.
    - No concrete implementation is provided — that's a future sprint.
      Orchestrator works today with zero dispatcher configured; it
      simply has nothing to dispatch to yet.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ToolDispatcher(ABC):
    """
    Contract for the future Tool Layer (IB-AR Ch.7 — Tool Rules).

    Any concrete Tool Layer implementation plugs into the Orchestrator
    by implementing `dispatch()`. This keeps the Orchestrator's code
    unchanged when the real Tool Layer is built — it only ever talks
    to this interface, never to a specific tool implementation.
    """

    @abstractmethod
    def dispatch(self, tool_name: str, **kwargs: Any) -> Any:
        """
        Execute a named tool with the given keyword arguments.

        Args:
            tool_name: Registered name of the tool to invoke.
            **kwargs: Tool-specific arguments.

        Returns:
            Whatever the tool implementation returns.

        Implementations must honor IB-AR Ch.7: destructive actions
        (delete/send/pay) require confirmation, every call must be
        logged, and permission scope must be enforced before the
        underlying action runs.
        """
        raise NotImplementedError
