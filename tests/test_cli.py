"""Tests for Typer CLI commands."""

from typer.testing import CliRunner

from kontexus.cli import app
from kontexus.core import add_context
from kontexus.models import ContextCreate, Tier

from unittest.mock import patch

runner = CliRunner()


def _seed_entry(**overrides) -> int:
    """Insert a test entry and return its ID."""
    defaults = {
        "prompt": "Test prompt",
        "summary": "Test summary",
        "llm_used": "Claude",
        "source_chat": "Test Chat",
    }
    defaults.update(overrides)
    entry = add_context(ContextCreate(**defaults))
    return entry.id


# --- add ---

class TestAddCommand:

    def test_basic_add(self):
        result = runner.invoke(app, ["add", "My prompt", "My summary"])
        assert result.exit_code == 0
        assert "Added context #" in result.output

    def test_add_with_all_options(self):
        result = runner.invoke(app, [
            "add", "Prompt", "Summary",
            "-s", "Chat Name",
            "-l", "GPT",
            "-t", "S",
            "-c", "Great",
        ])
        assert result.exit_code == 0
        assert "Tier: S" in result.output

    def test_add_unrated(self):
        result = runner.invoke(app, ["add", "Prompt", "Summary"])
        assert "Unrated" in result.output


# --- list ---

class TestListCommand:

    def test_list_empty(self):
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No contexts found" in result.output

    def test_list_shows_entries(self):
        _seed_entry(source_chat="Session Alpha", tier=Tier.A)
        result = runner.invoke(app, ["list"])
        assert "Session Alpha" in result.output
        assert "[A]" in result.output

    def test_list_filters_by_tier(self):
        _seed_entry(tier=Tier.S, source_chat="S-tier")
        _seed_entry(tier=Tier.B, source_chat="B-tier")
        result = runner.invoke(app, ["list", "--tier", "S"])
        assert "S-tier" in result.output
        assert "B-tier" not in result.output


# --- view ---

class TestViewCommand:

    def test_view_existing(self):
        entry_id = _seed_entry(prompt="View this", source_chat="View Test")
        result = runner.invoke(app, ["view", str(entry_id)])
        assert result.exit_code == 0
        assert "View this" in result.output
        assert "View Test" in result.output

    def test_view_missing(self):
        result = runner.invoke(app, ["view", "9999"])
        assert result.exit_code == 1
        assert "not found" in result.output


# --- rate ---

class TestRateCommand:

    def test_rate_entry(self):
        entry_id = _seed_entry()
        result = runner.invoke(app, ["rate", str(entry_id), "S"])
        assert result.exit_code == 0
        assert "rated as S" in result.output

    def test_rate_with_comment(self):
        entry_id = _seed_entry()
        result = runner.invoke(app, ["rate", str(entry_id), "A", "--comment", "Nice"])
        assert result.exit_code == 0
        assert "rated as A" in result.output

    def test_rate_missing(self):
        result = runner.invoke(app, ["rate", "9999", "F"])
        assert result.exit_code == 1
        assert "not found" in result.output


# --- search ---

class TestSearchCommand:

    def test_search_finds_match(self):
        _seed_entry(prompt="Rust async patterns")
        result = runner.invoke(app, ["search", "Rust"])
        assert "1 match" in result.output

    def test_search_no_match(self):
        _seed_entry(prompt="Python basics")
        result = runner.invoke(app, ["search", "Haskell"])
        assert "No matches found" in result.output


# --- export ---

class TestExportCommand:

    def test_export_markdown(self):
        entry_id = _seed_entry(tier=Tier.S)
        result = runner.invoke(app, ["export", str(entry_id)])
        assert result.exit_code == 0
        assert "**Tier:** S" in result.output

    def test_export_json(self):
        entry_id = _seed_entry()
        result = runner.invoke(app, ["export", str(entry_id), "--fmt", "json"])
        assert result.exit_code == 0
        assert '"prompt"' in result.output

    def test_export_missing(self):
        result = runner.invoke(app, ["export", "9999"])
        assert result.exit_code == 1


# --- delete ---

class TestDeleteCommand:

    def test_delete_existing(self):
        entry_id = _seed_entry()
        result = runner.invoke(app, ["delete", str(entry_id)])
        assert result.exit_code == 0
        assert "deleted" in result.output

    def test_delete_missing(self):
        result = runner.invoke(app, ["delete", "9999"])
        assert result.exit_code == 1
        assert "not found" in result.output


# --- merge ---

class TestMergeCommand:

    def test_merge_two_entries(self):
        id_a = _seed_entry(prompt="Prompt A")
        id_b = _seed_entry(prompt="Prompt B")
        result = runner.invoke(app, ["merge", str(id_a), str(id_b)])
        assert result.exit_code == 0
        assert "merged context" in result.output.lower()

    def test_merge_missing_id(self):
        id_a = _seed_entry()
        result = runner.invoke(app, ["merge", str(id_a), "9999"])
        assert result.exit_code == 1
        assert "not found" in result.output


class TestAddClipboard:

    @patch("kontexus.cli.pyperclip.paste", return_value="Clipped prompt")
    def test_prompt_from_clipboard(self, mock_paste):
        result = runner.invoke(app, ["add", "-pc", "", "My summary"])
        assert result.exit_code == 0
        assert "Added context #" in result.output

    @patch("kontexus.cli.pyperclip.paste", return_value="Clipped summary")
    def test_summary_from_clipboard(self, mock_paste):
        result = runner.invoke(app, ["add", "My prompt", "-sc"])
        assert result.exit_code == 0
        assert "Added context #" in result.output

    @patch("kontexus.cli.pyperclip.paste", return_value="Clipped content")
    def test_both_from_clipboard(self, mock_paste):
        result = runner.invoke(app, ["add", "-pc", "-sc"])
        assert result.exit_code == 0
        assert "Added context #" in result.output

    @patch("kontexus.cli.pyperclip.paste", return_value="")
    def test_empty_clipboard_prompt(self, mock_paste):
        result = runner.invoke(app, ["add", "-pc", "", "Summary"])
        assert result.exit_code == 1
        assert "clipboard is empty" in result.output

    @patch("kontexus.cli.pyperclip.paste", return_value="")
    def test_empty_clipboard_summary(self, mock_paste):
        result = runner.invoke(app, ["add", "Prompt", "-sc"])
        assert result.exit_code == 1
        assert "clipboard is empty" in result.output

    def test_no_prompt_no_flag(self):
        result = runner.invoke(app, ["add", "", "Summary"])
        assert result.exit_code == 1
        assert "provide PROMPT" in result.output

    def test_no_summary_no_flag(self):
        result = runner.invoke(app, ["add", "Prompt", ""])
        assert result.exit_code == 1
        assert "provide SUMMARY" in result.output