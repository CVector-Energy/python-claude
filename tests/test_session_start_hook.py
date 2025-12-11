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
            # Should only mention ruff in the enabled checks
            assert "will automatically run ruff after" in output["additionalContext"]
            # Should not mention pytest or mypy as enabled
            assert "mypy" not in output[
                "additionalContext"
            ] or "disabled" in output.get("systemMessage", "")
            assert "pytest" not in output[
                "additionalContext"
            ] or "disabled" in output.get("systemMessage", "")

            assert "systemMessage" in output
            assert "currently disabled: mypy, pytest" in output["systemMessage"]
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
            # When no checks are enabled, should show special message
            assert (
                "No quality checks are currently enabled" in output["additionalContext"]
            )
            assert "systemMessage" in output
            assert "currently disabled: ruff, mypy, pytest" in output["systemMessage"]

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
            # Should only mention mypy and pytest as enabled (with "and")
            assert (
                "will automatically run mypy and pytest after"
                in output["additionalContext"]
            )
            assert "systemMessage" in output
            assert "currently disabled: ruff" in output["systemMessage"]

    def test_shows_single_enabled_check(self, tmp_path: Path, capsys: Any) -> None:
        """Test message when only one check is enabled."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            # Disable mypy and pytest, leaving only ruff enabled
            state = QualityCheckState(tmp_path)
            state.disable("mypy")
            state.disable("pytest")

            hook = SessionStartHook(hook_input)
            exit_code = hook.run()
            assert exit_code == 0
            captured = capsys.readouterr()

            # Parse JSON output
            output = json.loads(captured.out)
            # Should only mention ruff (no "and")
            assert "will automatically run ruff after" in output["additionalContext"]
            # Should not have "and" when there's only one
            assert " and " not in output["additionalContext"]
            assert "systemMessage" in output
            assert "currently disabled: mypy, pytest" in output["systemMessage"]
