"""Tests for SessionStartHook."""

import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

from python_claude.hooks.base import HookInput
from python_claude.hooks.session_start_hook import SessionStartHook
from python_claude.hooks.state import QualityCheckState


class TestSessionStartHook:
    def test_prints_intro_message(self, tmp_path: Path, capsys: Any) -> None:
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = SessionStartHook(hook_input)
            exit_code = hook.run()
            assert exit_code == 0
            captured = capsys.readouterr()

            # Parse JSON output
            output = json.loads(captured.out)
            assert (
                "Claude Code Hooks will automatically run"
                in output["additionalContext"]
            )
            assert "ruff, mypy, and pytest" in output["additionalContext"]
            # When all checks are enabled, no systemMessage should be present
            assert "systemMessage" not in output

    def test_shows_disabled_checks(self, tmp_path: Path, capsys: Any) -> None:
        """Test that disabled checks are reported in the session start message."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            # Disable pytest and mypy
            state = QualityCheckState(tmp_path)
            state.disable("pytest")
            state.disable("mypy")

            hook = SessionStartHook(hook_input)
            exit_code = hook.run()
            assert exit_code == 0
            captured = capsys.readouterr()

            # Parse JSON output
            output = json.loads(captured.out)
            assert "systemMessage" in output
            assert "currently disabled: pytest, mypy" in output["systemMessage"]
            assert (
                "Use /pytest, /mypy, or /ruff to toggle them back on"
                in output["systemMessage"]
            )

    def test_shows_all_disabled_checks(self, tmp_path: Path, capsys: Any) -> None:
        """Test message when all checks are disabled."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            # Disable all checks
            state = QualityCheckState(tmp_path)
            state.disable("pytest")
            state.disable("mypy")
            state.disable("ruff")

            hook = SessionStartHook(hook_input)
            exit_code = hook.run()
            assert exit_code == 0
            captured = capsys.readouterr()

            # Parse JSON output
            output = json.loads(captured.out)
            assert "systemMessage" in output
            assert "currently disabled: pytest, mypy, ruff" in output["systemMessage"]

    def test_shows_single_disabled_check(self, tmp_path: Path, capsys: Any) -> None:
        """Test message when only one check is disabled."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            # Disable only ruff
            state = QualityCheckState(tmp_path)
            state.disable("ruff")

            hook = SessionStartHook(hook_input)
            exit_code = hook.run()
            assert exit_code == 0
            captured = capsys.readouterr()

            # Parse JSON output
            output = json.loads(captured.out)
            assert "systemMessage" in output
            assert "currently disabled: ruff" in output["systemMessage"]
