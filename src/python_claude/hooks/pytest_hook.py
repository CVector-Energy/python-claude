"""Pytest hook for Claude Code."""

import subprocess
import sys
from pathlib import Path

from python_claude.hooks.base import Hook, HookInput


class PytestHook(Hook):
    """Runs pytest when stopping."""

    name = "pytest"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        super().__init__(hook_input)

    @property
    def track_file(self) -> Path:
        """Get the path to the edited files tracking file."""
        return self.log_dir / "pytest-files.txt"

    def run(self) -> int:
        """Run pytest."""
        result = subprocess.run(
            ["poetry", "run", "pytest"],
            cwd=self.project_dir,
            stdout=sys.stderr,
        )

        exit_code = result.returncode
        self.log(f"exit {exit_code}")

        # Clean up tracking file on success
        if exit_code == 0:
            self.track_file.unlink(missing_ok=True)

        # Transform pytest exit code 1 (test failures) to exit code 2
        # for Claude Code to properly understand test failures
        if exit_code == 1:
            return 2
        return exit_code
