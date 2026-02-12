# kontexus — Project Structure

```
kontexus/
├── pyproject.toml          # Project metadata, dependencies, CLI entry point
├── README.md               # Project documentation
├── .gitignore              # Git exclusions
│
├── src/
│   └── kontexus/
│       ├── __init__.py     # Package init
│       ├── cli.py          # Typer CLI commands (add, list, view, rate, search, export)
│       ├── core.py         # Business logic shared between CLI and API
│       ├── database.py     # SQLite connection management and migrations
│       ├── models.py       # Pydantic models and Tier enum
│       └── api.py          # FastAPI endpoints (Phase 2)
│
├── docs/                   # Project documentation (plans, guides, references)
│
├── tests/
│   ├── __init__.py
│   ├── test_core.py        # Tests for business logic
│   ├── test_cli.py         # Tests for CLI commands
│   └── test_database.py    # Tests for database operations
│
└── data/
    └── .gitkeep            # Holds contexts.db at runtime (gitignored)
```

## Design Rationale

**`src/` layout** — Prevents accidental imports from the working directory and keeps packaging clean for `pip install -e .`.

**`core.py` separate from `cli.py` and `api.py`** — All business logic lives in one place. The CLI and API are thin wrappers that call into it, so adding the FastAPI layer in Phase 2 requires no duplication.

**`models.py` shared** — The Tier enum and Pydantic models are defined once and consumed by both interfaces.

**`docs/`** — Keeps project plans, guides, and reference material out of the repo root. Houses the project plan, roadmap, and technical guides.

**`data/` for the database** — Keeps the `.db` file out of the source tree. The `.gitignore` excludes `data/*.db`.
