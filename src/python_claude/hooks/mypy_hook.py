"""Mypy hook for Claude Code."""

import subprocess
import sys
from pathlib import Path

from python_claude.hooks.base import (
    Hook,
    HookInput,
    checkout_dir,
    combine_exit_codes,
)
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

        if file_path:
            # File path provided - check if it's a Python file
            if not self.is_python_file(file_path):
                return 0
            checkout = checkout_dir(Path(file_path), self.project_dir)
            exit_code = self._run_mypy(file_path, checkout)
            # Map mypy exit code 1 (type errors) to exit code 2 for Claude Code correction
            return 2 if exit_code == 1 else exit_code

        # No file path (Stop hook) - check if any Python files were edited
        files = self.read_tracked_files(self.track_file)
        if not files:
            self.log("No edited Python files")
            return 0

        # Check the entire project in each checkout where files were edited
        exit_codes: list[int] = []
        remaining: list[str] = []
        for checkout, checkout_files in self.group_by_checkout(files).items():
            exit_code = self._run_mypy(".", checkout)
            if exit_code == 1:
                exit_code = 2
            if exit_code != 0:
                remaining.extend(checkout_files)
            exit_codes.append(exit_code)

        self.retain_tracked_files(self.track_file, remaining)
        return combine_exit_codes(exit_codes)

    def _run_mypy(self, mypy_target: str, checkout: Path) -> int:
        """Run mypy on the target in the given checkout and return its exit code."""
        self.log(f"{mypy_target} in {checkout}")

        # mypy writes errors to stdout, but only stderr is fed back to Claude
        result = subprocess.run(
            ["uv", "run", "mypy", mypy_target],
            cwd=checkout,
            stdout=sys.stderr,  # Redirect stdout to stderr for Claude
        )

        self.log(f"exit {result.returncode}")
        return result.returncode
