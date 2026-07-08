"""
tests/test_orchestrator.py

Covers core/orchestrator.py:
    - process_input() routes and returns a placeholder response,
      updating state.selected_agent and state.task_status.
    - _dispatch_to_tool() degrades gracefully (returns None, logs a
      warning) when no ToolDispatcher is configured, instead of
      raising NotImplementedError.
    - _dispatch_to_tool() delegates to an injected ToolDispatcher when
      one is provided.
"""

from __future__ import annotations

import unittest
from typing import Any

from core.config import Config
from core.interfaces import ToolDispatcher
from core.orchestrator import Orchestrator
from core.state import AppState, TaskStatus


class FakeToolDispatcher(ToolDispatcher):
    """Test double recording every dispatch() call it receives."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def dispatch(self, tool_name: str, **kwargs: Any) -> Any:
        self.calls.append((tool_name, kwargs))
        return f"handled:{tool_name}"


class TestOrchestratorProcessInput(unittest.TestCase):
    def setUp(self) -> None:
        self.config = Config()
        self.state = AppState()
        self.orchestrator = Orchestrator(config=self.config, state=self.state)

    def test_process_input_routes_and_updates_state(self) -> None:
        result = self.orchestrator.process_input("please fix this python bug")

        self.assertEqual(result.agent_id, "coding_agent")
        self.assertEqual(self.state.selected_agent, "coding_agent")
        self.assertEqual(result.status, TaskStatus.WAITING_ON_HUMAN)
        self.assertIn("coding_agent", result.message)

    def test_process_input_falls_back_to_general_agent(self) -> None:
        result = self.orchestrator.process_input("good morning")
        self.assertEqual(result.agent_id, "general_agent")


class TestOrchestratorToolDispatch(unittest.TestCase):
    def test_dispatch_to_tool_without_dispatcher_returns_none(self) -> None:
        orchestrator = Orchestrator(config=Config())
        result = orchestrator._dispatch_to_tool("some_tool")
        self.assertIsNone(result)

    def test_dispatch_to_tool_delegates_to_injected_dispatcher(self) -> None:
        fake_dispatcher = FakeToolDispatcher()
        orchestrator = Orchestrator(config=Config(), tool_dispatcher=fake_dispatcher)

        result = orchestrator._dispatch_to_tool("send_email", to="a@example.com")

        self.assertEqual(result, "handled:send_email")
        self.assertEqual(
            fake_dispatcher.calls, [("send_email", {"to": "a@example.com"})]
        )


if __name__ == "__main__":
    unittest.main()
