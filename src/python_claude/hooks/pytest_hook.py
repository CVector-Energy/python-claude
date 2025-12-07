"""Pytest hook for Claude Code."""

import subprocess

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
        )

        exit_code = result.returncode
        self.log(f"exit {exit_code}")
        return exit_code
