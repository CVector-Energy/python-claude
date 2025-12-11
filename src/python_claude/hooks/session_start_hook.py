"""Session start hook for Claude Code."""

import json
from typing import cast

from python_claude.hooks.base import Hook, HookInput
from python_claude.hooks.state import QualityCheck, QualityCheckState


class SessionStartHook(Hook):
    """Prints introductory message at session start."""

    name = "session-start"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        super().__init__(hook_input)

    def run(self) -> int:
        """Print the introductory message."""
        state = QualityCheckState(self.project_dir)

        # Check which quality checks are enabled and disabled
        enabled_checks = []
        disabled_checks = []

        for check_name in ["ruff", "mypy", "pytest"]:
            check = cast(QualityCheck, check_name)
            if state.is_enabled(check):
                enabled_checks.append(check_name)
            else:
                disabled_checks.append(check_name)

        # Build the message based on enabled checks
        if enabled_checks:
            # Format list with proper grammar: "a, b, and c"
            if len(enabled_checks) == 1:
                checks_list = enabled_checks[0]
            elif len(enabled_checks) == 2:
                checks_list = f"{enabled_checks[0]} and {enabled_checks[1]}"
            else:
                checks_list = (
                    ", ".join(enabled_checks[:-1]) + f", and {enabled_checks[-1]}"
                )

            additional_context = (
                f"As you edit files, Claude Code Hooks will automatically run "
                f"{checks_list} after you edit a file. You don't need "
                f"to run these commands manually. You can run these before making "
                f"an edit using:\n"
                f"- poetry run ruff format .\n"
                f"- poetry run ruff check .\n"
                f"- poetry run mypy .\n"
                f"- poetry run pytest"
            )
        else:
            additional_context = (
                "No quality checks are currently enabled. "
                "Use /pytest, /mypy, or /ruff to enable checks."
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
