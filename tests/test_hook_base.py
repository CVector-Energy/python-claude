"""Tests for base Hook functionality."""

import os
from pathlib import Path
from unittest.mock import patch

from python_claude.hooks.base import HookInput
from python_claude.hooks.edited_hook import EditedHook


class TestHookBase:
    def test_is_python_file(self, tmp_path: Path) -> None:
        hook_input = HookInput(
            session_id=None, tool_input={"file_path": "/test/file.py"}, raw={}
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = EditedHook(hook_input)
            assert hook.is_python_file() is True

    def test_is_not_python_file(self, tmp_path: Path) -> None:
        hook_input = HookInput(
            session_id=None, tool_input={"file_path": "/test/file.js"}, raw={}
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = EditedHook(hook_input)
            assert hook.is_python_file() is False

    def test_log_dir_with_session(self, tmp_path: Path) -> None:
        hook_input = HookInput(session_id="session-abc", tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = EditedHook(hook_input)
            expected = tmp_path / ".claude" / "debug" / "sessions" / "session-abc"
            assert hook.log_dir == expected

    def test_log_dir_without_session(self, tmp_path: Path) -> None:
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = EditedHook(hook_input)
            expected = tmp_path / ".claude" / "debug"
            assert hook.log_dir == expected
