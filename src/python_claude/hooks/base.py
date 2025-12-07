"""Base hook functionality for Claude Code hooks."""

import json
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class HookInput:
    """Parsed input from Claude Code hook."""

    session_id: str | None
    tool_input: dict[str, Any]
    raw: dict[str, Any]

    @property
    def file_path(self) -> str | None:
        """Get the file path from tool input if present."""
        return self.tool_input.get("file_path")

    @classmethod
    def from_stdin(cls) -> "HookInput":
        """Read and parse hook input from stdin."""
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            return cls(session_id=None, tool_input={}, raw={})

        data = json.loads(raw_input)
        session_id = data.get("session_id")
        if session_id == "null":
            session_id = None
        tool_input = data.get("tool_input", {})
        return cls(session_id=session_id, tool_input=tool_input, raw=data)


class Hook(ABC):
    """Base class for Claude Code hooks."""

    name: str = "base"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        self.input = hook_input or HookInput.from_stdin()
        self._project_dir: Path | None = None
        self._log_dir: Path | None = None

    @property
    def project_dir(self) -> Path:
        """Get the Claude project directory."""
        if self._project_dir is None:
            env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
            if env_dir:
                self._project_dir = Path(env_dir)
            else:
                self._project_dir = Path.cwd()
        return self._project_dir

    @property
    def log_dir(self) -> Path:
        """Get the log directory for this session."""
        if self._log_dir is None:
            base_dir = self.project_dir / ".claude" / "debug"
            if self.input.session_id:
                self._log_dir = base_dir / "sessions" / self.input.session_id
            else:
                self._log_dir = base_dir
            self._log_dir.mkdir(parents=True, exist_ok=True)
        return self._log_dir

    @property
    def log_file(self) -> Path:
        """Get the log file path."""
        return self.log_dir / "hooks.log"

    def log(self, message: str) -> None:
        """Log a message to the hook log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{self.name}] {message}\n"
        with open(self.log_file, "a") as f:
            f.write(log_line)

    def is_python_file(self, file_path: str | None = None) -> bool:
        """Check if the given or input file path is a Python file."""
        path = file_path or self.input.file_path
        if path is None:
            return False
        return path.endswith(".py")

    @abstractmethod
    def run(self) -> int:
        """Run the hook and return exit code."""
        ...
