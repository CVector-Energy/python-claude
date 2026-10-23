"""Ruff check hook for Claude Code."""

import subprocess
import sys
from pathlib import Path

from python_claude.hooks.base import Hook, HookInput, combine_exit_codes
from python_claude.hooks.state import QualityCheckState


class RuffCheckHook(Hook):
    """Runs ruff check on all files collected during the session."""

    name = "ruff-check"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        super().__init__(hook_input)

    @property
    def track_file(self) -> Path:
        """Get the path to the edited files tracking file."""
        return self.log_dir / "edited-files.txt"

    def run(self) -> int:
        """Run ruff check on all tracked files if enabled."""
        state = QualityCheckState(self.project_dir)
        if not state.is_enabled("ruff"):
            self.log("Skipped (disabled)")
            return 0

        # Check if tracking file exists and has content
        tracked = self.read_tracked_files(self.track_file)
        if not tracked:
            self.log("No edited Python files to check")
            return 0

        files = [file_path for file_path in tracked if Path(file_path).exists()]
        if not files:
            self.log("No existing Python files to check")
            self.track_file.unlink(missing_ok=True)
            return 0

        exit_codes: list[int] = []
        remaining: list[str] = []
        for checkout, checkout_files in self.group_by_checkout(files).items():
            self.log(
                f"Checking {len(checkout_files)} files in {checkout}: {' '.join(checkout_files)}"
            )

            result = subprocess.run(
                ["uv", "run", "ruff", "check", "--fix", *checkout_files],
                cwd=checkout,
                stdout=sys.stderr,
            )

            exit_code = result.returncode
            self.log(f"exit {exit_code}")

            # ruff check exit code 1 indicates a lint error that was not automatically fixed; return status 2 to signal claude to consider fixing it
            if exit_code == 1:
                exit_code = 2

            if exit_code != 0:
                remaining.extend(checkout_files)
            exit_codes.append(exit_code)

        self.retain_tracked_files(self.track_file, remaining)
        return combine_exit_codes(exit_codes)
