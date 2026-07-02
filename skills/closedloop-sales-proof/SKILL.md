---
name: "closedloop-sales-proof"
description: "Build sales proof packets from ClosedLoop AI evidence. Use when sales, sales enablement, marketing, founders, or leadership need customer examples, proof points, snippets, talk tracks, or follow-up copy for prospect conversations. Uses find_sales_proof. Does not send email or claim permission."
---

# ClosedLoop AI Sales Proof

Build a sales proof packet from real customer evidence.

This skill governs `find_sales_proof` only. It does not log permission requests. When the user chooses a proof packet and wants to test approval, use `closedloop-proof-permissions`.

## Input

Accept a prospect concern, product area, segment, outcome, competitor objection, or broad sales-proof request.

Examples:

```text
Give me sales proof for reporting ROI.
Find proof points for museums worried about reconciliation.
Show customer examples I can use in a follow-up email.
```

Default `time_period_days` to 90 unless the user specifies a different window. Default `limit` to 10 unless the user asks for a different count.

## Execute

Call:

```text
find_sales_proof(
  query="{topic if provided}",
  limit={limit},
  time_period_days={time_period_days}
)
```

Do not manually stitch lower-level searches. The tool returns sales packets, proof points, evidence, permission caveats, and a follow-up action for the permission workflow.

## Present Results

Use this structure:

```text
SALES PROOF: {topic or "recent proof"}       last {time_period_days} days
=======================================================================

BEST PACKETS
1. {Person} - {Role}, {Customer account}
   Fit: {fit_score}
   Talk track: {sales_talk_track}
   Proof points:
   - "{proof_points[0].text}" - {date}
   Caveat: {permission note}
   Follow-up: {follow_up_actions[0].label} with {follow_up_actions[0].params}

NEXT STEP
Pick the proof point you want to test, then log a fake permission email with closedloop-proof-permissions.
```

## Feedback To ClosedLoop AI

If the data looks missing, stale, low-quality, or surprising, or the user says the proof is wrong or incomplete, explicitly invite them to send feedback about ClosedLoop AI. If they ask you to send it, use `closedloop-send-feedback` or call `send_closedloop_feedback(content=...)`. Strip PII and customer-specific details.

## Rules

- Use only the returned evidence.
- Preserve verbatim proof points when quoting evidence.
- Treat proof as sales-enablement material only until permission is approved.
- Never imply the customer agreed to public proof or reference participation.
- Never send customer email.
