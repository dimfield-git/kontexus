"""Shared fixtures for kontexus tests."""

import pytest
from pathlib import Path
import kontexus.database as db_module


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    """Redirect all database operations to a temporary file.

    This runs automatically for every test — no test ever touches
    the real contexts.db in data/.
    """
    test_db = tmp_path / "test_contexts.db"
    monkeypatch.setattr(db_module, "DEFAULT_DB_PATH", test_db)
    db_module.init_db()
    return test_db
