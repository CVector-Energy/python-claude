"""Git status hook for Claude Code."""

import subprocess

from python_claude.hooks.base import Hook, HookInput


class GitStatusHook(Hook):
    """Shows git status."""

    name = "git-status"

    def __init__(self, hook_input: HookInput | None = None) -> None:
        super().__init__(hook_input)

    def run(self) -> int:
        """Run git status and output the result."""
        print("# git status")
        result = subprocess.run(
            ["git", "status"],
            cwd=self.project_dir,
        )
        return result.returncode
