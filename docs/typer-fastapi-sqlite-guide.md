# Understanding Typer, FastAPI, and SQLite
## A Practical Guide for the kontexus Project

**Date:** February 11, 2026  
**For:** Developers new to these tools but familiar with Python basics

---

## Introduction

This document explains three Python tools we're using in the kontexus project. Each solves a specific problem:

- **Typer:** Makes building command-line interfaces (CLIs) easy and type-safe
- **FastAPI:** Creates modern web APIs with minimal code
- **SQLite:** Provides a simple, file-based database without server setup

Let's explore each one.

---

## Part 1: SQLite - The Database

### What Problem Does SQLite Solve?

You need to store data persistently. You could use:
- Plain text files (hard to query, prone to corruption)
- JSON files (better, but still limited search capability)
- MySQL/PostgreSQL (overkill - requires server setup, separate process)

**SQLite is the middle ground:** A real database engine, but stored in a single file. No server needed.

### Core Concepts

**1. It's Just a File**
```
my_database.db  ← This is your entire database
```

**2. Tables Store Structured Data**
Think of tables like spreadsheets with strict column types:

```
Context Entries Table:
┌────┬─────────────┬──────────┬──────┬──────────┐
│ id │ prompt      │ summary  │ tier │ created  │
├────┼─────────────┼──────────┼──────┼──────────┤
│ 1  │ "Sum this"  │ "..."    │ S    │ 2026-... │
│ 2  │ "Explain"   │ "..."    │ A    │ 2026-... │
└────┴─────────────┴──────────┴──────┴──────────┘
```

**3. SQL = Structured Query Language**
You interact with SQLite using SQL commands:

```sql
-- Create a table
CREATE TABLE contexts (
    id INTEGER PRIMARY KEY,
    prompt TEXT NOT NULL,
    summary TEXT NOT NULL,
    tier TEXT CHECK(tier IN ('S','A','B','F')),
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert data
INSERT INTO contexts (prompt, summary, tier) 
VALUES ('Explain SQLite', 'SQLite is...', 'S');

-- Query data
SELECT * FROM contexts WHERE tier = 'S';

-- Update data
UPDATE contexts SET tier = 'A' WHERE id = 1;

-- Delete data
DELETE FROM contexts WHERE id = 2;
```

### Using SQLite in Python

Python includes SQLite support built-in (no installation needed):

```python
import sqlite3

# Connect to database (creates file if doesn't exist)
conn = sqlite3.connect('contexts.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS contexts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt TEXT NOT NULL,
        tier TEXT
    )
''')

# Insert data
cursor.execute(
    "INSERT INTO contexts (prompt, tier) VALUES (?, ?)",
    ("What is SQLite?", "S")
)
conn.commit()  # Save changes

# Query data
cursor.execute("SELECT * FROM contexts WHERE tier = 'S'")
rows = cursor.fetchall()
for row in rows:
    print(row)  # (1, 'What is SQLite?', 'S')

# Always close when done
conn.close()
```

### Key SQLite Advantages

✓ **Zero configuration** - no server to install/manage  
✓ **Single file** - easy to backup, move, or version control  
✓ **Fast** - excellent for local applications  
✓ **Reliable** - used in phones, browsers, embedded systems  
✓ **Full-featured** - supports joins, indexes, transactions  

### SQLite Limitations (Not Relevant for Our Project)

✗ **Not for high-concurrency web apps** (many simultaneous writes)  
✗ **No built-in user authentication**  
✗ **Single database file** (harder to distribute across machines)

**For a local CLI tool?** SQLite is perfect.

---

## Part 2: Typer - The CLI Framework

### What Problem Does Typer Solve?

Building CLIs in pure Python is tedious:

```python
import sys

# Manual argument parsing - ugly and error-prone
if len(sys.argv) < 3:
    print("Usage: script.py <command> <id>")
    sys.exit(1)

command = sys.argv[1]
context_id = sys.argv[2]

if command == "view":
    # your logic
elif command == "rate":
    # your logic
else:
    print("Unknown command")
```

**Typer makes this clean and automatic:**

```python
import typer

app = typer.Typer()

@app.command()
def view(context_id: int):
    """View a context entry"""
    print(f"Viewing context {context_id}")

@app.command()
def rate(context_id: int, tier: str):
    """Rate a context entry"""
    print(f"Rating context {context_id} as {tier}")

if __name__ == "__main__":
    app()
```

