---
name: "closedloop-spec"
description: "Write a Google-design-doc technical spec for a feature, grounded in what customers actually said and in the patterns already in your codebase. Every design decision cites evidence or an existing file. Read only; writes no code and changes no data."
---

# ClosedLoop AI Spec

Write a technical spec for a feature, where every design decision cites either customer evidence or an existing pattern in the codebase. Nothing is invented.

This skill reads. It writes no code, changes no data, and opens no pull request.

## Check ClosedLoop AI MCP is available

Before doing anything, try calling `get_overview(time_range="all")`.

**If the call fails or the tool is not found:**

```
ClosedLoop AI MCP is not connected. This skill needs it to ground the spec in customer evidence.

Set it up in 30 seconds — use the endpoint that matches your ClosedLoop AI app URL:
  US  (app.closedloop.sh)     https://mcp.closedloop.sh
  EU  (eu.app.closedloop.sh)  https://eu.mcp.closedloop.sh

Then add it with your agent (swap in your region's URL):
  Claude Code   claude mcp add --transport http closedloop-ai <URL>   then /mcp and authorize
  Codex CLI     codex mcp add closedloop-ai --url <URL>               then codex mcp login closedloop-ai

Full guide: https://closedloop.sh/docs/mcp-server/overview
```

Then stop.

## Input

A feature or topic, and optionally a hint about where in the repo to look.

```text
Write a technical spec for the Slack integration
Spec out bulk editing, the code is in src/integrations
Technical spec for SSO
```

If no feature is given, ask for one rather than guessing.

## Step 1 — Pick the repo to search

If the input named a path, use it. Otherwise use Glob to find `package.json`, `pyproject.toml`, `go.mod`, or `Cargo.toml` one level deep from the working directory, then ask the user which repos to search with `AskUserQuestion` (multi-select, most likely first and marked "(Recommended)", always offering "Skip — no codebase search needed" last).

Wait for the answer before continuing.

## Step 2 — Fetch customer evidence

Three calls, all scoped to the feature:

1. `search_opportunities(query="<feature>")` — the clustered customer problems, and the unique customer count behind each. This is where the demand signal comes from.
2. `search_insights(query="<feature>")` — individual quotes, pain points, and workarounds. Call it a second time with `is_deal_blocker=true` to isolate the urgency signal.
3. `search_signals(query="<feature>", type="churn_reason")` — stated churn.

**Stated churn comes only from `search_signals`.** It is a strategic-intelligence record type, never a flag on an insight, so `search_signals(type="churn_reason")` is the only call that answers "is anyone leaving over this".

If all three come back empty, stop and say the feature has no customer evidence behind it. Do not write a spec with an empty PRD reference: the premise of this skill is that every decision cites something.

## Step 3 — Read the codebase before designing anything

Search for existing files of the same type as the feature, data model and migration files, API route conventions, and the test-file patterns the team already writes. Read one or two of the most relevant files.

Reference real file names and line numbers. Never invent an architecture the repo does not already have.

For any question about how an existing system works, look it up and answer it with a line reference. Do not leave a question open that the code answers.

## Step 4 — Write the spec

```text
# [Feature Name] — Technical Spec

**Author:** [leave blank]
**Status:** Draft
**PRD reference:** [one sentence: the job to be done from the evidence, plus the
highest-urgency signal — a deal blocker, stated churn, or the customer count]

## Context and Scope
The technical landscape this lands in: patterns already in the codebase with file
names and line numbers, relevant data models, and the customer job in one sentence
from evidence. Background only, no decisions.

## Goals and Non-Goals
Goals: the job stories from the evidence, stated as technical outcomes.
Non-goals: things that could be in scope and explicitly are not. Genuine scope
boundaries, never negated reliability goals ("shouldn't crash").

## Design
Trade-offs, not steps. If a decision is obvious, skip it and write the code.
  Data model changes — only new tables, columns, fields. Follow the migration
    pattern already in the repo.
  API contracts — match the route and handler conventions you found. Only new or
    changed endpoints, with request and response shape.
  System flow — source to storage to consumer, as a short numbered sequence.
  Key trade-offs — per decision: what you chose, the main alternative, and why.

## Alternatives Considered
Per rejected approach: what it was, why it looked reasonable, why it lost.

## Acceptance Criteria
Given / When / Then, matching the test style in the repo.

## Edge Cases
Only cases where the answer changes what you build.

## Observability
Success signal, and what detects a silent failure after hours of no activity.
Follow the logging and monitoring conventions already in the repo.

## Rollout
Feature flag and default, beta targets drawn from the highest-urgency customers
in the evidence, data migration, rollback.

## Open Questions
Only things you genuinely cannot determine without asking someone or running an
experiment.
```

## Rules

- **Every design decision cites evidence or an existing code pattern.** No invented architecture.
- **Content exclusions are non-goals, not edge cases.** Any data or content type a customer could reasonably expect to be covered and is not (message threads, attachments, historical backfill, private content) is an explicit non-goal with one sentence of reasoning. If the exclusion means the customer gets less than they expect, it is a scoping decision.
- **Close the onboarding gap in the system flow.** If any user action sits between "connected" and "first data flows" — inviting a bot, granting a scope, finishing a setup step — that step appears in the numbered sequence. Never jump from step 1 to step N. An undocumented gap leaves first-time users on an empty state with no guidance, which is a churn risk, so write the acceptance criterion for that empty state.
- **Acceptance criteria cover three layers.** One that asserts the end-to-end job is done and the data is visible to the user; one per distinct user-facing capability (connect, configure, disconnect, reconnect); and one per error state named in Edge Cases. Every edge case has a matching criterion.
- **Every new collection endpoint gets an empty-state criterion**, naming the exact response.
- **Never leave open a question the codebase answers.** If you read the code and found it, state it as a fact with a line reference.
- **Demand-signal numbers must match the PRD.** If a PRD already exists for this feature, the customer and insight counts must match it exactly, or you state why they differ. An unexplained discrepancy erodes trust in both documents.

## Feedback To ClosedLoop AI

If the evidence looks missing, stale, low-quality, or surprising, or the user says the spec matched the wrong customer needs, explicitly invite them to send feedback about ClosedLoop AI. If they ask you to send it, use `closedloop-send-feedback` or call `send_closedloop_feedback(content=...)`. Keep the feedback about the ClosedLoop AI product and data experience, strip PII and customer-specific data, and do not treat it as customer evidence.
