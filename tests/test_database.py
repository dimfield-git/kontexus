"""Tests for database connection management and migrations."""

import sqlite3
from kontexus.database import get_db, init_db, get_db_path


class TestInitDb:
    """Verify schema creation and migration tracking."""

    def test_creates_contexts_table(self, tmp_db):
        with get_db() as db:
            row = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='contexts'"
            ).fetchone()
        assert row is not None

    def test_creates_schema_version_table(self, tmp_db):
        with get_db() as db:
            row = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
            ).fetchone()
        assert row is not None

    def test_schema_version_matches_migration_count(self, tmp_db):
        from kontexus.database import MIGRATIONS

        with get_db() as db:
            row = db.execute("SELECT version FROM schema_version").fetchone()
        assert row["version"] == len(MIGRATIONS)

    def test_init_db_is_idempotent(self, tmp_db):
        """Calling init_db() twice should not error or duplicate data."""
        init_db()
        init_db()
        with get_db() as db:
            rows = db.execute("SELECT * FROM schema_version").fetchall()
        assert len(rows) == 1

    def test_tier_check_constraint(self, tmp_db):
        """Only S/A/B/F should be accepted by the database."""
        with get_db() as db:
            # Valid tier should work
            db.execute(
                "INSERT INTO contexts (prompt, summary, llm_used, tier) VALUES (?, ?, ?, ?)",
                ("p", "s", "Claude", "S"),
            )

        # Invalid tier should raise
        import pytest
        with pytest.raises(sqlite3.IntegrityError):
            with get_db() as db:
                db.execute(
                    "INSERT INTO contexts (prompt, summary, llm_used, tier) VALUES (?, ?, ?, ?)",
                    ("p", "s", "Claude", "X"),
                )


class TestGetDb:
    """Verify connection context manager behavior."""

    def test_commits_on_success(self, tmp_db):
        with get_db() as db:
            db.execute(
                "INSERT INTO contexts (prompt, summary, llm_used) VALUES (?, ?, ?)",
                ("test", "test", "Claude"),
            )

        # Data should persist after the context manager exits
        with get_db() as db:
            row = db.execute("SELECT * FROM contexts WHERE prompt = 'test'").fetchone()
        assert row is not None

    def test_rolls_back_on_error(self, tmp_db):
        try:
            with get_db() as db:
                db.execute(
                    "INSERT INTO contexts (prompt, summary, llm_used) VALUES (?, ?, ?)",
                    ("rollback_test", "test", "Claude"),
                )
                raise ValueError("Simulated error")
        except ValueError:
            pass

        # Row should not exist after rollback
        with get_db() as db:
            row = db.execute(
                "SELECT * FROM contexts WHERE prompt = 'rollback_test'"
            ).fetchone()
        assert row is None

    def test_row_factory_returns_dict_like_rows(self, tmp_db):
        with get_db() as db:
            db.execute(
                "INSERT INTO contexts (prompt, summary, llm_used) VALUES (?, ?, ?)",
                ("dict_test", "summary", "GPT"),
            )
            row = db.execute("SELECT * FROM contexts").fetchone()
        assert row["prompt"] == "dict_test"
        assert row["llm_used"] == "GPT"
