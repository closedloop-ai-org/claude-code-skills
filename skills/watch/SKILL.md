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
```

## What to do

1. **Fetch the catalog** — call `get_watch_catalog`. It returns the exact predicates, operators, and values you may use. **Compile only from these keys** — never invent a field or value.
2. **Compile the request into a rule IR.** Today the supported shape is a **threshold over product insights**:
   ```json
   {
     "name": "<short label>",
     "subject": "insight",
     "trigger": { "kind": "threshold", "cadence": "daily", "metric": { "agg": "count", "window_days": <N> }, "op": "gte", "value": <K> },
     "when": { "predicate": "insight.category", "op": "equals", "value": "bug" },
     "actions": [{ "type": "inbox", "config": {} }]
   }
   ```
   - Map "N+ X in D days" → `value: N`, `window_days: D`, and a `when` predicate over the catalog (e.g. `insight.category = "bug"`, `insight.severity = "High"`, `insight.frustration_score >= 0.8`). Combine conditions with `AND` / `OR` when the user names more than one.
   - **Delivery**: default to `inbox` (in-app). Use `slack_message` only if the user names a Slack channel — then put its channel id in `config.channel_id` (ask for it if you don't have it). `teams_dm` / `teams_channel` / `email` likewise.
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

Supported now: **threshold alerts on product insights** — counts of insights matching a category / severity / emotion / feature-area / frustration filter over a time window. If the user asks for something outside this (per-customer churn, deal-stage changes, competitor mentions, "X then Y" sequences), say what's supported today and that broader watches are coming — don't force-fit it into a shape that won't evaluate.

## Not this

- **Not for one-off questions** about your data — use `/closedloop:deep-dive` or `/closedloop:weekly-brief` for "what's happening right now."
- **Not for feedback about ClosedLoop AI itself** — that's `/closedloop:send-feedback`.
