"""Tests for SessionStartHook."""

import os
from pathlib import Path
from unittest.mock import patch

from python_claude.hooks.base import HookInput
from python_claude.hooks.session_start_hook import SessionStartHook


class TestSessionStartHook:
    def test_prints_intro_message(self, tmp_path: Path, capsys: object) -> None:
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = SessionStartHook(hook_input)
            exit_code = hook.run()
            assert exit_code == 0
            captured = capsys.readouterr()  # type: ignore[attr-defined]
            assert "Claude Code Hooks will automatically run" in captured.out
            assert "ruff, mypy, and pytest" in captured.out
