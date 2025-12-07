"""Tests for EditedHook."""

import os
from pathlib import Path
from unittest.mock import patch

from python_claude.hooks.base import HookInput
from python_claude.hooks.edited_hook import EditedHook


class TestEditedHook:
    def test_tracks_python_file(self, tmp_path: Path) -> None:
        hook_input = HookInput(
            session_id=None,
            tool_input={"file_path": "/test/file.py"},
            raw={},
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = EditedHook(hook_input)
            exit_code = hook.run()
            assert exit_code == 0
            assert hook.track_file.exists()
            assert "/test/file.py" in hook.track_file.read_text()

    def test_ignores_non_python_file(self, tmp_path: Path) -> None:
        hook_input = HookInput(
            session_id=None,
            tool_input={"file_path": "/test/file.js"},
            raw={},
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = EditedHook(hook_input)
            exit_code = hook.run()
            assert exit_code == 0
            assert not hook.track_file.exists()

    def test_does_not_duplicate_files(self, tmp_path: Path) -> None:
        hook_input = HookInput(
            session_id=None,
            tool_input={"file_path": "/test/file.py"},
            raw={},
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook1 = EditedHook(hook_input)
            hook1.run()
            hook2 = EditedHook(hook_input)
            hook2.run()
            content = hook2.track_file.read_text()
            assert content.count("/test/file.py") == 1
