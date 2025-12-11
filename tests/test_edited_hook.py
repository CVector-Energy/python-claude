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
            # Check all tracking files
            assert hook.check_track_file.exists()
            assert "/test/file.py" in hook.check_track_file.read_text()
            assert hook.format_track_file.exists()
            assert "/test/file.py" in hook.format_track_file.read_text()
            assert hook.mypy_track_file.exists()
            assert "/test/file.py" in hook.mypy_track_file.read_text()
            assert hook.pytest_track_file.exists()
            assert "/test/file.py" in hook.pytest_track_file.read_text()

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
            assert not hook.check_track_file.exists()
            assert not hook.format_track_file.exists()
            assert not hook.mypy_track_file.exists()
            assert not hook.pytest_track_file.exists()

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
            # Check all tracking files don't have duplicates
            check_content = hook2.check_track_file.read_text()
            assert check_content.count("/test/file.py") == 1
            format_content = hook2.format_track_file.read_text()
            assert format_content.count("/test/file.py") == 1
            mypy_content = hook2.mypy_track_file.read_text()
            assert mypy_content.count("/test/file.py") == 1
            pytest_content = hook2.pytest_track_file.read_text()
            assert pytest_content.count("/test/file.py") == 1
