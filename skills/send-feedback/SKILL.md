---
name: "closedloop:send-feedback"
description: "Send feedback about ClosedLoop AI to the ClosedLoop team — a bug, a feature request, or praise about the platform itself. Translated to English and sent directly; no confirmation, no ticket id."
---

# /closedloop:send-feedback

Use this to tell the ClosedLoop team something about **ClosedLoop AI itself** — a bug you hit, a feature you want, or something you love. It goes straight to the ClosedLoop product team.

(This is feedback ABOUT ClosedLoop AI. It is NOT for logging your own customers' feedback — that flows in automatically through your connected sources, and the read skills like `/closedloop:deep-dive` surface it.)

## Check ClosedLoop AI MCP is available

Try calling `get_overview(time_range="all")`.

**If the call fails or the tool is not found:**

```
ClosedLoop AI MCP is not connected.

  claude mcp add --transport http closedloop-ai https://mcp.closedloop.sh

Then restart Claude Code, type /mcp, select closedloop-ai, and authorize.
Guide: https://closedloop.sh/docs/mcp-server/overview
```

Then stop.

Also confirm `send_closedloop_feedback` is in the tool list. If you see the read tools (`get_overview`, `search_insights`, …) but **not** `send_closedloop_feedback`, your MCP connection predates the tool — reconnect (`/mcp` → re-authorize) to pick it up.

## Input handling

You describe the feedback in plain language.

```
/closedloop:send-feedback the weekly brief should let me filter by segment
/closedloop:send-feedback the deep-dive skill timed out on a big query
/closedloop:send-feedback <feedback about ClosedLoop AI, in any language>
```

If you point at something earlier in the conversation ("send that to the ClosedLoop team"), use it — don't make the user retype it.

## Execution

### Step 1: Capture the feedback

Take what the user wants to tell the ClosedLoop team about ClosedLoop AI. Use **only** what they actually said — don't invent or embellish.

### Step 2: Translate to English

If it isn't in English, translate **faithfully** — preserve the meaning, keep the user's own framing, don't summarize. (ClosedLoop AI content is English downstream.)

### Step 3: Send

Call `send_closedloop_feedback(content="{English feedback}", metadata={…})` directly — **no confirmation step, just send it**. Optional `metadata` can carry light context (e.g. which part of the platform, feedback type) — only what's actually known. The tool returns a plain success confirmation (no id). Tell the user it was sent to the ClosedLoop team, in one line.

## Output format

```
✓ Sent to the ClosedLoop team
  {one-line restatement of the feedback}
```

## Rules

- **Their words, faithfully.** Translate without summarizing; don't compress the feedback into your own words or invent detail.
- **No confirmation step — just send it.** No preview, no approve prompt.
- **English only in `content`.** Translate if the user wrote in another language.
- **Honest confirmation.** Report it as "sent to the ClosedLoop team" — never "analyzed", and never show or invent an id (the tool returns success only, not a ticket number).
- **One piece of feedback per call.** Several distinct points → send each separately.

## What this skill does NOT do

- **Not for logging your own customers' feedback.** That comes in through your connected sources (Gong, Intercom, surveys, …); the read skills surface it. This skill only sends feedback to the ClosedLoop team about ClosedLoop AI.
- **Does not invent.** It sends what the user actually wrote (translated), nothing fabricated.
- **Does not return a ticket id.** It's a feedback channel, not a support-ticket system.
