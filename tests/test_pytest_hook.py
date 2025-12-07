"""Tests for PytestHook."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from python_claude.hooks.base import HookInput
from python_claude.hooks.pytest_hook import PytestHook


class TestPytestHook:
    def test_pytest_success(self, tmp_path: Path) -> None:
        """Test that exit code 0 is returned when pytest succeeds."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = PytestHook(hook_input)
            mock_result = MagicMock()
            mock_result.returncode = 0
            with patch("subprocess.run", return_value=mock_result):
                exit_code = hook.run()
                assert exit_code == 0

    def test_pytest_test_failures(self, tmp_path: Path) -> None:
        """Test that exit code 1 (test failures) is transformed to exit code 2."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = PytestHook(hook_input)
            mock_result = MagicMock()
            mock_result.returncode = 1
            with patch("subprocess.run", return_value=mock_result):
                exit_code = hook.run()
                assert exit_code == 2

    def test_pytest_other_error(self, tmp_path: Path) -> None:
        """Test that other exit codes are passed through unchanged."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = PytestHook(hook_input)
            mock_result = MagicMock()
            mock_result.returncode = 3
            with patch("subprocess.run", return_value=mock_result):
                exit_code = hook.run()
                assert exit_code == 3

    def test_pytest_no_tests_collected(self, tmp_path: Path) -> None:
        """Test that exit code 5 (no tests collected) is passed through."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = PytestHook(hook_input)
            mock_result = MagicMock()
            mock_result.returncode = 5
            with patch("subprocess.run", return_value=mock_result):
                exit_code = hook.run()
                assert exit_code == 5
