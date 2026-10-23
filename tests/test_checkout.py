"""Tests for running quality checks in the checkout where files were edited."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from python_claude.hooks.base import HookInput, checkout_dir
from python_claude.hooks.git_status_hook import GitStatusHook
from python_claude.hooks.mypy_hook import MypyHook
from python_claude.hooks.pytest_hook import PytestHook
from python_claude.hooks.ruff_check_hook import RuffCheckHook
from python_claude.hooks.ruff_format_hook import RuffFormatHook


def make_repo(tmp_path: Path) -> tuple[Path, Path]:
    """Create a main checkout with a worktree nested under .claude/worktrees, as the Claude Code desktop app does."""
    main = tmp_path / "repo"
    (main / ".git").mkdir(parents=True)
    (main / "src").mkdir()
    (main / "src" / "main_file.py").write_text("")
    worktree = main / ".claude" / "worktrees" / "feature"
    (worktree / "src").mkdir(parents=True)
    (worktree / ".git").write_text(f"gitdir: {main}/.git/worktrees/feature\n")
    (worktree / "src" / "wt_file.py").write_text("")
    return main, worktree


def ok() -> MagicMock:
    result = MagicMock()
    result.returncode = 0
    return result


class TestCheckoutDir:
    def test_file_in_main_checkout(self, tmp_path: Path) -> None:
        main, _ = make_repo(tmp_path)
        assert checkout_dir(main / "src" / "main_file.py", main) == main

    def test_file_in_nested_worktree(self, tmp_path: Path) -> None:
        main, worktree = make_repo(tmp_path)
        assert checkout_dir(worktree / "src" / "wt_file.py", main) == worktree

    def test_file_in_new_directory(self, tmp_path: Path) -> None:
        main, worktree = make_repo(tmp_path)
        assert checkout_dir(worktree / "new" / "pkg" / "x.py", main) == worktree

    def test_project_in_subdirectory_of_repo(self, tmp_path: Path) -> None:
        main, worktree = make_repo(tmp_path)
        (main / "backend").mkdir()
        (worktree / "backend").mkdir()
        project = main / "backend"
        assert checkout_dir(worktree / "backend" / "x.py", project) == (
            worktree / "backend"
        )

    def test_file_outside_any_repository(self, tmp_path: Path) -> None:
        main, _ = make_repo(tmp_path)
        assert checkout_dir(Path("/path/to/file.py"), main) == main


class TestStopHooksUseEditedCheckout:
    def test_pytest_runs_only_in_worktree(self, tmp_path: Path) -> None:
        main, worktree = make_repo(tmp_path)
        hook_input = HookInput(session_id="s", tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(main)}):
            hook = PytestHook(hook_input)
            hook.track_file.write_text(f"{worktree}/src/wt_file.py\n")
            with patch("subprocess.run", return_value=ok()) as mock_run:
                assert hook.run() == 0
            assert [c.kwargs["cwd"] for c in mock_run.call_args_list] == [worktree]
            assert not hook.track_file.exists()

    def test_pytest_failure_keeps_only_failing_checkout_tracked(
        self, tmp_path: Path
    ) -> None:
        main, worktree = make_repo(tmp_path)
        hook_input = HookInput(session_id="s", tool_input={}, raw={})

        def run(args: list[str], cwd: Path, **kwargs: object) -> MagicMock:
            result = MagicMock()
            result.returncode = 1 if cwd == worktree else 0
            return result

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(main)}):
            hook = PytestHook(hook_input)
            hook.track_file.write_text(
                f"{main}/src/main_file.py\n{worktree}/src/wt_file.py\n"
            )
            with patch("subprocess.run", side_effect=run) as mock_run:
                assert hook.run() == 2
            assert {c.kwargs["cwd"] for c in mock_run.call_args_list} == {
                main,
                worktree,
            }
            assert hook.track_file.read_text() == f"{worktree}/src/wt_file.py\n"

    def test_mypy_stop_runs_in_worktree(self, tmp_path: Path) -> None:
        main, worktree = make_repo(tmp_path)
        hook_input = HookInput(session_id="s", tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(main)}):
            hook = MypyHook(hook_input)
            hook.track_file.write_text(f"{worktree}/src/wt_file.py\n")
            with patch("subprocess.run", return_value=ok()) as mock_run:
                assert hook.run() == 0
            mock_run.assert_called_once()
            assert mock_run.call_args.args[0] == ["uv", "run", "mypy", "."]
            assert mock_run.call_args.kwargs["cwd"] == worktree

    def test_mypy_single_file_runs_in_its_checkout(self, tmp_path: Path) -> None:
        main, worktree = make_repo(tmp_path)
        file_path = f"{worktree}/src/wt_file.py"
        hook_input = HookInput(
            session_id="s", tool_input={"file_path": file_path}, raw={}
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(main)}):
            hook = MypyHook(hook_input)
            with patch("subprocess.run", return_value=ok()) as mock_run:
                assert hook.run() == 0
            assert mock_run.call_args.kwargs["cwd"] == worktree

    def test_ruff_format_groups_files_by_checkout(self, tmp_path: Path) -> None:
        main, worktree = make_repo(tmp_path)
        main_file = f"{main}/src/main_file.py"
        wt_file = f"{worktree}/src/wt_file.py"
        hook_input = HookInput(session_id="s", tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(main)}):
            hook = RuffFormatHook(hook_input)
            hook.track_file.write_text(f"{main_file}\n{wt_file}\n")
            with patch("subprocess.run", return_value=ok()) as mock_run:
                assert hook.run() == 0
            calls = {c.kwargs["cwd"]: c.args[0] for c in mock_run.call_args_list}
            assert calls == {
                main: ["uv", "run", "ruff", "format", main_file],
                worktree: ["uv", "run", "ruff", "format", wt_file],
            }

    def test_ruff_check_runs_in_worktree(self, tmp_path: Path) -> None:
        main, worktree = make_repo(tmp_path)
        wt_file = f"{worktree}/src/wt_file.py"
        hook_input = HookInput(session_id="s", tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(main)}):
            hook = RuffCheckHook(hook_input)
            hook.track_file.write_text(f"{wt_file}\n")
            with patch("subprocess.run", return_value=ok()) as mock_run:
                assert hook.run() == 0
            mock_run.assert_called_once()
            assert mock_run.call_args.args[0] == [
                "uv",
                "run",
                "ruff",
                "check",
                "--fix",
                wt_file,
            ]
            assert mock_run.call_args.kwargs["cwd"] == worktree

    def test_session_state_stays_in_project_dir(self, tmp_path: Path) -> None:
        main, worktree = make_repo(tmp_path)
        hook_input = HookInput(
            session_id="s", tool_input={}, raw={"cwd": str(worktree)}
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(main)}):
            hook = PytestHook(hook_input)
            assert hook.log_dir == main / ".claude" / "debug" / "sessions" / "s"


class TestGitStatusUsesSessionCwd:
    def test_git_status_in_worktree(self, tmp_path: Path) -> None:
        main, worktree = make_repo(tmp_path)
        hook_input = HookInput(
            session_id="s", tool_input={}, raw={"cwd": str(worktree / "src")}
        )
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(main)}):
            hook = GitStatusHook(hook_input)
            with patch("subprocess.run", return_value=ok()) as mock_run:
                hook.run()
            assert mock_run.call_args.kwargs["cwd"] == worktree

    def test_git_status_without_cwd(self, tmp_path: Path) -> None:
        main, _ = make_repo(tmp_path)
        hook_input = HookInput(session_id="s", tool_input={}, raw={})
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(main)}):
            hook = GitStatusHook(hook_input)
            with patch("subprocess.run", return_value=ok()) as mock_run:
                hook.run()
            assert mock_run.call_args.kwargs["cwd"] == main
