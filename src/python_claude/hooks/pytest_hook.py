"""Pytest hook for Claude Code."""

import subprocess
import sys

from python_claude.hooks.base import Hook, HookInput


class PytestHook(Hook):
    """Runs pytest when stopping."""

    name = "pytest"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        super().__init__(hook_input)

    def run(self) -> int:
        """Run pytest."""
        result = subprocess.run(
            ["poetry", "run", "pytest"],
            cwd=self.project_dir,
            stdout=sys.stderr,
        )

        exit_code = result.returncode
        # Transform pytest exit code 1 (test failures) to exit code 2
        # for Claude Code to properly understand test failures
        if exit_code == 1:
            exit_code = 2
        self.log(f"exit {exit_code}")
        return exit_code
