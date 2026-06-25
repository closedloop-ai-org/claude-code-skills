---
name: "closedloop:watch"
description: "Set up a notification watch — get alerted (Slack / Teams / in-app) when something crosses a threshold in your ClosedLoop AI product insights."
---

# /closedloop:watch

Create a **notification watch**: a rule that alerts you when something happens in your ClosedLoop AI data — e.g. *"tell me when we get 5+ bug reports in a week."* You describe it in plain language; this compiles it into a precise rule, shows you exactly what it will watch, and (after you confirm) saves it. It's then evaluated automatically and notifies you when it fires.

## Input

```
/closedloop:watch alert me when 5+ bug reports come in over a week
/closedloop:watch ping me in #product when integration complaints spike
/closedloop:watch let me know if we get 3+ high-severity issues in 3 days
/closedloop:watch alert me in #cs when 3+ churn signals come in over two weeks
```

## What to do

1. **Fetch the catalog** — call `get_watch_catalog`. It returns the exact predicates, operators, and values you may use. **Compile only from these keys** — never invent a field or value.
2. **Compile the request into a rule IR.** Two threshold shapes are supported — a **threshold over product insights** (`subject: "insight"`) or over **strategic-intelligence signals incl. churn** (`subject: "signal"`):
   ```json
   {
     "name": "<short label>",
     "subject": "insight",
     "trigger": { "kind": "threshold", "cadence": "daily", "metric": { "agg": "count", "window_days": <N> }, "op": "gte", "value": <K> },
     "when": { "predicate": "insight.category", "op": "equals", "value": "bug" },
     "actions": [{ "type": "slack_message", "config": { "channel_id": "<from the user>" } }]
   }
   ```
   - Map "N+ X in D days" → `value: N`, `window_days: D`, and a `when` condition over the catalog (e.g. `insight.category = "bug"`, `insight.severity = "High"`, `insight.frustration_score >= 0.8`).
   - **`when` node shape (use this exactly).** A `when` is EITHER a leaf — `{ "predicate": "<key>", "op": "<op>", "value": <v> }` — OR a boolean group — `{ "op": "AND" | "OR" | "NOT", "conditions": [ <node>, … ] }` (`NOT` takes exactly one child). Nest freely. **It MUST be `op` + `conditions` — do NOT emit `{ "AND": [...] }` or `{ "combinator": "AND", ... }`; both fail validation.** Example — *critical bugs in checkout*:
     ```json
     { "op": "AND", "conditions": [
       { "predicate": "insight.category", "op": "equals", "value": "bug" },
       { "predicate": "insight.severity", "op": "equals", "value": "Critical" },
       { "predicate": "insight.feature_area", "op": "contains", "value": "checkout" }
     ] }
     ```
   - **Churn / signals**: for churn use `subject: "signal"` with `when: { predicate: "signal.is_stated_churn", op: "is_true" }` (the canonical stated-churn predicate, backed by `strategic_intelligence` record types — never the dead `is_churn_risk` flag). Or filter `signal.type` directly (`churn_reason`, `general_dislike`, `competitor_mention`, …), `signal.mention_kind`, `signal.is_blocker`.
   - **Delivery**: ask where to send it — a Slack channel (`slack_message`, `config.channel_id`), Teams (`teams_dm` / `teams_channel`), email (`email`, `config.recipients`), or a webhook (`webhook`, `config.url`). Don't assume a destination — if the user didn't name one, ask. (Don't use `inbox`; in-app delivery isn't wired up yet.)
3. **Validate** — call `validate_watch(rule=<ir>)`. If it returns errors, fix them against the catalog and re-validate. Don't proceed on errors.
4. **Read it back and confirm.** Tell the user in one plain-English line what will be watched and how they'll be notified — e.g. *"I'll alert you in-app when 5+ bug insights arrive within 7 days. Create it?"* **Wait for a yes.** Never auto-create.
5. **Create** — on confirmation, call `create_watch(rule=<ir>)`. Report the result in one line (it's saved and will notify them when it fires).

If these tools aren't available, the ClosedLoop AI MCP isn't connected — tell the user to run `claude mcp add --transport http closedloop-ai https://mcp.closedloop.sh`, then restart and `/mcp` → authorize.

## Rules

- **Catalog keys only** — every predicate, operator, and enum value must come from `get_watch_catalog`. Validate before creating.
- **Confirm before creating** — show the plain-English readback and wait for a yes. No auto-activate.
- **One watch per call.**
- **No invented thresholds** — if the user didn't give a number or window, ask (don't guess "5 in 7 days").

## Scope (today)

Supported now: **threshold alerts** over two subjects, both counting over a time window:
- **product insights** (`subject: "insight"`) — category / severity / emotion / feature-area / frustration / deal-blocker filters.
- **strategic-intelligence signals** (`subject: "signal"`) — including **stated churn** (`signal.is_stated_churn`, or `signal.type` = `churn_reason` / `general_dislike`), competitor mentions (`signal.type`, `signal.mention_kind`), and blockers (`signal.is_blocker`).

If the user asks for something outside this (per-account churn *state*, deal-stage changes, "X then Y" sequences), say what's supported today and that broader watches are coming — don't force-fit it into a shape that won't evaluate.

## Not this

- **Not for one-off questions** about your data — use `/closedloop:deep-dive` or `/closedloop:weekly-brief` for "what's happening right now."
- **Not for feedback about ClosedLoop AI itself** — that's `/closedloop:send-feedback`.
