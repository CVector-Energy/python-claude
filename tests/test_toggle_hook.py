"""Tests for ToggleHook."""

import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

from python_claude.hooks.base import HookInput
from python_claude.hooks.state import QualityCheckState
from python_claude.hooks.toggle_hook import ToggleHook


class TestToggleHook:
    def test_toggle_pytest(self, tmp_path: Path, capsys: Any) -> None:
        """Test toggling pytest from enabled to disabled."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            # Mock sys.argv to provide the check name
            with patch.object(sys, "argv", ["python-claude", "toggle", "pytest"]):
                hook = ToggleHook(hook_input)
                exit_code = hook.run()
                assert exit_code == 0

                captured = capsys.readouterr()
                assert "Pytest is now disabled" in captured.out

                # Verify state was actually changed
                state = QualityCheckState(tmp_path)
                assert not state.is_enabled("pytest")

    def test_toggle_mypy(self, tmp_path: Path, capsys: Any) -> None:
        """Test toggling mypy from enabled to disabled."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            with patch.object(sys, "argv", ["python-claude", "toggle", "mypy"]):
                hook = ToggleHook(hook_input)
                exit_code = hook.run()
                assert exit_code == 0

                captured = capsys.readouterr()
                assert "Mypy is now disabled" in captured.out

                state = QualityCheckState(tmp_path)
                assert not state.is_enabled("mypy")

    def test_toggle_ruff(self, tmp_path: Path, capsys: Any) -> None:
        """Test toggling ruff from enabled to disabled."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            with patch.object(sys, "argv", ["python-claude", "toggle", "ruff"]):
                hook = ToggleHook(hook_input)
                exit_code = hook.run()
                assert exit_code == 0

                captured = capsys.readouterr()
                assert "Ruff is now disabled" in captured.out

                state = QualityCheckState(tmp_path)
                assert not state.is_enabled("ruff")

    def test_toggle_twice_returns_to_enabled(self, tmp_path: Path, capsys: Any) -> None:
        """Test toggling twice returns check to enabled state."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            with patch.object(sys, "argv", ["python-claude", "toggle", "pytest"]):
                # First toggle: disable
                hook1 = ToggleHook(hook_input)
                hook1.run()

                # Second toggle: enable
                hook2 = ToggleHook(hook_input)
                exit_code = hook2.run()
                assert exit_code == 0

                captured = capsys.readouterr()
                assert "Pytest is now enabled" in captured.out

                state = QualityCheckState(tmp_path)
                assert state.is_enabled("pytest")

    def test_missing_check_name(self, tmp_path: Path, capsys: Any) -> None:
        """Test that missing check name returns error."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            with patch.object(sys, "argv", ["python-claude", "toggle"]):
                hook = ToggleHook(hook_input)
                exit_code = hook.run()
                assert exit_code == 1

                captured = capsys.readouterr()
                assert "Usage: python-claude toggle <check>" in captured.err

    def test_invalid_check_name(self, tmp_path: Path, capsys: Any) -> None:
        """Test that invalid check name returns error."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            with patch.object(sys, "argv", ["python-claude", "toggle", "invalid"]):
                hook = ToggleHook(hook_input)
                exit_code = hook.run()
                assert exit_code == 1

                captured = capsys.readouterr()
                assert "Unknown check: invalid" in captured.err
                assert "Available checks: pytest, mypy, ruff" in captured.err
