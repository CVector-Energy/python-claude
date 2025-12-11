"""Mypy hook for Claude Code."""

import subprocess
import sys
from pathlib import Path

from python_claude.hooks.base import Hook, HookInput
from python_claude.hooks.state import QualityCheckState


class MypyHook(Hook):
    """Runs mypy type checking on edited Python files."""

    name = "mypy"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        super().__init__(hook_input)

    @property
    def track_file(self) -> Path:
        """Get the path to the edited files tracking file."""
        return self.log_dir / "mypy-files.txt"

    def run(self) -> int:
        """Run mypy on the edited file or entire project if enabled.

        If file_path is provided and is a Python file, run mypy on that file.
        If no file_path is provided (e.g., Stop hook), run mypy on entire project
        only if files were edited.
        """
        state = QualityCheckState(self.project_dir)
        if not state.is_enabled("mypy"):
            self.log("Skipped (disabled)")
            return 0

        file_path = self.input.file_path

        # Determine what to type check
        if file_path:
            # File path provided - check if it's a Python file
            if not self.is_python_file(file_path):
                return 0
            mypy_target = file_path
        else:
            # No file path (Stop hook) - check if any Python files were edited
            if not self.track_file.exists() or self.track_file.stat().st_size == 0:
                self.log("No edited Python files")
                return 0
            # Check entire project
            mypy_target = "."

        self.log(mypy_target)

        # mypy writes errors to stdout, but only stderr is fed back to Claude
        result = subprocess.run(
            ["poetry", "run", "mypy", mypy_target],
            cwd=self.project_dir,
            stdout=sys.stderr,  # Redirect stdout to stderr for Claude
        )

        exit_code = result.returncode
        self.log(f"exit {exit_code}")

        # Clean up tracking file on success (only for Stop hook)
        if exit_code == 0 and not file_path:
            self.track_file.unlink(missing_ok=True)

        # Map mypy exit code 1 (type errors) to exit code 2 for Claude Code correction
        if exit_code == 1:
            return 2
        return exit_code
