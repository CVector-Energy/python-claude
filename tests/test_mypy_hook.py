"""Tests for MypyHook."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from python_claude.hooks.base import HookInput
from python_claude.hooks.mypy_hook import MypyHook


class TestMypyHook:
    def test_python_file_success(self, tmp_path: Path) -> None:
        """Test mypy succeeds on a Python file."""
        hook_input = HookInput(
            session_id=None,
            tool_input={"file_path": "/path/to/file.py"},
            raw={},
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = MypyHook(hook_input)
            mock_result = MagicMock()
            mock_result.returncode = 0
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                exit_code = hook.run()
                assert exit_code == 0
                mock_run.assert_called_once()
                # Verify it ran mypy on the specific file
                call_args = mock_run.call_args
                assert call_args[0][0] == ["poetry", "run", "mypy", "/path/to/file.py"]

    def test_python_file_type_errors(self, tmp_path: Path) -> None:
        """Test mypy type errors (exit 1) are transformed to exit code 2."""
        hook_input = HookInput(
            session_id=None,
            tool_input={"file_path": "/path/to/file.py"},
            raw={},
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = MypyHook(hook_input)
            mock_result = MagicMock()
            mock_result.returncode = 1
            with patch("subprocess.run", return_value=mock_result):
                exit_code = hook.run()
                assert exit_code == 2

    def test_python_file_other_error(self, tmp_path: Path) -> None:
        """Test other mypy errors are passed through unchanged."""
        hook_input = HookInput(
            session_id=None,
            tool_input={"file_path": "/path/to/file.py"},
            raw={},
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = MypyHook(hook_input)
            mock_result = MagicMock()
            mock_result.returncode = 3
            with patch("subprocess.run", return_value=mock_result):
                exit_code = hook.run()
                assert exit_code == 3

    def test_non_python_file(self, tmp_path: Path) -> None:
        """Test non-Python files are skipped."""
        hook_input = HookInput(
            session_id=None,
            tool_input={"file_path": "/path/to/file.txt"},
            raw={},
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = MypyHook(hook_input)
            with patch("subprocess.run") as mock_run:
                exit_code = hook.run()
                assert exit_code == 0
                # Verify subprocess was not called
                mock_run.assert_not_called()

    def test_stop_hook_no_file_path_success(self, tmp_path: Path) -> None:
        """Test Stop hook (no file_path) runs mypy on entire project."""
        hook_input = HookInput(
            session_id="abc123",
            tool_input={},
            raw={
                "session_id": "abc123",
                "hook_event_name": "Stop",
                "stop_hook_active": True,
            },
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = MypyHook(hook_input)
            # Create tracking file with edited files
            hook.track_file.parent.mkdir(parents=True, exist_ok=True)
            hook.track_file.write_text("/path/to/file.py\n")

            mock_result = MagicMock()
            mock_result.returncode = 0
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                exit_code = hook.run()
                assert exit_code == 0
                mock_run.assert_called_once()
                # Verify it ran mypy on current directory
                call_args = mock_run.call_args
                assert call_args[0][0] == ["poetry", "run", "mypy", "."]
                # Verify tracking file was cleaned up
                assert not hook.track_file.exists()

    def test_stop_hook_type_errors(self, tmp_path: Path) -> None:
        """Test Stop hook with type errors (exit 1) transforms to exit code 2."""
        hook_input = HookInput(
            session_id="abc123",
            tool_input={},
            raw={
                "session_id": "abc123",
                "hook_event_name": "Stop",
                "stop_hook_active": True,
            },
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = MypyHook(hook_input)
            mock_result = MagicMock()
            mock_result.returncode = 1
            with patch("subprocess.run", return_value=mock_result):
                exit_code = hook.run()
                assert exit_code == 2

    def test_empty_file_path_runs_full_check(self, tmp_path: Path) -> None:
        """Test empty string file_path is treated as Stop hook."""
        hook_input = HookInput(
            session_id=None,
            tool_input={"file_path": ""},
            raw={},
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            hook = MypyHook(hook_input)
            mock_result = MagicMock()
            mock_result.returncode = 0
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                exit_code = hook.run()
                assert exit_code == 0
                # Verify it ran mypy on current directory
                call_args = mock_run.call_args
                assert call_args[0][0] == ["poetry", "run", "mypy", "."]
