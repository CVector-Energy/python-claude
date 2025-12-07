"""Session start hook for Claude Code."""

from python_claude.hooks.base import Hook, HookInput


class SessionStartHook(Hook):
    """Prints introductory message at session start."""

    name = "session-start"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        super().__init__(hook_input)

    def run(self) -> int:
        """Print the introductory message."""
        print(
            "As you edit files, Claude Code Hooks will automatically run "
            "ruff, mypy, and pytest. You don't need to run these commands manually."
        )
        return 0
