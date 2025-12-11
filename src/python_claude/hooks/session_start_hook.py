"""Session start hook for Claude Code."""

import json

from python_claude.hooks.base import Hook, HookInput
from python_claude.hooks.state import QualityCheckState


class SessionStartHook(Hook):
    """Prints introductory message at session start."""

    name = "session-start"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        super().__init__(hook_input)

    def run(self) -> int:
        """Print the introductory message."""
        state = QualityCheckState(self.project_dir)

        # Check which quality checks are disabled
        disabled_checks = []
        if not state.is_enabled("pytest"):
            disabled_checks.append("pytest")
        if not state.is_enabled("mypy"):
            disabled_checks.append("mypy")
        if not state.is_enabled("ruff"):
            disabled_checks.append("ruff")

        additional_context = (
            "As you edit files, Claude Code Hooks will automatically run "
            "ruff, mypy, and pytest after you edit a file. You don't need "
            "to run these commands manually. You can run these before making "
            "an edit using:\n"
            "- poetry run ruff format .\n"
            "- poetry run ruff check .\n"
            "- poetry run mypy .\n"
            "- poetry run pytest"
        )

        output = {"additionalContext": additional_context}

        if disabled_checks:
            checks_str = ", ".join(disabled_checks)
            system_message = (
                f"Note: The following quality checks are currently disabled: {checks_str}\n"
                f"Use /pytest, /mypy, or /ruff to toggle them back on."
            )
            output["systemMessage"] = system_message

        print(json.dumps(output))
        return 0
