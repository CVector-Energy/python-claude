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


def _git_root(path: Path) -> Path | None:
    """Find the nearest directory containing a .git entry (a directory in a main checkout, a file in a worktree)."""
    for candidate in [path, *path.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def checkout_dir(path: Path, project_dir: Path) -> Path:
    """Find the directory that plays the role of project_dir in the checkout containing path.

    Claude Code may edit files in a git worktree rather than in the checkout where the session started (CLAUDE_PROJECT_DIR). Quality checks must run in the worktree, at the same relative location as the project directory within its repository.
    """
    root = _git_root(path)
    if root is None:
        return project_dir
    project_root = _git_root(project_dir)
    if project_root is not None:
        candidate = root / project_dir.relative_to(project_root)
        if path.is_relative_to(candidate):
            return candidate
    return root


def combine_exit_codes(exit_codes: list[int]) -> int:
    """Combine exit codes from several checkouts, preferring 2 so that Claude is asked to fix any failure it can act on."""
    if 2 in exit_codes:
        return 2
    return next((code for code in exit_codes if code != 0), 0)


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
    def working_dir(self) -> Path:
        """Get the checkout containing the session's current working directory."""
        cwd = self.input.raw.get("cwd")
        if not cwd:
            return self.project_dir
        return checkout_dir(Path(cwd), self.project_dir)

    def group_by_checkout(self, files: list[str]) -> dict[Path, list[str]]:
        """Group edited files by the checkout that contains them."""
        groups: dict[Path, list[str]] = {}
        for file_path in files:
            checkout = checkout_dir(Path(file_path), self.project_dir)
            groups.setdefault(checkout, []).append(file_path)
        return groups

    def read_tracked_files(self, track_file: Path) -> list[str]:
        """Read the files recorded in a tracking file."""
        if not track_file.exists():
            return []
        return [
            line.strip() for line in track_file.read_text().split("\n") if line.strip()
        ]

    def retain_tracked_files(self, track_file: Path, files: list[str]) -> None:
        """Replace the contents of a tracking file, removing it when no files remain."""
        if files:
            track_file.write_text("".join(f"{file_path}\n" for file_path in files))
        else:
            track_file.unlink(missing_ok=True)

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
