"""Ruff format hook for Claude Code."""

import subprocess
import sys

from python_claude.hooks.base import Hook, HookInput


class RuffFormatHook(Hook):
    """Runs ruff format on edited Python files."""

    name = "ruff-format"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        super().__init__(hook_input)

    def run(self) -> int:
        """Run ruff format on the edited file if it's a Python file."""
        file_path = self.input.file_path
        if not file_path or not self.is_python_file(file_path):
            return 0

        self.log(file_path)

        result = subprocess.run(
            ["poetry", "run", "ruff", "format", file_path],
            cwd=self.project_dir,
            stdout=sys.stderr,
        )

        exit_code = result.returncode
        self.log(f"exit {exit_code}")
        return exit_code
