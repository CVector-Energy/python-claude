# python-claude

Python hooks for Claude Code for projects using:
- poetry
- ruff
- mypy
- pytest

The hooks ensure that the quality tools are automatically used:

Each time a file is edited:
- Reformat with `ruff format`
- Type-check with `mypy`
- Record the file

When claude is ready to stop:
- Repair lints of edited files with `ruff check --fix`. (We do not do this while editing files, becaue it Claude tends to add `import` statements in a dedicated edit, ahead of adding the code that uses it. In this case, `ruff check --fix` would erase the "unused" import.)
- Run the tests with `pytest`.

## Installation

```bash
poetry add python-claude
```

## Usage

This package provides hooks that can be used with Claude Code's hook system.

### Available Commands

- `edited` - Tracks edited Python files for deferred processing
- `git status` - Shows git status
- `mypy` - Runs mypy type checking on edited files
- `pytest` - Runs pytest
- `ruff check` - Runs ruff check on collected files with auto-fix
- `ruff format` - Runs ruff format on edited files
- `session start` - Prints introductory message about automatic hooks

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
            "command": "poetry run python-claude ruff check"
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
            "command": "poetry run python-claude ruff format"
          },
          {
            "type": "command",
            "command": "poetry run python-claude edited"
          },
          {
            "type": "command",
            "command": "poetry run python-claude mypy"
          }
        ]
      }
    ]
  }
}
```

## Development

```bash
poetry install
poetry run pytest
poetry run ruff check
poetry run mypy src
```