Now you automatically get:
```bash
$ python cli.py view 5
Viewing context 5

$ python cli.py rate 5 S
Rating context 5 as S

$ python cli.py --help
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

Commands:
  view  View a context entry
  rate  Rate a context entry
```

### Core Typer Concepts

**1. Type Hints = Automatic Validation**

```python
def rate(context_id: int, tier: str):
    pass
```

Typer sees `int` and automatically:
- Converts the argument to integer
- Shows error if user provides non-integer
- Generates help text showing expected type

**2. Enums for Restricted Choices**

```python
from enum import Enum

class Tier(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    F = "F"

@app.command()
def rate(context_id: int, tier: Tier):
    print(f"Tier: {tier.value}")
```

Now Typer only accepts S/A/B/F. Anything else = automatic error.

**3. Options vs Arguments**

```python
@app.command()
def search(
    query: str,                          # Required argument
    tier: Tier = None,                   # Optional argument with default
    limit: int = typer.Option(10, "--limit", "-l")  # Flag option
):
    pass
```

Usage:
```bash
$ python cli.py search "career advice"           # Uses defaults
$ python cli.py search "tech" S                  # Filters by S tier
$ python cli.py search "tech" --limit 5          # Limits results
$ python cli.py search "tech" S -l 20            # Combines both
```

**4. Automatic Help Generation**

```python
@app.command()
def add(
    prompt: str = typer.Argument(..., help="The prompt you gave the LLM"),
    summary: str = typer.Argument(..., help="The context summary generated")
):
    """Add a new context entry to the database."""
    pass
```

Generates beautiful help:
```bash
$ python cli.py add --help
Usage: cli.py add [OPTIONS] PROMPT SUMMARY

  Add a new context entry to the database.

Arguments:
  PROMPT   The prompt you gave the LLM  [required]
  SUMMARY  The context summary generated  [required]
```

### Real Example for Context Manager

```python
import typer
from enum import Enum
from datetime import datetime

app = typer.Typer()

class Tier(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    F = "F"

@app.command()
def add(
    prompt: str,
    summary: str,
    source_chat: str = typer.Option(None, help="Name of source chat"),
    llm_used: str = typer.Option("Claude", help="Which LLM generated this")
):
    """Add a new context entry."""
    # Here you'd insert into SQLite
    typer.echo(f"Added context from {source_chat} using {llm_used}")

@app.command()
def rate(
    context_id: int,
    tier: Tier,
    comment: str = typer.Option("", help="Optional comment")
):
    """Rate an existing context entry."""
    # Here you'd update SQLite
    typer.echo(f"Rated context {context_id} as {tier.value}")
    if comment:
        typer.echo(f"Comment: {comment}")

@app.command()
def list_contexts(
    tier: Tier = typer.Option(None, help="Filter by tier"),
    limit: int = typer.Option(10, help="Max results to show")
):
    """List all context entries."""
    # Here you'd query SQLite
    filter_msg = f" (tier {tier.value})" if tier else ""
    typer.echo(f"Showing up to {limit} contexts{filter_msg}")

if __name__ == "__main__":
    app()
```

Usage:
```bash
$ kontexus add "Explain Typer" "Typer is a CLI framework..." --source-chat "Learning Python"
$ kontexus rate 1 S --comment "Excellent summary"
$ kontexus list-contexts --tier S --limit 5
```

### Why Typer Over Click?

**Click** (older, more common):
```python
@click.command()
@click.argument('context_id', type=int)
@click.option('--tier', type=click.Choice(['S','A','B','F']))
def rate(context_id, tier):
    pass
```

**Typer** (modern, type-hint based):
```python
@app.command()
def rate(context_id: int, tier: Tier):
    pass
```

Typer is:
- Less boilerplate
- Type-safe (IDE autocomplete works)
- Validation automatic from type hints
- Made by same creator as FastAPI (consistent style)

---

## Part 3: FastAPI - The Web API Framework

### What Problem Does FastAPI Solve?

You want to expose your data/logic via HTTP so other programs (like a browser extension) can access it.

**Traditional approach (Flask):**
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/contexts/<int:context_id>', methods=['GET'])
def get_context(context_id):
    # Manual validation
    # Manual response formatting
    # No automatic documentation
    context = fetch_from_db(context_id)
    return jsonify(context)
