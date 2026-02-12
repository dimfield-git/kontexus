# kontexus - Product Roadmap
## LLM Context Manager

**Project:** kontexus  
**Status:** Planning complete, awaiting Phase 1 build  
**Last Updated:** February 11, 2026  
**Maintainer:** Ted Karlsson

---

## Document Purpose

This roadmap tracks future features, enhancements, and experimental ideas beyond the core project plan. The project plan defines what we're building now. This roadmap defines where we might go next.

**Core Project Plan:** See `kontexus-project-plan.md` (locked specification)

---

## Current State: Foundation (Locked)

### Phase 1: Python CLI Core ✓ Planned
- Data model + SQLite schema
- CLI commands (add, list, view, rate, search, export)
- S/A/B/F tier validation
- Basic error handling

### Phase 2: FastAPI Backend ✓ Planned
- REST API exposing context operations
- Auto-generated API docs
- Local server (localhost:8000)

### Phase 3: Browser Extension ✓ Planned
- Extension UI for quick access
- Save/retrieve context without leaving browser
- Tier filtering and rating

---

## Near-Term Enhancements (Post-MVP)

### 1.1 Rich Metadata
**When:** After Phase 1 is working and being used daily  
**Why:** Make context entries more discoverable and useful

**Features:**
- Tag system (technical, career, learning, project-specific)
- Source URL tracking (which chat link produced this)
- Character/token count for summaries
- Last accessed timestamp
- Usage counter (how many times exported/viewed)

**Complexity:** Low (just additional database columns)

---

### 1.2 Advanced Export Formats
**When:** After core export is working  
**Why:** Different use cases need different formats

**Features:**
- **Markdown with metadata header** (readable + parseable)
- **JSON with full metadata** (programmatic use)
- **Plain text optimized for LLM input** (clean, no fluff)
- **Batch export** (all S-tier contexts, contexts by tag, date range)
- **Template system** (customize export format)

**Complexity:** Low-Medium (format transformation logic)

---

### 1.3 Version Tracking
**When:** After you start iterating on context summaries  
**Why:** Context refinement over time

**Features:**
- Track versions of the same context entry
- Diff view between versions
- Restore previous versions
- Version comments ("refined technical depth", "added project updates")

**Complexity:** Medium (schema changes, UI for version navigation)

---

## Mid-Term Features (Proven Value)

### 2.1 LLM Reliability Tracking
**When:** After you have 20+ context entries from different LLMs  
**Why:** Build evidence-based model selection strategy

