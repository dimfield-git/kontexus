"""SQLite connection management and migrations."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "contexts.db"



###The MIGRATIONS list is where future schema changes go — just append a new SQL string
###and init_db() will pick it up automatically based on the version number.

MIGRATIONS = [
    # Version 1: initial schema
    """
    CREATE TABLE IF NOT EXISTS contexts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt TEXT NOT NULL,
        summary TEXT NOT NULL,
        source_chat TEXT,
        llm_used TEXT NOT NULL,
        tier TEXT CHECK(tier IN ('S', 'A', 'B', 'F')),
        comment TEXT,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
]


def get_db_path() -> Path:
    """Return the database path, creating parent dirs if needed."""
    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return DEFAULT_DB_PATH


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables and run pending migrations."""
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER NOT NULL
            )
        """)

        row = db.execute("SELECT version FROM schema_version").fetchone()
        current_version = row["version"] if row else 0

        for i, migration in enumerate(MIGRATIONS, start=1):
            if i > current_version:
                db.execute(migration)

        if current_version == 0:
            db.execute("INSERT INTO schema_version (version) VALUES (?)", (len(MIGRATIONS),))
        else:
            db.execute("UPDATE schema_version SET version = ?", (len(MIGRATIONS),))