```

**FastAPI approach:**
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Context(BaseModel):
    id: int
    prompt: str
    summary: str
    tier: str

@app.get("/contexts/{context_id}")
def get_context(context_id: int) -> Context:
    context = fetch_from_db(context_id)
    return context  # FastAPI handles JSON conversion
```

You automatically get:
- Type validation (context_id must be int)
- Automatic JSON serialization
- Interactive API documentation at `/docs`
- Request/response schema generation

### Core FastAPI Concepts

**1. Path Parameters**

```python
@app.get("/contexts/{context_id}")
def get_context(context_id: int):
    return {"id": context_id}
```

```bash
GET http://localhost:8000/contexts/5
→ {"id": 5}
```

**2. Query Parameters**

```python
@app.get("/contexts")
def list_contexts(tier: str = None, limit: int = 10):
    return {"tier": tier, "limit": limit}
```

```bash
GET http://localhost:8000/contexts?tier=S&limit=5
→ {"tier": "S", "limit": 5}
```

**3. Request Body (Pydantic Models)**

```python
from pydantic import BaseModel

class ContextCreate(BaseModel):
    prompt: str
    summary: str
    tier: str

@app.post("/contexts")
def create_context(context: ContextCreate):
    # context.prompt, context.summary, context.tier are validated
    return {"created": context}
```

```bash
POST http://localhost:8000/contexts
Body: {"prompt": "...", "summary": "...", "tier": "S"}
```

**4. Response Models**

```python
class Context(BaseModel):
    id: int
    prompt: str
    tier: str
    created: datetime

@app.get("/contexts/{context_id}", response_model=Context)
def get_context(context_id: int) -> Context:
    # Return must match Context schema
    return fetch_from_db(context_id)
```

FastAPI validates the response matches the schema.

### Real Example for Context Manager

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

app = FastAPI(title="LLM Context Manager API")

