"""Tests for RuffCheckHook."""

import os
from pathlib import Path
from unittest.mock import patch

from python_claude.hooks.base import HookInput
from python_claude.hooks.ruff_check_hook import RuffCheckHook
from python_claude.hooks.state import QualityCheckState


class TestRuffCheckHook:
    def test_no_files_to_check(self, tmp_path: Path) -> None:
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = RuffCheckHook(hook_input)
            exit_code = hook.run()
            assert exit_code == 0

    def test_ruff_skipped_when_disabled(self, tmp_path: Path) -> None:
        """Test that ruff is skipped when disabled in state."""
        hook_input = HookInput(session_id=None, tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            # Disable ruff
            state = QualityCheckState(tmp_path)
            state.disable("ruff")

            hook = RuffCheckHook(hook_input)
            # Create tracking file with edited files
            hook.track_file.parent.mkdir(parents=True, exist_ok=True)
            hook.track_file.write_text("/path/to/file.py\n")

            with patch("subprocess.run") as mock_run:
                exit_code = hook.run()
                assert exit_code == 0
                # Verify subprocess was not called
                mock_run.assert_not_called()
