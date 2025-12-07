"""Tests for HookInput."""

import json
from io import StringIO
from unittest.mock import patch

from python_claude.hooks.base import HookInput


class TestHookInput:
    def test_from_empty_stdin(self) -> None:
        with patch("sys.stdin", StringIO("")):
            hook_input = HookInput.from_stdin()
            assert hook_input.session_id is None
            assert hook_input.tool_input == {}
            assert hook_input.file_path is None

    def test_from_json_stdin(self) -> None:
        data = {
            "session_id": "test-session-123",
            "tool_input": {"file_path": "/path/to/file.py"},
        }
        with patch("sys.stdin", StringIO(json.dumps(data))):
            hook_input = HookInput.from_stdin()
            assert hook_input.session_id == "test-session-123"
            assert hook_input.file_path == "/path/to/file.py"

    def test_null_session_id(self) -> None:
        data = {"session_id": "null", "tool_input": {}}
        with patch("sys.stdin", StringIO(json.dumps(data))):
            hook_input = HookInput.from_stdin()
            assert hook_input.session_id is None
