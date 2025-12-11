"""Ruff format hook for Claude Code."""

import subprocess
import sys
from pathlib import Path

from python_claude.hooks.base import Hook, HookInput
from python_claude.hooks.state import QualityCheckState


class RuffFormatHook(Hook):
    """Runs ruff format on all files collected during the session."""

    name = "ruff-format"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        super().__init__(hook_input)

    @property
    def track_file(self) -> Path:
        """Get the path to the format files tracking file."""
        return self.log_dir / "format-files.txt"

    def run(self) -> int:
        """Run ruff format on all tracked files if enabled."""
        state = QualityCheckState(self.project_dir)
        if not state.is_enabled("ruff"):
            self.log("Skipped (disabled)")
            return 0

        # Check if tracking file exists and has content
        if not self.track_file.exists() or self.track_file.stat().st_size == 0:
            self.log("No edited Python files to format")
            return 0

        files: list[str] = []
        for line in self.track_file.read_text().strip().split("\n"):
            file_path = line.strip()
            if file_path and Path(file_path).exists():
                files.append(file_path)

        if not files:
            self.log("No existing Python files to format")
            self.track_file.unlink(missing_ok=True)
            return 0

        self.log(f"Formatting {len(files)} files: {' '.join(files)}")

        result = subprocess.run(
            ["poetry", "run", "ruff", "format", *files],
            cwd=self.project_dir,
            stdout=sys.stderr,
        )

        exit_code = result.returncode
        self.log(f"exit {exit_code}")

        if exit_code == 0:
            self.track_file.unlink(missing_ok=True)

        return exit_code
