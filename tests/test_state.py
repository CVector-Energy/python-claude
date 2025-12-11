"""Tests for QualityCheckState."""

import json
from pathlib import Path

from python_claude.hooks.state import QualityCheckState


class TestQualityCheckState:
    def test_default_state_all_enabled(self, tmp_path: Path) -> None:
        """Test that all checks are enabled by default."""
        state = QualityCheckState(tmp_path)
        assert state.is_enabled("pytest")
        assert state.is_enabled("mypy")
        assert state.is_enabled("ruff")

    def test_toggle_disables_check(self, tmp_path: Path) -> None:
        """Test that toggle disables an enabled check."""
        state = QualityCheckState(tmp_path)
        new_value = state.toggle("pytest")
        assert new_value is False
        assert not state.is_enabled("pytest")

    def test_toggle_enables_check(self, tmp_path: Path) -> None:
        """Test that toggle enables a disabled check."""
        state = QualityCheckState(tmp_path)
        state.disable("pytest")
        new_value = state.toggle("pytest")
        assert new_value is True
        assert state.is_enabled("pytest")

    def test_enable_check(self, tmp_path: Path) -> None:
        """Test that enable sets check to True."""
        state = QualityCheckState(tmp_path)
        state.disable("mypy")
        state.enable("mypy")
        assert state.is_enabled("mypy")

    def test_disable_check(self, tmp_path: Path) -> None:
        """Test that disable sets check to False."""
        state = QualityCheckState(tmp_path)
        state.disable("ruff")
        assert not state.is_enabled("ruff")

    def test_state_persists_across_instances(self, tmp_path: Path) -> None:
        """Test that state persists to file and loads correctly."""
        state1 = QualityCheckState(tmp_path)
        state1.disable("pytest")
        state1.disable("mypy")

        # Create new instance and verify state persisted
        state2 = QualityCheckState(tmp_path)
        assert not state2.is_enabled("pytest")
        assert not state2.is_enabled("mypy")
        assert state2.is_enabled("ruff")  # Should still be enabled

    def test_state_file_format(self, tmp_path: Path) -> None:
        """Test that state file has correct JSON format."""
        state = QualityCheckState(tmp_path)
        state.disable("pytest")
        state.enable("mypy")
        state.disable("ruff")

        state_file = tmp_path / ".claude" / "quality-checks.json"
        assert state_file.exists()

        with open(state_file) as f:
            data = json.load(f)

        assert data["pytest"] is False
        assert data["mypy"] is True
        assert data["ruff"] is False

    def test_corrupted_file_returns_defaults(self, tmp_path: Path) -> None:
        """Test that corrupted state file returns default values."""
        state_file = tmp_path / ".claude" / "quality-checks.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("invalid json{]")

        state = QualityCheckState(tmp_path)
        # Should return defaults when file is corrupted
        assert state.is_enabled("pytest")
        assert state.is_enabled("mypy")
        assert state.is_enabled("ruff")

    def test_non_dict_file_returns_defaults(self, tmp_path: Path) -> None:
        """Test that non-dict JSON returns default values."""
        state_file = tmp_path / ".claude" / "quality-checks.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text('["not", "a", "dict"]')

        state = QualityCheckState(tmp_path)
        # Should return defaults when file contains non-dict
        assert state.is_enabled("pytest")
        assert state.is_enabled("mypy")
        assert state.is_enabled("ruff")

    def test_multiple_toggles(self, tmp_path: Path) -> None:
        """Test multiple toggles work correctly."""
        state = QualityCheckState(tmp_path)

        # Toggle pytest multiple times
        assert state.toggle("pytest") is False  # enabled -> disabled
        assert state.toggle("pytest") is True  # disabled -> enabled
        assert state.toggle("pytest") is False  # enabled -> disabled

        # Verify final state
        assert not state.is_enabled("pytest")
