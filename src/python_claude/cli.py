"""Command-line interface for python-claude hooks."""

import sys

from python_claude.hooks import (
    EditedHook,
    GitStatusHook,
    MypyHook,
    PytestHook,
    RuffCheckHook,
    RuffFormatHook,
    SessionStartHook,
)
from python_claude.hooks.base import Hook

HOOKS: dict[str, type[Hook]] = {
    "edited": EditedHook,
    "git status": GitStatusHook,
    "mypy": MypyHook,
    "pytest": PytestHook,
    "ruff check": RuffCheckHook,
    "ruff format": RuffFormatHook,
    "session start": SessionStartHook,
}


def _print_available_hooks() -> None:
    """Print available hooks to stderr."""
    hooks = ", ".join(sorted(HOOKS.keys()))
    print(f"Available hooks: {hooks}", file=sys.stderr)


def main() -> None:
    """Main entry point for the CLI."""
    if len(sys.argv) < 2:
        print("Usage: python-claude <command>", file=sys.stderr)
        _print_available_hooks()
        sys.exit(1)

    # Try two-word command first, then single word
    if len(sys.argv) >= 3:
        hook_name = f"{sys.argv[1]} {sys.argv[2]}"
        if hook_name not in HOOKS:
            hook_name = sys.argv[1]
    else:
        hook_name = sys.argv[1]

    if hook_name not in HOOKS:
        print(f"Unknown command: {hook_name}", file=sys.stderr)
        _print_available_hooks()
        sys.exit(1)

    hook_class = HOOKS[hook_name]
    hook = hook_class()
    exit_code = hook.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
