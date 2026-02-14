"""Business logic shared between CLI and API."""


"""One function per CLI command from the project plan:

1. add_context — insert a new context entry into the database
2. list_contexts — return all entries, optionally filtered by tier
3. get_context — fetch a single entry by ID
4. rate_context — update an entry's tier and optional comment
5. search_contexts — search across prompt/summary text by keyword
6. export_context — retrieve an entry and format it as markdown, JSON, or plain text
7. delete_context — remove an entry by ID
8. merge_contexts — concatenate two entries (A on top of B) into a new draft entry, user edits afterward"""



from typing import Optional

from kontexus.database import get_db, init_db
from kontexus.models import Context, ContextCreate, Tier


def add_context(data: ContextCreate) -> Context:
    """Insert a new context entry and return it."""
    init_db()
    with get_db() as db:
        cursor = db.execute(
            """
            INSERT INTO contexts (prompt, summary, source_chat, llm_used, tier, comment)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (data.prompt, data.summary, data.source_chat, data.llm_used,
             data.tier.value if data.tier else None, data.comment),
        )
        row = db.execute("SELECT * FROM contexts WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return Context(**dict(row))


def list_contexts(tier: Optional[Tier] = None) -> list[Context]:
    """Return all context entries, optionally filtered by tier."""
    init_db()
    with get_db() as db:
        if tier:
            rows = db.execute(
                "SELECT * FROM contexts WHERE tier = ? ORDER BY created DESC",
                (tier.value,),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM contexts ORDER BY created DESC"
            ).fetchall()
    return [Context(**dict(row)) for row in rows]


def get_context(context_id: int) -> Optional[Context]:
    """Fetch a single context entry by ID."""
    init_db()
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM contexts WHERE id = ?", (context_id,)
        ).fetchone()
    return Context(**dict(row)) if row else None

def rate_context(context_id: int, tier: Tier, comment: Optional[str] = None) -> Optional[Context]:
    """Update the tier and optional comment for a context entry."""
    init_db()
    with get_db() as db:
        db.execute(
            "UPDATE contexts SET tier = ?, comment = ? WHERE id = ?",
            (tier.value, comment, context_id),
        )
        row = db.execute(
            "SELECT * FROM contexts WHERE id = ?", (context_id,)
        ).fetchone()
    return Context(**dict(row)) if row else None


def search_contexts(query: str) -> list[Context]:
    """Search across prompt and summary fields by keyword."""
    init_db()
    with get_db() as db:
        rows = db.execute(
            """
            SELECT * FROM contexts
            WHERE prompt LIKE ? OR summary LIKE ?
            ORDER BY created DESC
            """,
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
    return [Context(**dict(row)) for row in rows]


def export_context(context_id: int, fmt: str = "markdown") -> Optional[str]:
    """Export a context entry as markdown, JSON, or plain text."""
    entry = get_context(context_id)
    if not entry:
        return None

    if fmt == "json":
        return entry.model_dump_json(indent=2)

    if fmt == "text":
        return (
            f"{entry.prompt}\n\n"
            f"{entry.summary}\n\n"
            f"Tier: {entry.tier.value if entry.tier else 'Unrated'}"
        )

    # Default: markdown
    return (
        f"# {entry.source_chat or 'Context'}\n\n"
        f"**Prompt:**\n{entry.prompt}\n\n"
        f"**Summary:**\n{entry.summary}\n\n"
        f"**Tier:** {entry.tier.value if entry.tier else 'Unrated'}  \n"
        f"**LLM:** {entry.llm_used}  \n"
        f"**Created:** {entry.created}"
    )


def delete_context(context_id: int) -> bool:
    """Delete a context entry by ID. Returns True if found and deleted."""
    init_db()
    with get_db() as db:
        cursor = db.execute(
            "DELETE FROM contexts WHERE id = ?", (context_id,)
        )
    return cursor.rowcount > 0


def merge_contexts(id_a: int, id_b: int) -> Optional[Context]:
    """Merge two context entries (A on top of B) into a new draft entry."""
    a = get_context(id_a)
    b = get_context(id_b)
    if not a or not b:
        return None

    merged = ContextCreate(
        prompt=f"{a.prompt}\n\n---\n\n{b.prompt}",
        summary=f"{a.summary}\n\n---\n\n{b.summary}",
        source_chat=f"Merged: {a.source_chat or id_a} + {b.source_chat or id_b}",
        llm_used=f"{a.llm_used}, {b.llm_used}",
    )
    return add_context(merged)







