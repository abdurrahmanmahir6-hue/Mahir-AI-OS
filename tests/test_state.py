"""
tests/test_state.py

Covers core/state.py:
    - start_session() sets user/session and resets task_status to IDLE.
    - end_session() marks the session inactive.
    - reset_task() clears agent, skill, AND model (this used to leave
      selected_model stale — regression test for that fix).
"""

from __future__ import annotations

import unittest

from core.state import AppState, TaskStatus


class TestAppStateSession(unittest.TestCase):
    def test_start_session_sets_user_and_session(self) -> None:
        state = AppState()
        state.start_session(session_id="abc-123", user="alice")

        self.assertIsNotNone(state.current_session)
        assert state.current_session is not None
        self.assertEqual(state.current_session.session_id, "abc-123")
        self.assertTrue(state.current_session.is_active)
        self.assertEqual(state.current_user, "alice")
        self.assertEqual(state.task_status, TaskStatus.IDLE)

    def test_end_session_marks_inactive(self) -> None:
        state = AppState()
        state.start_session(session_id="abc-123")
        state.end_session()

        self.assertIsNotNone(state.current_session)
        assert state.current_session is not None
        self.assertFalse(state.current_session.is_active)
        self.assertEqual(state.task_status, TaskStatus.IDLE)

    def test_end_session_without_active_session_does_not_crash(self) -> None:
        state = AppState()
        state.end_session()  # no session started; must not raise
        self.assertIsNone(state.current_session)


class TestAppStateResetTask(unittest.TestCase):
    def test_reset_task_clears_agent_skill_and_model(self) -> None:
        state = AppState()
        state.selected_agent = "coding_agent"
        state.selected_skill = "summarize_document"
        state.selected_model = "gpt-4"
        state.task_status = TaskStatus.RUNNING

        state.reset_task()

        self.assertIsNone(state.selected_agent)
        self.assertIsNone(state.selected_skill)
        self.assertIsNone(state.selected_model)  # regression: was NOT reset before
        self.assertEqual(state.task_status, TaskStatus.IDLE)

    def test_reset_task_preserves_session_and_user(self) -> None:
        state = AppState()
        state.start_session(session_id="abc-123", user="alice")
        state.selected_agent = "coding_agent"

        state.reset_task()

        self.assertEqual(state.current_user, "alice")
        self.assertIsNotNone(state.current_session)


if __name__ == "__main__":
    unittest.main()
