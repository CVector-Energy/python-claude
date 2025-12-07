"""Ruff check hook for Claude Code."""

import subprocess
from pathlib import Path

from python_claude.hooks.base import Hook, HookInput


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
        """Run ruff check on all tracked files."""
        # Check if tracking file exists and has content
        if not self.track_file.exists() or self.track_file.stat().st_size == 0:
            self.log("No edited Python files to check")
            return 0

        # Filter to only existing files
        files: list[str] = []
        for line in self.track_file.read_text().strip().split("\n"):
            file_path = line.strip()
            if file_path and Path(file_path).exists():
                files.append(file_path)

        if not files:
            self.log("No existing Python files to check")
            self.track_file.unlink(missing_ok=True)
            return 0

        self.log(f"Checking {len(files)} files: {' '.join(files)}")

        result = subprocess.run(
            ["poetry", "run", "ruff", "check", "--fix", *files],
            cwd=self.project_dir,
        )

        exit_code = result.returncode
        self.log(f"exit {exit_code}")

        if exit_code == 0:
            self.track_file.unlink(missing_ok=True)

        return exit_code
