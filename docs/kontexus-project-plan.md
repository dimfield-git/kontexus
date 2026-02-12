# kontexus
## LLM Context Manager - Project Plan v3 (Final)

## Project Overview
**Purpose:** Manage, version, and grade context handoff documents for cross-LLM/cross-chat continuity  
**Stack:** Python CLI (Typer) + FastAPI backend, SQLite storage, eventual browser extension (JS/TS)  
**Educational Value:** API design, database modeling, CLI tooling, browser extension architecture

---

## Core Features

### Data Model
**Context Entry:**
- Prompt text (what you asked the LLM to generate)
- Summary/response (the context document produced)
- Metadata: source chat name, creation date, LLM used, purpose/tags
- Your evaluation: **tier (S/A/B/F)**, comments
- Unique ID, version tracking

**Storage:** SQLite (portable, no dependencies, works everywhere)

---

## Development Phases

### Phase 1: Python CLI Core
**Goal:** Working tool you can actually use immediately

**Stack:** Python + Typer + SQLite

**Build:**
1. Data model + SQLite schema with migration support
2. CLI commands: `kontexus add`, `kontexus list`, `kontexus view <id>`, `kontexus rate <id> <tier> [comment]`, `kontexus search <query>`, `kontexus export <id>`
3. Tier validation (only S/A/B/F accepted)
4. Basic error handling

**Deliverable:** Functional CLI you install and use daily

---

### Phase 2: FastAPI Backend
**Goal:** Enable browser extension + learn API patterns

**Stack:** FastAPI + existing SQLite database

**Build:**
1. FastAPI backend exposing context operations
2. Endpoints: GET/POST/PUT for entries, search, ratings
3. Auto-generated API docs (FastAPI feature at /docs)
4. Local server (localhost:8000) - no auth needed initially

**Deliverable:** API you can test with browser/Postman, Python CLI can optionally use it too

---

### Phase 3: Browser Extension
**Goal:** Capture context directly from browser, quick access

**Stack:** JavaScript/TypeScript + Chrome/Firefox extension APIs

**Build:**
1. Extension UI (popup) - list contexts, search, view details
2. "Save current context" button (copies from clipboard or text selection)
3. Communicate with local FastAPI backend
4. Quick tier rating + commenting from browser
5. Filter by tier (show only S-tier contexts, etc.)

**Deliverable:** Browser button that lets you save/retrieve context without leaving your workflow

---

## Technical Decisions - Confirmed

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **CLI Framework** | Typer | Modern type hints, aligns with FastAPI philosophy, less boilerplate |
| **API Framework** | FastAPI | Async support, auto-docs, modern Python, educational value |
| **Storage** | SQLite | Portable, no server, works everywhere, simple |
| **Grade System** | S/A/B/F tiers | Clear quality tiers, familiar from gaming/ranking systems |
| **Core Use Cases** | Export AND rating equally important | Dual focus on retrieval and evaluation |

---

## Export Formats
- **JSON:** For programmatic processing/other tools
- **Markdown:** Human-readable, can paste directly in chats
- **Plain text:** Direct LLM input format

---

## Future Considerations
- Version tracking for context entries (when you update/refine a summary)
- Tag system for categorization (e.g., "technical", "career", "learning")
- Search by tier, date range, LLM used
- Batch operations (export all S-tier contexts, etc.)
- Optional sync between machines (future Phase 4?)

---

## Success Criteria
**Phase 1:** You're using it daily to manage actual context handoffs  
**Phase 2:** Browser extension successfully talks to local API  
**Phase 3:** You can capture and retrieve context without leaving browser  

---

## Next Steps
1. Begin Phase 1 implementation (awaiting your go-ahead)
2. Set up project structure (directory layout, dependencies)
3. Build core data model and CLI scaffolding
4. Iterate based on real usage

---

**Status:** Planning complete - awaiting build authorization

**Date Created:** February 11, 2026  
**Project Author:** Ted Karlsson
