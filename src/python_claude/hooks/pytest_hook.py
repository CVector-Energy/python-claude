"""Pytest hook for Claude Code."""

import subprocess
import sys
from pathlib import Path

from python_claude.hooks.base import Hook, HookInput, combine_exit_codes
from python_claude.hooks.state import QualityCheckState


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
        """Run pytest if enabled and files were edited."""
        state = QualityCheckState(self.project_dir)
        self.log(f"state:{state}")
        if not state.is_enabled("pytest"):
            self.log("Skipped (disabled)")
            return 0

        self.log(f"{self.track_file}")

        # Check if any Python files were edited
        files = self.read_tracked_files(self.track_file)
        if not files:
            self.log("No edited Python files")
            return 0

        exit_codes: list[int] = []
        remaining: list[str] = []
        for checkout, checkout_files in self.group_by_checkout(files).items():
            self.log(f"Running pytest in {checkout}")

            result = subprocess.run(
                ["uv", "run", "pytest"],
                cwd=checkout,
                stdout=sys.stderr,
            )

            exit_code = result.returncode
            # Transform pytest exit code 1 (test failures) to exit code 2
            # for Claude Code to properly understand test failures
            if exit_code == 1:
                exit_code = 2
            self.log(f"exit {exit_code}")

            # Keep tracking files of checkouts that still fail
            if exit_code != 0:
                remaining.extend(checkout_files)
            exit_codes.append(exit_code)

        self.retain_tracked_files(self.track_file, remaining)
        return combine_exit_codes(exit_codes)
