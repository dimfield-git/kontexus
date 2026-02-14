# kontexus Context Merge Assessment

## Overview

You merged three different *kinds* of context into one package:

1)  **Interaction / Epistemic Contract**\
    (How you want the AI to behave + what "truth" means in your frame)

2)  **Personal / Professional Identity Snapshot**\
    (CV-grade facts + current trajectory)

3)  **Project Specification**\
    (kontexus architecture + state-of-build)

This is a strong move. These three layers---behavior drift, identity
drift, and project drift---are exactly where cross-chat continuity
typically fails.

The issue is not the content. It is the packaging.

Right now it is too easy for an LLM to: - Treat the epistemic contract
as psychoanalysis. - Treat the identity snapshot as a persona to
roleplay. - Treat the project spec as permanent truth even when
outdated.

------------------------------------------------------------------------

## What's Strong

-   **Subtractive coherence constraint** is excellent.\
    A stable negative boundary ("don't distort / don't invent /
    distinguish inference") generalizes well across domains.

-   **Fact vs inference separation** is explicitly valued.\
    This is one of the strongest anti-hallucination levers you can
    encode.

-   The **machine-optimized identity block** is very effective for
    cold-start onboarding. Dense, factual, minimal fluff.

-   The **kontexus specification** is operational.\
    It contains phases, schema, functions, layout --- enough structure
    for another LLM to meaningfully continue work.

------------------------------------------------------------------------

## Where It Risks Failing in Practice

### A) Scope Contamination

The first meta-summary contains psychologically loaded material (mother,
loneliness, health behaviors) alongside epistemic protocol. Many models
will default into therapy-mode simply because those details exist, even
if you reject moral framing. The presence itself acts as a trigger.

### B) Temporal Brittleness

Statements like: - "Phase 1 complete" - "All CLI commands working" -
"PyPI name claimed"

These age quickly. Without freshness handling, models will anchor on
stale state.

### C) Priority Ambiguity

The merged document does not encode precedence rules.

Example: - Project spec: "Be proactive surfacing structuring tools." -
Interaction protocol: "Avoid overreach."

Which outranks which? You know. The model does not.

------------------------------------------------------------------------

## The Single Best Improvement

Add a small header protocol at the top of the merged document:

### PRECEDENCE

Contract \> Facts \> Project \> Color/Brand \> Philosophy

### FRESHNESS

Any claim containing: "current," "working," "done," "claimed," "latest,"
etc. is tentative unless timestamped.

If it matters, ask once, briefly.

### MODE

Default behavior: - Collaborator - Minimal psychologizing - Separate
fact/inference - No padding

This alone significantly increases machine stability.

------------------------------------------------------------------------

## Suggested Restructuring (Same Content, More Stability)

### 1) Contract (One Screen, Bullet-Hard)

-   Do not invent.
-   Mark uncertainty.
-   Separate fact vs inference.
-   Avoid moral theater / enlightenment-status framing.
-   Keep answers tight unless expansion is requested.
-   Start serious sessions with mood/energy check (if user wants).

### 2) Identity Facts (Timestamped, Factual Only)

Use your machine-optimized block as-is.\
Add a date header.

### 3) Project Specification (Timestamped + Assumptions)

Add: - Repo path / branch / last commit hash (if available) - 1--2
working CLI examples - "Next 3 TODOs" (short)

### 4) Optional Human Context (Quarantined)

If including personal relational material, label it clearly:

> Optional --- Only engage if user explicitly raises topic.\
> Do not steer conversation here.

------------------------------------------------------------------------

## Verdict

The merged artifact is strong.

However, without: - Precedence encoding, - Freshness handling, - And
optional-context quarantine,

it remains vulnerable to: - Therapy-mode drift, - Stale-state
anchoring, - Persona roleplay drift.

Add those guardrails and it becomes a highly stable cross-LLM continuity
artifact.
