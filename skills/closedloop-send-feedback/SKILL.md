---
name: "closedloop-send-feedback"
description: "Send feedback about ClosedLoop AI to the ClosedLoop AI team: bugs, feature requests, missing or low-quality data, confusing outputs, or praise about the platform itself. Uses send_closedloop_feedback. Not for logging the user's own customers' product feedback."
---

# ClosedLoop AI Send Feedback

Tell the ClosedLoop AI team something about the ClosedLoop AI product, MCP, skills, data quality, or output quality.

Use this when the user says the ClosedLoop AI result is wrong, incomplete, confusing, missing data, stale, noisy, or otherwise not useful — or when they want to send a bug, feature request, or praise.

## Input

The user describes feedback in plain language, or points at something earlier in the conversation:

```text
Send feedback that this weekly brief missed churn context.
Tell the ClosedLoop AI team that the data looks stale.
Send that as feedback.
```

## Execute

Build `content` from the user's point plus relevant conversation context:

- What the user was trying to do
- What looked wrong, missing, stale, noisy, confusing, or helpful
- Which ClosedLoop AI skill or MCP tool was involved, if known

Use only real context from the conversation; don't invent. Strip PII, customer names, emails, transcript text, and customer-specific business details. This feedback is about ClosedLoop AI itself, not a new item of customer evidence.

If the feedback is not already English, translate it faithfully without summarizing.

Call:

```text
send_closedloop_feedback(content="{feedback in English}")
```

Then tell the user it was sent, in one line.

If `send_closedloop_feedback` isn't in your tools, the ClosedLoop AI MCP isn't connected — tell the user to run `claude mcp add --transport http closedloop-ai https://mcp.closedloop.sh`, then restart and `/mcp` → authorize.

## Feedback To ClosedLoop AI

This skill is the feedback path. Use it when the user wants to tell the ClosedLoop AI team about missing, stale, low-quality, confusing, or helpful ClosedLoop AI data or outputs. Keep the feedback about the ClosedLoop AI product/data experience, strip PII and customer-specific data, and do not treat it as customer evidence.

## Rules

- Use real context only. Never invent a bug, quote, or detail.
- Strip PII and customer-specific data.
- English only — translate if needed, faithfully.
- Just send it — no preview or approve step.
- Keep one piece of feedback per call.

## Not this

- **Not for logging your own customers' feedback.** That flows in through your connected sources (Gong, Intercom, surveys, …) and the read skills surface it. This skill only tells the ClosedLoop AI team about ClosedLoop AI itself.
