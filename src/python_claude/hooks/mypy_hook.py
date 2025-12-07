"""Mypy hook for Claude Code."""

import subprocess
import sys

from python_claude.hooks.base import Hook, HookInput


class MypyHook(Hook):
    """Runs mypy type checking on edited Python files."""

    name = "mypy"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        super().__init__(hook_input)

    def run(self) -> int:
        """Run mypy on the edited file if it's a Python file."""
        file_path = self.input.file_path
        if not file_path or not self.is_python_file(file_path):
            return 0

        self.log(file_path)

        # mypy writes errors to stdout, but only stderr is fed back to Claude
        result = subprocess.run(
            ["poetry", "run", "mypy", file_path],
            cwd=self.project_dir,
            stdout=sys.stderr,  # Redirect stdout to stderr for Claude
        )

        exit_code = result.returncode
        self.log(f"exit {exit_code}")

        # Map mypy exit code 1 (type errors) to exit code 2 for Claude Code correction
        if exit_code == 1:
            return 2
        return exit_code
