# kontexus
<img width="1014" height="373" alt="Kontexusforgithub" src="https://github.com/user-attachments/assets/774203e9-49f1-451e-8328-abb0ce24c5a8" />

LLM Context Manager — manage, version, and grade context handoff documents for cross-LLM and cross-chat continuity.

Store prompts alongside their generated summaries, rate them using an S/A/B/F tier system, and build a searchable library of context handoffs you can export and feed into any LLM session.

## Requirements

- Python 3.10 or higher
- pip
- Git (optional, for cloning)

## Installation

Clone the repository and install in editable mode inside a virtual environment:

```bash
git clone https://github.com/dimfield-git/kontexus.git
cd kontexus
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

The `kontexus` command is now available in your terminal whenever the virtual environment is active. To activate it in future sessions:

```bash
cd ~/repos/kontexus
source .venv/bin/activate
```

## Usage

### Add a context entry

```bash
kontexus add "Your prompt" "The summary the LLM generated"
```

With options:

```bash
kontexus add "Your prompt" "The summary" -s "Chat name" -l GPT -t A -c "My notes"
```

| Flag | Long form | Description | Default |
|------|-----------|-------------|---------|
| `-s` | `--source-chat` | Name of the source chat | None |
| `-l` | `--llm-used` | Which LLM generated it | Claude |
| `-t` | `--tier` | Rating: S, A, B, or F | Unrated |
| `-c` | `--comment` | Your notes | None |
| `-pc` | `--prompt-clip` | Read prompt from clipboard | Off |
| `-sc` | `--summary-clip` | Read summary from clipboard | Off |

For long prompts or summaries, write them to files and use command substitution:

```bash
kontexus add "$(cat prompt.txt)" "$(cat summary.txt)" -s "Session name" -l GPT -t A
```
### Add from clipboard

Copy text to your clipboard, then:
```bash
# Summary from clipboard, prompt typed
kontexus add "My prompt" -sc -s "Chat name" -t A

# Both from clipboard
kontexus add -pc -sc -s "Chat name"
```

### List all entries

```bash
kontexus list
kontexus list --tier S
```

### View a single entry

```bash
kontexus view 1
```

### Rate an entry

```bash
kontexus rate 1 S
kontexus rate 1 A --comment "Decent but missing technical depth"
```

### Search across prompts and summaries

```bash
kontexus search "career"
```

### Export an entry

```bash
kontexus export 1
kontexus export 1 --fmt json
kontexus export 1 --fmt text
```

Supported formats: `markdown` (default), `json`, `text`.

### Delete an entry

```bash
kontexus delete 1
```

### Merge two entries

Combines two context entries into a new draft (first entry on top, separated by `---`):

```bash
kontexus merge 2 3
```

To merge three or more, chain the commands:

```bash
kontexus merge 2 3
kontexus merge 5 4
```

## Tier System

| Tier | Meaning |
|------|---------|
| S | Excellent — high-fidelity context that transfers cleanly |
| A | Good — usable with minor gaps |
| B | Acceptable — gets the job done but lacks depth |
| F | Failed — misleading, incomplete, or unusable |

## Project Structure

```
kontexus/
├── src/kontexus/
│   ├── cli.py        # Typer CLI commands
│   ├── core.py       # Business logic
│   ├── database.py   # SQLite connection and migrations
│   ├── models.py     # Pydantic models and Tier enum
│   └── api.py        # FastAPI endpoints (Phase 2)
├── data/             # SQLite database (gitignored)
├── tests/
└── docs/
```

## Data Storage

All data is stored locally in `data/contexts.db` (SQLite). No network access, no cloud dependencies, no accounts. The database file is gitignored by default.

## License

MIT