**Features:**
- **Failure mode tagging:**
  - over_encouragement (GPT's snake whisper)
  - hallucination (factual errors)
  - timidity (overly cautious, won't commit)
  - context_drift (loses thread mid-response)
  - pattern_matching_error (wrong assumptions)
- **Analytics dashboard:**
  - Tier distribution by LLM
  - Failure mode frequency per model
  - Best model for specific task types
- **Search/filter:**
  - "Show all GPT contexts with over_encouragement"
  - "Show S-tier Claude summaries for technical content"

**Complexity:** Medium (new schema fields, aggregation queries, possibly simple visualization)

**Schema additions:**
```sql
ALTER TABLE contexts ADD COLUMN failure_modes TEXT;  -- JSON array
ALTER TABLE contexts ADD COLUMN task_type TEXT;      -- technical, creative, analysis, etc.
```

---

### 2.2 Smart Search
**When:** After you have 50+ contexts and basic search feels limited  
**Why:** Find relevant context faster

**Features:**
- Full-text search across prompt + summary + comments
- Search by date range
- Combined filters (tier + LLM + tags + date)
- Fuzzy matching ("roobtics" finds "robotics")
- Search result ranking (by tier, recency, usage count)

**Complexity:** Medium (potentially add FTS5 SQLite extension)

---

### 2.3 Context Relationships
**When:** When you notice contexts reference each other  
**Why:** Track conceptual lineage

**Features:**
- Link related contexts ("this builds on context #12")
- Context chains/threads
- Dependency visualization (simple tree/graph)
- "Show all contexts related to TedOS project"

**Complexity:** Medium-High (graph data model, UI complexity)

---

## Long-Term Vision (Experimental)

### 3.1 Multi-Machine Sync
**When:** If you use multiple computers regularly  
**Why:** Access contexts anywhere

**Options:**
- Git-based sync (commit .db file)
- Cloud storage sync (Dropbox/Drive folder)
- Custom sync service (SQLite → remote DB)

**Complexity:** High (conflict resolution, network code)  
**Risk:** May over-complicate the simple tool  
**Decision:** Only if manual file copying becomes painful

---

### 3.2 Collaborative Contexts
**When:** If you work with others on shared projects  
**Why:** Team knowledge management

**Features:**
- Shared context pools
- Multi-user rating (average tiers)
- Comments/discussions per context
- Access control (read/write permissions)

**Complexity:** Very High (authentication, permissions, collaboration UI)  
**Risk:** Scope creep, security concerns  
**Decision:** Probably separate product; keep personal tool lean

---

### 3.3 AI-Assisted Features
**When:** After core tool is mature and you're familiar with usage patterns  
**Why:** Reduce manual work, surface insights

**Potential features:**
- Auto-suggest tags based on content
- Detect duplicate/similar contexts
- Auto-tier suggestion based on content quality metrics
- Summary quality scoring
- Recommend contexts when starting new chats

**Complexity:** High (requires ML/heuristics, API integration)  
**Risk:** Over-engineering, introduces dependencies  
**Decision:** Evaluate only if manual processes become bottleneck

---

### 3.4 Integration with Other Tools
**When:** If specific integrations prove valuable  
**Why:** Reduce friction in existing workflows

**Potential integrations:**
- **Obsidian/Notion:** Export contexts as notes
- **GitHub:** Auto-create context from issue/PR discussions
- **Slack/Discord:** Save important conversations as contexts
- **Email:** Forward summaries to yourself
- **RSS/Read-later:** Capture article summaries

**Complexity:** Medium-High per integration  
**Decision:** Build only high-value integrations, keep core tool independent

---

## Ideas Under Evaluation

### Template Library
- Pre-built context templates for common use cases
- "Technical deep-dive template", "Career discussion template", etc.
- Community-contributed templates

**Status:** Interesting, but might be over-engineering  
**Next step:** Wait to see if patterns emerge naturally in your usage

---

### Context Quality Metrics
- Automated scoring: length, structure, specificity
- "Health check" for existing contexts
- Suggest improvements ("add source URL", "clarify tier rationale")

**Status:** Potentially useful, but risks making tool feel naggy  
**Next step:** Track manually first, automate only if clear patterns emerge

---

### Natural Language CLI
- `context find "that thing about rust we discussed last week"`
- LLM-powered query parsing → structured search

**Status:** Cool but gimmicky for power users; CLI flags are more precise  
**Next step:** Probably skip unless you find yourself wishing for it

---

### Analytics Dashboard
- Usage trends over time
- Most valuable contexts (S-tier, frequently accessed)
- LLM comparison charts
- Context creation velocity

**Status:** Nice-to-have, low priority  
**Next step:** Simple CLI stats first (`context stats`), GUI dashboard only if justified

---

## Principles for Roadmap Evaluation

Before adding any feature to the build queue, ask:

1. **Does it solve a real problem I'm experiencing?** (Not hypothetical)
2. **Is the manual process actually painful?** (Automation must justify complexity)
3. **Does it align with "lean tool" philosophy?** (Avoid feature creep)
4. **Can I build it in a weekend or less?** (Complexity budget)
5. **Will it make me use the tool more, or just feel clever?** (Utility > novelty)

**Remember:** The best feature is often the one you don't build.

---

## Decision Log

| Feature | Decision | Rationale | Date |
|---------|----------|-----------|------|
| LLM failure mode tracking | ✓ Add to roadmap (Mid-term) | Directly supports multi-model usage strategy | 2026-02-11 |
| Multi-machine sync | ⏸ Evaluate later | Manual file copying works for now | 2026-02-11 |
| Collaborative features | ✗ Out of scope | Personal tool, different product category | 2026-02-11 |

---

## Contributing Ideas

If someone helps you build this or suggests features:

1. Add to "Ideas Under Evaluation"
2. Apply the 5 evaluation questions
3. If it passes, move to appropriate roadmap tier
4. Update decision log

Keep the core project plan untouched. This roadmap is the experimentation space.

---

## Success Metrics

**Phase 1 success:**
- Using tool daily for 2+ weeks
- Created 10+ context entries
- Successfully reused contexts across LLM instances

**Phase 2 success:**
- Browser extension works reliably
- Save context without leaving browser
- API feels natural to use

**Phase 3 success:**
- Tool has saved you measurable time
- Would be annoyed if it broke
- Considering which roadmap features to build next

---

**Next Review:** After Phase 1 is complete and in daily use

**Living Document:** Update as usage patterns emerge and priorities shift
