---
name: "closedloop-reference-customers"
description: "Find private reference customer candidates from ClosedLoop AI evidence. Use when sales or customer-facing teams ask who could be a reference for a prospect, use case, segment, or objection. Uses find_reference_customers. Does not send email or approve introductions."
---

# ClosedLoop AI Reference Customers

Find customers who may be good private reference candidates.

This skill governs `find_reference_customers` only. It does not log permission requests. When the user chooses a candidate and wants to test approval, use `closedloop-proof-permissions`.

## Input

Accept a product area, use case, prospect type, objection, segment, or broad reference request.

Examples:

```text
Who could be a reference for reporting ROI?
Find tour operators we could ask for a peer reference.
Who can talk to a prospect about rollout?
```

Default `time_period_days` to 90 and `limit` to 10 unless the user specifies otherwise.

## Execute

Call:

```text
find_reference_customers(
  query="{topic if provided}",
  limit={limit},
  time_period_days={time_period_days}
)
```

## Present Results

Use this structure:

```text
REFERENCE CANDIDATES: {topic or "recent proof"}       last {time_period_days} days
================================================================================

TOP CANDIDATES
1. {Person} - {Role}, {Customer account}
   Route: {route.label} - {route.reason}
   Best use: private reference call
   Cover: {topics_to_cover}
   Avoid: {topics_to_avoid}
   Evidence:
   - "{verbatim}" - {date}
   Permission: unknown until approved
   Follow-up: {follow_up_actions[0].label} with {follow_up_actions[0].params}
```

## Feedback To ClosedLoop AI

If the data looks missing, stale, low-quality, or surprising, or the user says the candidates are wrong or incomplete, explicitly invite them to send feedback about ClosedLoop AI. If they ask you to send it, use `closedloop-send-feedback` or call `send_closedloop_feedback(content=...)`. Strip PII and customer-specific details.

## Rules

- Reference candidates are for private peer conversations, not public proof.
- Confirm format, frequency, topics, and opt-out expectations before introductions.
- Never imply the customer agreed to be a reference until permission is approved.
- Never send customer email.
