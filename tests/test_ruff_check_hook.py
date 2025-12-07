"""Tests for RuffCheckHook."""

import os
from pathlib import Path
from unittest.mock import patch

from python_claude.hooks.base import HookInput
from python_claude.hooks.ruff_check_hook import RuffCheckHook


class TestRuffCheckHook:
    def test_no_files_to_check(self, tmp_path: Path) -> None:
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = RuffCheckHook(hook_input)
            exit_code = hook.run()
            assert exit_code == 0
