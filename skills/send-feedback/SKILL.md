---
name: "closedloop:send-feedback"
description: "Send feedback about ClosedLoop AI to the ClosedLoop team — a bug, a feature request, or praise about the platform itself."
---

# /closedloop:send-feedback

Tell the ClosedLoop team something about **ClosedLoop AI itself** — a bug, a feature request, or praise. It goes to the ClosedLoop product team.

## Input

The user describes the feedback in plain language, or points at something earlier in the conversation ("send that to the ClosedLoop team").

```
/closedloop:send-feedback the weekly brief should let me filter by segment
/closedloop:send-feedback <feedback in any language>
```

## What to do

1. **Build the `content`** — the user's point PLUS the relevant context from this conversation: what they were doing in ClosedLoop AI, what triggered the feedback, the behavior or error they saw. Use only real context from the conversation; don't invent. Strip PII (names, emails, customer data).
2. **Translate to English** if it isn't already — faithfully, no summarizing.
3. **Send** — call `send_closedloop_feedback(content="{...}")` directly, no confirmation. Then tell the user it was sent, in one line.

If `send_closedloop_feedback` isn't in your tools, the ClosedLoop AI MCP isn't connected — tell the user to run `claude mcp add --transport http closedloop-ai https://mcp.closedloop.sh`, then restart and `/mcp` → authorize.

## Rules

- **Real context only** — include what actually happened in the conversation; never invent a bug, quote, or detail.
- **No PII in `content`** — strip names, emails, customer data.
- **English only** — translate if needed, faithfully.
- **Just send it** — no preview or approve step.
- **One piece of feedback per call.**

## Not this

- **Not for logging your own customers' feedback.** That flows in through your connected sources (Gong, Intercom, surveys, …) and the read skills (`/closedloop:deep-dive`, `/closedloop:weekly-brief`) surface it. This skill only tells the ClosedLoop team about ClosedLoop AI.
