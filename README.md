# python-claude

Python hooks for Claude Code for projects using:
- poetry
- ruff
- mypy
- pytest

The hooks ensure that the quality tools are automatically used:

Each time a file is edited:
- Record the file for later processing

When Claude is ready to stop:
- Reformat edited files with `ruff format`
- Repair lints of edited files with `ruff check --fix`
- Type-check edited files with `mypy`
- Run the tests with `pytest`

Note: We defer `ruff format` and `ruff check` until Claude stops to avoid changing files while Claude is working. Changing files during editing would spoil Claude's edits and force it to reread files.
## Installation

```bash
poetry add python-claude
```

## Usage

This package provides hooks that can be used with Claude Code's hook system.

### Available Commands

- `edited` - Tracks edited Python files for deferred processing (used in PostToolUse hook)
- `git status` - Shows git status
- `mypy` - Runs mypy type checking on edited files (used in Stop hook)
- `pytest` - Runs pytest
- `ruff check` - Runs ruff check on collected files with auto-fix (used in Stop hook)
- `ruff format` - Runs ruff format on collected files (used in Stop hook)
- `session start` - Prints introductory message about automatic hooks
- `toggle <check>` - Enable/disable a quality check (pytest, mypy, or ruff)

### Claude Code Settings

Add hooks to your Claude Code settings.json:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "poetry run python-claude session start"
          },
          {
            "type": "command",
            "command": "poetry run python-claude git status"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "poetry run python-claude ruff format"
          },
          {
            "type": "command",
            "command": "poetry run python-claude ruff check"
          },
          {
            "type": "command",
            "command": "poetry run python-claude mypy"
          },
          {
            "type": "command",
            "command": "poetry run python-claude pytest"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "poetry run python-claude edited"
          }
        ]
      }
    ]
  }
}
```

### Toggling Quality Checks

You can temporarily disable quality checks when needed. This is useful when:
- Tests are failing and you want to focus on type errors first
- You want to make multiple changes before running checks
- You're working on a feature that temporarily breaks tests

#### Using Slash Commands (Recommended)

The easiest way is to use the provided slash commands in Claude Code:

- `/pytest` - Toggle pytest on/off
- `/mypy` - Toggle mypy on/off
- `/ruff` - Toggle ruff (format + check) on/off

Each command will show whether the check is now enabled or disabled.

#### Using CLI Directly

You can also use the CLI directly:

```bash
poetry run python-claude toggle pytest
poetry run python-claude toggle mypy
poetry run python-claude toggle ruff
```

The toggle state persists across Claude Code sessions, stored in `.claude/quality-checks.json` (which is gitignored). All checks are enabled by default.

## Development

```bash
poetry install
poetry run pytest
poetry run ruff check
poetry run mypy src
```
