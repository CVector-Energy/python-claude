"""Toggle hook for enabling/disabling quality checks."""

import sys
from typing import cast

from python_claude.hooks.base import Hook
from python_claude.hooks.state import QualityCheck, QualityCheckState


class ToggleHook(Hook):
    """Toggles quality check state."""

    name = "toggle"

    def run(self) -> int:
        """Toggle a quality check and print the new state."""
        # Get the check name from command line args
        # sys.argv will be: ['python-claude', 'toggle', 'pytest']
        if len(sys.argv) < 3:
            print("Usage: python-claude toggle <check>", file=sys.stderr)
            print("Available checks: pytest, mypy, ruff", file=sys.stderr)
            return 1

        check = sys.argv[2]
        if check not in ("pytest", "mypy", "ruff"):
            print(f"Unknown check: {check}", file=sys.stderr)
            print("Available checks: pytest, mypy, ruff", file=sys.stderr)
            return 1

        state = QualityCheckState(self.project_dir)
        # Cast is safe because we validated check is one of the three valid values
        new_state = state.toggle(cast(QualityCheck, check))
        status = "enabled" if new_state else "disabled"
        print(f"{check.capitalize()} is now {status}")
        return 0
