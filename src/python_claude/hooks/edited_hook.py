"""Collects edited Python files for deferred ruff check."""

from pathlib import Path

from python_claude.hooks.base import Hook, HookInput


class EditedHook(Hook):
    """Tracks edited Python files for later processing in Stop hook."""

    name = "edited"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        super().__init__(hook_input)

    @property
    def track_file(self) -> Path:
        """Get the path to the edited files tracking file."""
        return self.log_dir / "edited-files.txt"

    def run(self) -> int:
        """Track the edited file if it's a Python file."""
        file_path = self.input.file_path
        if not file_path or not self.is_python_file(file_path):
            return 0

        # Read existing tracked files
        tracked_files: set[str] = set()
        if self.track_file.exists():
            tracked_files = set(self.track_file.read_text().strip().split("\n"))
            tracked_files.discard("")

        # Add file if not already tracked
        if file_path not in tracked_files:
            with open(self.track_file, "a") as f:
                f.write(f"{file_path}\n")

        return 0
