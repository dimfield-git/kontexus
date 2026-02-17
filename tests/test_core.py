"""Tests for business logic in core.py."""

import json

from kontexus.core import (
    add_context,
    list_contexts,
    get_context,
    rate_context,
    search_contexts,
    export_context,
    delete_context,
    merge_contexts,
)
from kontexus.models import ContextCreate, Tier


def _make_entry(**overrides) -> ContextCreate:
    """Helper to build a ContextCreate with sensible defaults."""
    defaults = {
        "prompt": "Test prompt",
        "summary": "Test summary",
        "llm_used": "Claude",
        "source_chat": "Test Chat",
    }
    defaults.update(overrides)
    return ContextCreate(**defaults)


# --- add_context ---

class TestAddContext:

    def test_returns_context_with_id(self):
        entry = add_context(_make_entry())
        assert entry.id is not None
        assert entry.id >= 1

    def test_stores_all_fields(self):
        data = _make_entry(
            prompt="Specific prompt",
            summary="Specific summary",
            source_chat="My Chat",
            llm_used="GPT",
            tier=Tier.A,
            comment="Good one",
        )
        entry = add_context(data)
        assert entry.prompt == "Specific prompt"
        assert entry.summary == "Specific summary"
        assert entry.source_chat == "My Chat"
        assert entry.llm_used == "GPT"
        assert entry.tier == Tier.A
        assert entry.comment == "Good one"

    def test_unrated_entry_has_no_tier(self):
        entry = add_context(_make_entry())
        assert entry.tier is None

    def test_created_timestamp_is_set(self):
        entry = add_context(_make_entry())
        assert entry.created is not None


# --- list_contexts ---

class TestListContexts:

    def test_returns_empty_list_when_no_entries(self):
        assert list_contexts() == []

    def test_returns_all_entries(self):
        add_context(_make_entry(prompt="First"))
        add_context(_make_entry(prompt="Second"))
        assert len(list_contexts()) == 2

    def test_filters_by_tier(self):
        add_context(_make_entry(tier=Tier.S))
        add_context(_make_entry(tier=Tier.B))
        add_context(_make_entry(tier=Tier.S))

        s_entries = list_contexts(tier=Tier.S)
        assert len(s_entries) == 2
        assert all(e.tier == Tier.S for e in s_entries)

    def test_ordered_newest_first(self):
        first = add_context(_make_entry(prompt="First"))
        second = add_context(_make_entry(prompt="Second"))
        entries = list_contexts()
        assert entries[0].id == second.id
        assert entries[1].id == first.id


# --- get_context ---

class TestGetContext:

    def test_returns_entry_by_id(self):
        created = add_context(_make_entry(prompt="Find me"))
        found = get_context(created.id)
        assert found is not None
        assert found.prompt == "Find me"

    def test_returns_none_for_missing_id(self):
        assert get_context(9999) is None


# --- rate_context ---

class TestRateContext:

    def test_updates_tier(self):
        entry = add_context(_make_entry())
        rated = rate_context(entry.id, Tier.S)
        assert rated.tier == Tier.S

    def test_updates_comment(self):
        entry = add_context(_make_entry())
        rated = rate_context(entry.id, Tier.A, comment="Solid work")
        assert rated.comment == "Solid work"

    def test_returns_none_for_missing_id(self):
        assert rate_context(9999, Tier.F) is None


# --- search_contexts ---

class TestSearchContexts:

    def test_finds_match_in_prompt(self):
        add_context(_make_entry(prompt="Explain quantum computing"))
        results = search_contexts("quantum")
        assert len(results) == 1

    def test_finds_match_in_summary(self):
        add_context(_make_entry(summary="Quantum mechanics overview"))
        results = search_contexts("quantum")
        assert len(results) == 1

    def test_returns_empty_for_no_match(self):
        add_context(_make_entry(prompt="Python basics"))
        assert search_contexts("javascript") == []

    def test_case_insensitive_via_like(self):
        add_context(_make_entry(prompt="NixOS configuration"))
        results = search_contexts("nixos")
        assert len(results) == 1


# --- export_context ---

class TestExportContext:

    def test_markdown_format(self):
        entry = add_context(_make_entry(tier=Tier.S, source_chat="My Chat"))
        output = export_context(entry.id, "markdown")
        assert "# My Chat" in output
        assert "**Tier:** S" in output

    def test_json_format(self):
        entry = add_context(_make_entry(tier=Tier.A))
        output = export_context(entry.id, "json")
        parsed = json.loads(output)
        assert parsed["tier"] == "A"
        assert parsed["prompt"] == "Test prompt"

    def test_text_format(self):
        entry = add_context(_make_entry(tier=Tier.B))
        output = export_context(entry.id, "text")
        assert "Tier: B" in output
        assert "Test prompt" in output

    def test_returns_none_for_missing_id(self):
        assert export_context(9999) is None


# --- delete_context ---

class TestDeleteContext:

    def test_deletes_existing_entry(self):
        entry = add_context(_make_entry())
        assert delete_context(entry.id) is True
        assert get_context(entry.id) is None

    def test_returns_false_for_missing_id(self):
        assert delete_context(9999) is False


# --- merge_contexts ---

class TestMergeContexts:

    def test_creates_new_merged_entry(self):
        a = add_context(_make_entry(prompt="Prompt A", summary="Summary A"))
        b = add_context(_make_entry(prompt="Prompt B", summary="Summary B"))
        merged = merge_contexts(a.id, b.id)

        assert merged is not None
        assert merged.id not in (a.id, b.id)
        assert "Prompt A" in merged.prompt
        assert "Prompt B" in merged.prompt
        assert "Summary A" in merged.summary
        assert "Summary B" in merged.summary

    def test_preserves_originals(self):
        a = add_context(_make_entry(prompt="Keep A"))
        b = add_context(_make_entry(prompt="Keep B"))
        merge_contexts(a.id, b.id)

        assert get_context(a.id) is not None
        assert get_context(b.id) is not None

    def test_returns_none_if_id_missing(self):
        a = add_context(_make_entry())
        assert merge_contexts(a.id, 9999) is None
        assert merge_contexts(9999, a.id) is None
