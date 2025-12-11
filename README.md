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

### Option 1: Plugin Installation (Recommended)

Install as a Claude Code plugin for automatic hook configuration:

1. First, add this package to your project:
   ```bash
   poetry add python-claude
   ```

2. Install as a Claude Code plugin:
   ```bash
   claude plugin install /path/to/python-claude
   ```

3. Restart Claude Code to activate the hooks

The plugin automatically configures all necessary hooks - no manual settings.json configuration needed!

### Option 2: Manual Installation

If you prefer manual configuration:

1. Add to your project:
   ```bash
   poetry add python-claude
   ```

2. Add hooks to your Claude Code settings.json:
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

## Available Commands

- `edited` - Tracks edited Python files for deferred processing (used in PostToolUse hook)
- `git status` - Shows git status
- `mypy` - Runs mypy type checking on edited files (used in Stop hook)
- `pytest` - Runs pytest
- `ruff check` - Runs ruff check on collected files with auto-fix (used in Stop hook)
- `ruff format` - Runs ruff format on collected files (used in Stop hook)
- `session start` - Prints introductory message about automatic hooks

## Development

```bash
poetry install
poetry run pytest
poetry run ruff check
poetry run mypy src
```
