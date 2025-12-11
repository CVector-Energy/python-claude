"""State management for quality check toggles."""

import json
import os
from pathlib import Path
from typing import Literal

QualityCheck = Literal["pytest", "mypy", "ruff"]


class QualityCheckState:
    """Manages enabled/disabled state for quality checks."""

    def __init__(self, project_dir: Path | None = None) -> None:
        if project_dir is None:
            env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
            if env_dir:
                project_dir = Path(env_dir)
            else:
                project_dir = Path.cwd()
        self.project_dir = project_dir
        self.state_file = project_dir / ".claude" / "quality-checks.json"

    def _load_state(self) -> dict[str, bool]:
        """Load state from file, return default if file doesn't exist."""
        if not self.state_file.exists():
            # Default: all checks enabled
            return {"pytest": True, "mypy": True, "ruff": True}

        try:
            with open(self.state_file) as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                return {"pytest": True, "mypy": True, "ruff": True}
        except (json.JSONDecodeError, OSError):
            return {"pytest": True, "mypy": True, "ruff": True}

    def _save_state(self, state: dict[str, bool]) -> None:
        """Save state to file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def is_enabled(self, check: QualityCheck) -> bool:
        """Check if a quality check is enabled."""
        state = self._load_state()
        return state.get(check, True)

    def toggle(self, check: QualityCheck) -> bool:
        """Toggle a quality check and return new state."""
        state = self._load_state()
        new_value = not state.get(check, True)
        state[check] = new_value
        self._save_state(state)
        return new_value

    def enable(self, check: QualityCheck) -> None:
        """Enable a quality check."""
        state = self._load_state()
        state[check] = True
        self._save_state(state)

    def disable(self, check: QualityCheck) -> None:
        """Disable a quality check."""
        state = self._load_state()
        state[check] = False
        self._save_state(state)