# Enums
class Tier(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    F = "F"

# Request/Response Models
class ContextCreate(BaseModel):
    prompt: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    source_chat: Optional[str] = None
    llm_used: str = "Claude"
    tier: Optional[Tier] = None

class ContextUpdate(BaseModel):
    tier: Tier
    comment: Optional[str] = None

class Context(BaseModel):
    id: int
    prompt: str
    summary: str
    source_chat: Optional[str]
    llm_used: str
    tier: Optional[Tier]
    comment: Optional[str]
    created: datetime

# Endpoints
@app.post("/contexts", response_model=Context, status_code=201)
def create_context(context: ContextCreate):
    """Create a new context entry."""
    # Insert into SQLite, return created context
    new_context = insert_to_db(context)
    return new_context

@app.get("/contexts", response_model=List[Context])
def list_contexts(
    tier: Optional[Tier] = None,
    limit: int = 10,
    offset: int = 0
):
    """List all contexts with optional filtering."""
    contexts = query_db(tier=tier, limit=limit, offset=offset)
    return contexts

@app.get("/contexts/{context_id}", response_model=Context)
def get_context(context_id: int):
    """Get a specific context by ID."""
    context = query_db_by_id(context_id)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    return context

@app.put("/contexts/{context_id}/rate", response_model=Context)
def rate_context(context_id: int, rating: ContextUpdate):
    """Update tier and add comment for a context."""
    context = update_tier_in_db(context_id, rating.tier, rating.comment)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    return context

@app.delete("/contexts/{context_id}", status_code=204)
def delete_context(context_id: int):
    """Delete a context entry."""
    deleted = delete_from_db(context_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Context not found")
    return None
```

### Running the API

```bash
# Install FastAPI and server
pip install fastapi uvicorn

# Run the server
uvicorn main:app --reload

# Server starts at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Automatic Interactive Documentation

FastAPI generates Swagger UI at `/docs`:

```
http://localhost:8000/docs
```

You get a web interface where you can:
- See all endpoints
- View request/response schemas
- Test endpoints directly in browser
- No extra code needed - it's automatic

### Why FastAPI Over Flask?

| Feature | Flask | FastAPI |
|---------|-------|---------|
| Type validation | Manual | Automatic (Pydantic) |
| API docs | Manual (external tools) | Automatic (built-in) |
| Async support | Limited | Native |
| Speed | Moderate | Very fast |
| Modern Python | No type hints | Type hints throughout |

For a learning project with an API? FastAPI is the modern choice.

---

## Part 4: How They Work Together

### Architecture Overview

```
┌─────────────────────────────────────────────┐
│          Browser Extension (JS/TS)          │
│  (Future Phase 3)                           │
└────────────────┬────────────────────────────┘
                 │ HTTP requests
                 ▼
┌─────────────────────────────────────────────┐
│          FastAPI Backend                    │
│  (Phase 2)                                  │
│  • Exposes REST endpoints                   │
│  • Validates requests/responses             │
│  • Handles HTTP logic                       │
└────────────────┬────────────────────────────┘
                 │ Function calls
                 ▼
┌─────────────────────────────────────────────┐
│          Core Logic Layer                   │
│  • Business logic (rating, searching, etc)  │
│  • Data validation                          │
│  • Database operations                      │
└────────────────┬────────────────────────────┘
                 │ SQL queries
                 ▼
┌─────────────────────────────────────────────┐
│          SQLite Database                    │
│  (Phase 1)                                  │
│  • contexts.db file                         │
│  • Stores all context entries               │
└─────────────────────────────────────────────┘
                 ▲
                 │ SQL queries
┌────────────────┴────────────────────────────┐
│          Typer CLI                          │
│  (Phase 1)                                  │
│  • Command-line interface                   │
│  • Parses arguments                         │
│  • Calls core logic                         │
└─────────────────────────────────────────────┘
```

### Example Flow: Rating a Context

**Via CLI:**
```bash
$ python cli.py rate 5 S --comment "Perfect summary"
```

1. **Typer** parses: `context_id=5`, `tier=Tier.S`, `comment="Perfect summary"`
2. **Typer** validates types (5 is int, S is valid Tier)
3. **Core logic** function called: `rate_context(5, "S", "Perfect summary")`
4. **SQLite** executes: `UPDATE contexts SET tier='S', comment='...' WHERE id=5`
5. **CLI** displays: "Context 5 rated as S"

**Via API (browser extension in future):**
```javascript
// Browser extension JavaScript
fetch('http://localhost:8000/contexts/5/rate', {
    method: 'PUT',
    body: JSON.stringify({ tier: 'S', comment: 'Perfect summary' })
})
```

1. **FastAPI** receives HTTP PUT request
2. **Pydantic** validates request body matches `ContextUpdate` schema
3. **Same core logic** function called: `rate_context(5, "S", "Perfect summary")`
4. **SQLite** executes same UPDATE query
5. **FastAPI** returns JSON response: `{"id": 5, "tier": "S", ...}`

**Key insight:** Both CLI and API use the same core logic and database. They're just different interfaces to the same functionality.

---

## Part 5: Development Workflow

### Phase 1: CLI + SQLite

**Project structure:**
```
kontexus/
├── kontexus_cli.py      # Typer CLI interface
├── database.py          # SQLite operations
├── models.py            # Data classes
└── contexts.db          # SQLite database (created on first run)
```

**Development steps:**
1. Design SQLite schema (tables, columns)
2. Create database operations (CRUD functions)
3. Build Typer CLI commands
4. Test with real data

**You'll learn:**
- SQL schema design
- Database transactions
- CLI argument parsing
- Data validation

### Phase 2: Add FastAPI

**Updated structure:**
```
kontexus/
├── kontexus_cli.py      # Typer CLI (unchanged)
├── api.py               # NEW: FastAPI application
├── database.py          # SQLite operations (reused)
├── models.py            # Data classes (reused)
└── contexts.db          # Same database
```

**Development steps:**
1. Create Pydantic models for API
2. Build FastAPI endpoints
3. Reuse existing database.py functions
4. Test API with browser or curl

**You'll learn:**
- REST API design
- HTTP methods (GET/POST/PUT/DELETE)
- Request/response modeling
- API documentation

### Phase 3: Browser Extension

**Updated structure:**
```
kontexus/
├── backend/
│   ├── kontexus_cli.py
│   ├── api.py
│   ├── database.py
│   ├── models.py
│   └── contexts.db
└── extension/           # NEW: Browser extension
    ├── manifest.json
    ├── popup.html
    ├── popup.js
    └── background.js
```

**Development steps:**
1. Create extension UI (HTML/CSS)
2. Write JavaScript to call your FastAPI backend
3. Handle browser permissions
4. Package for Chrome/Firefox

**You'll learn:**
- Browser extension APIs
- Cross-origin requests (CORS)
- Frontend-backend integration
- JavaScript async/await

---

## Part 6: Quick Start Examples

### Minimal SQLite Example

```python
import sqlite3

# Create/connect
conn = sqlite3.connect('test.db')
c = conn.cursor()

# Create table
c.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)')

# Insert
c.execute("INSERT INTO items (name) VALUES (?)", ("First item",))
conn.commit()

# Query
c.execute("SELECT * FROM items")
print(c.fetchall())  # [(1, 'First item')]

conn.close()
```

### Minimal Typer Example

```python
import typer

app = typer.Typer()

@app.command()
def hello(name: str):
    typer.echo(f"Hello {name}")

if __name__ == "__main__":
    app()
```

Run: `python script.py hello Ted` → "Hello Ted"

### Minimal FastAPI Example

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}
```

Run: `uvicorn script:app --reload`  
Visit: `http://localhost:8000/docs`

---

## Part 7: Common Patterns

### Pattern 1: Database Connection Management

**Problem:** Opening/closing connections for every operation is slow.

**Solution:** Context manager pattern

```python
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect('contexts.db')
    conn.row_factory = sqlite3.Row  # Returns dict-like rows
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Usage
def get_context(context_id: int):
    with get_db() as db:
        cursor = db.execute("SELECT * FROM contexts WHERE id = ?", (context_id,))
        return cursor.fetchone()
```

### Pattern 2: Pydantic Models from SQLite Rows

```python
from pydantic import BaseModel
from datetime import datetime

class Context(BaseModel):
    id: int
    prompt: str
    tier: str
    created: datetime

def get_context(context_id: int) -> Context:
    with get_db() as db:
        cursor = db.execute("SELECT * FROM contexts WHERE id = ?", (context_id,))
        row = cursor.fetchone()
        return Context(**dict(row))  # Convert SQLite row to Pydantic model
```

### Pattern 3: Shared Logic Between CLI and API

```python
# core.py - Business logic
def rate_context_logic(context_id: int, tier: str, comment: str = ""):
    with get_db() as db:
        db.execute(
            "UPDATE contexts SET tier = ?, comment = ? WHERE id = ?",
            (tier, comment, context_id)
        )
        cursor = db.execute("SELECT * FROM contexts WHERE id = ?", (context_id,))
        return cursor.fetchone()

# context_cli.py - CLI interface
@app.command()
def rate(context_id: int, tier: Tier, comment: str = ""):
    result = rate_context_logic(context_id, tier.value, comment)
    typer.echo(f"Rated context {result['id']} as {result['tier']}")

# api.py - API interface
@app.put("/contexts/{context_id}/rate")
def rate_context(context_id: int, rating: ContextUpdate):
    result = rate_context_logic(context_id, rating.tier, rating.comment)
    return Context(**dict(result))
```

---

## Summary

### SQLite
- **What:** File-based database, no server needed
- **Why:** Persistent storage with query capabilities
- **When:** Local applications, embedded systems, prototypes

### Typer
- **What:** CLI framework using type hints
- **Why:** Build command-line tools quickly with automatic validation
- **When:** User needs terminal interface to your application

### FastAPI
- **What:** Modern web API framework
- **Why:** Expose your logic via HTTP with automatic docs
- **When:** Other programs (browser, mobile app) need to access your data

### Together
All three work on the same SQLite database, but provide different interfaces:
- **Typer** → Terminal users
- **FastAPI** → Web/browser users
- **SQLite** → Permanent storage for both

---

## Next Steps

1. **Install tools:**
   ```bash
   pip install typer fastapi uvicorn
   ```

2. **Practice each individually:**
   - Create a simple SQLite table and query it
   - Build a basic Typer CLI with 2-3 commands
   - Create a FastAPI endpoint that returns JSON

3. **Combine them:**
   - Start with database + CLI (Phase 1)
   - Add API layer (Phase 2)
   - Build browser extension (Phase 3)

4. **Resources:**
   - Typer docs: https://typer.tiangolo.com
   - FastAPI docs: https://fastapi.tiangolo.com
   - SQLite tutorial: https://www.sqlitetutorial.net

---

**End of educational guide**  
**Ready to build!**
