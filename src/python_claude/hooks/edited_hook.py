"""Collects edited Python files for deferred processing."""

from pathlib import Path

from python_claude.hooks.base import Hook, HookInput


class EditedHook(Hook):
    """Tracks edited Python files for later processing in Stop hook."""

    name = "edited"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        super().__init__(hook_input)

    @property
    def check_track_file(self) -> Path:
        """Get the path to the ruff check tracking file."""
        return self.log_dir / "edited-files.txt"

    @property
    def format_track_file(self) -> Path:
        """Get the path to the ruff format tracking file."""
        return self.log_dir / "format-files.txt"

    @property
    def mypy_track_file(self) -> Path:
        """Get the path to the mypy tracking file."""
        return self.log_dir / "mypy-files.txt"

    @property
    def pytest_track_file(self) -> Path:
        """Get the path to the pytest tracking file."""
        return self.log_dir / "pytest-files.txt"

    def _track_file(self, track_file: Path, file_path: str) -> None:
        """Add file to tracking file if not already present."""
        tracked_files: set[str] = set()
        if track_file.exists():
            tracked_files = set(track_file.read_text().strip().split("\n"))
            tracked_files.discard("")

        if file_path not in tracked_files:
            with open(track_file, "a") as f:
                f.write(f"{file_path}\n")

    def run(self) -> int:
        """Track the edited file if it's a Python file."""
        file_path = self.input.file_path
        if not file_path or not self.is_python_file(file_path):
            return 0

        self.log(file_path)

        # Track for all quality checks
        self._track_file(self.check_track_file, file_path)
        self._track_file(self.format_track_file, file_path)
        self._track_file(self.mypy_track_file, file_path)
        self._track_file(self.pytest_track_file, file_path)

        return 0
