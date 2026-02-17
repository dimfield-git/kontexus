"""Typer CLI commands for kontexus."""

"""cli.py is the user-facing layer — it translates terminal commands into calls to core.py. It handles argument parsing, 
input validation, and output formatting (what gets printed to the screen), but contains no business logic itself.
When you type kontexus add "my prompt" "my summary", Typer parses that into typed Python arguments, cli.py passes them
to core.py's add_context, and then formats the result for the terminal. Same logic, different presentation than what 
the API will do in Phase 2."""

import typer

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

import pyperclip

app = typer.Typer(help="kontexus — LLM Context Manager")


@app.command()
def add(
    prompt: str = typer.Argument("", help="The prompt you gave the LLM"),
    summary: str = typer.Argument("", help="The context summary generated"),
    prompt_clip: bool = typer.Option(False, "--prompt-clip", "-pc", help="Read prompt from clipboard"),
    summary_clip: bool = typer.Option(False, "--summary-clip", "-sc", help="Read summary from clipboard"),
    source_chat: str = typer.Option(None, "-s", "--source-chat", help="Name of source chat"),
    llm_used: str = typer.Option("Claude", "-l", "--llm-used", help="Which LLM generated this"),
    tier: Tier = typer.Option(None, "-t", "--tier", help="Initial tier rating (S/A/B/F)"),
    comment: str = typer.Option(None, "-c", "--comment", help="Optional comment"),
):
    """Add a new context entry."""
    if prompt_clip:
        prompt = pyperclip.paste()
        if not prompt.strip():
            typer.echo("Error: clipboard is empty (--prompt-clip).")
            raise typer.Exit(code=1)
    elif not prompt:
        typer.echo("Error: provide PROMPT as argument or use --prompt-clip.")
        raise typer.Exit(code=1)

    if summary_clip:
        summary = pyperclip.paste()
        if not summary.strip():
            typer.echo("Error: clipboard is empty (--summary-clip).")
            raise typer.Exit(code=1)
    elif not summary:
        typer.echo("Error: provide SUMMARY as argument or use --summary-clip.")
        raise typer.Exit(code=1)

    data = ContextCreate(
        prompt=prompt,
        summary=summary,
        source_chat=source_chat,
        llm_used=llm_used,
        tier=tier,
        comment=comment,
    )
    entry = add_context(data)
    typer.echo(f"Added context #{entry.id} (Tier: {entry.tier.value if entry.tier else 'Unrated'})")

@app.command("list")
def list_cmd(
        tier: Tier = typer.Option(None, help="Filter by tier (S/A/B/F)"),
):
    """List all context entries."""
    entries = list_contexts(tier)
    if not entries:
        typer.echo("No contexts found.")
        return
    for e in entries:
        typer.echo(f"#{e.id}  [{e.tier.value if e.tier else '-'}]  {e.source_chat or 'Untitled'}  ({e.created.strftime('%Y-%m-%d')})")

@app.command()
def view(context_id: int = typer.Argument(..., help="Context ID to view")):
    """View a single context entry."""
    entry = get_context(context_id)
    if not entry:
        typer.echo(f"Context #{context_id} not found.")
        raise typer.Exit(code=1)
    typer.echo(f"ID:          {entry.id}")
    typer.echo(f"Source:      {entry.source_chat or 'N/A'}")
    typer.echo(f"LLM:         {entry.llm_used}")
    typer.echo(f"Tier:        {entry.tier.value if entry.tier else 'Unrated'}")
    typer.echo(f"Comment:     {entry.comment or 'N/A'}")
    typer.echo(f"Created:     {entry.created}")
    typer.echo(f"\n--- Prompt ---\n{entry.prompt}")
    typer.echo(f"\n--- Summary ---\n{entry.summary}")

@app.command()
def rate(
        context_id: int = typer.Argument(..., help="Context ID to rate"),
        tier: Tier = typer.Argument(..., help="Tier rating (S/A/B/F)"),
        comment: str = typer.Option(None, help="Optional comment"),
):
    """Rate a context entry."""
    entry = rate_context(context_id, tier, comment)
    if not entry:
        typer.echo(f"Context #{context_id} not found.")
        raise typer.Exit(code=1)
    typer.echo(f"Context #{entry.id} rated as {entry.tier.value if entry.tier else 'Unrated'}")

@app.command()
def search(query: str = typer.Argument(..., help="Search keyword")):
    """Search across prompt and summary text."""
    entries = search_contexts(query)
    if not entries:
        typer.echo("No matches found.")
        return
    typer.echo(f"Found {len(entries)} match(es):")
    for e in entries:
        typer.echo(f"  #{e.id}  [{e.tier.value if e.tier else '-'}]  {e.source_chat or 'Untitled'}")

@app.command()
def export(
        context_id: int = typer.Argument(..., help="Context ID to export"),
        fmt: str = typer.Option("markdown", help="Format: markdown, json, or text"),
):
    """Export a context entry."""
    result = export_context(context_id, fmt)
    if not result:
        typer.echo(f"Context #{context_id} not found.")
        raise typer.Exit(code=1)
    typer.echo(result)

@app.command()
def delete(context_id: int = typer.Argument(..., help="Context ID to delete")):
    """Delete a context entry."""
    if not delete_context(context_id):
        typer.echo(f"Context #{context_id} not found.")
        raise typer.Exit(code=1)
    typer.echo(f"Context #{context_id} deleted.")

@app.command()
def merge(
        id_a: int = typer.Argument(..., help="First context ID (goes on top)"),
        id_b: int = typer.Argument(..., help="Second context ID"),
):
    """Merge two context entries into a new draft."""
    entry = merge_contexts(id_a, id_b)
    if not entry:
        typer.echo("One or both context IDs not found.")
        raise typer.Exit(code=1)
    typer.echo(f"Created merged context #{entry.id} from #{id_a} + #{id_b}")

if __name__ == "__main__":
    app()

