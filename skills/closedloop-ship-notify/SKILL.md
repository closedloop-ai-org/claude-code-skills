---
name: "closedloop-ship-notify"
description: "Find every customer who asked for something you just shipped, then draft personalized launch follow-up. Uses find_launch_audience. Draft only; never sends customer email."
---

# ClosedLoop AI Ship Notify

Find the customers who asked for a shipped feature and draft launch follow-up that references what they actually said.

This skill governs `find_launch_audience` only. It does not send messages, create CSM notifications, create permission requests, or write sent-email logs.

## Input

Accept one shipped feature, opportunity, or PM feature at a time.

Examples:

```text
We shipped bulk CSV export. Who asked for it and what should we tell them?
Find launch audience for opportunity_id=...
SAML SSO is live. Draft follow-up for customers who asked for it.
```

Prefer exact ids when available:

- `opportunity_id` for the shipped ClosedLoop AI opportunity.
- `pm_feature_id` for the PM feature linked to a shipped opportunity.
- `query` only when ids are not available.

Default `limit` to 20 unless the user asks for a different count. Default `time_period_days` to all available linked evidence unless the user specifies a shorter window.

## Execute

Call:

```text
find_launch_audience(
  opportunity_id="{id if available}",
  pm_feature_id="{id if available}",
  query="{plain-language shipped feature if ids are unavailable}",
  limit={limit},
  time_period_days={time_period_days},
  sender_name="{sender name if provided}",
  user_role="{sender role if provided}",
  feature_url="{feature or changelog URL if provided}"
)
```

Use one scope input. Prefer `opportunity_id`, then `pm_feature_id`, then `query`.

## Present Results

Use this structure:

```text
SHIP NOTIFY: {resolved_scope.title}
====================================

Status: shipped
Sent: no
Customers found: {summary.total_customers}
Insights found: {summary.total_insights}

P0 - DEAL UNBLOCKERS
1. {person.name}, {person.job_title}, {account.name}
   Route: {recommended_route.label}
   Why: {why}
   Evidence: "{evidence[0].verbatim}"

   Draft:
   To: {draft_message.to}
   Subject: {draft_message.subject}

   {draft_message.body}

P1 - HIGH-VALUE CUSTOMERS
...

P2 - ACTIVE CUSTOMERS
...

P3 - WIN-BACK CANDIDATES
...

P4 - SALES ENABLEMENT
...

Safety:
- No email was sent.
- No notification or sent-email record was written.
- A human should review and send manually.
```

Omit empty tiers. Keep the no-send safety line visible.

## Feedback To ClosedLoop AI

If the data looks missing, stale, low-quality, or surprising, or the user says the requester matches, tiers, routes, evidence, or drafts are wrong or incomplete, explicitly invite them to send feedback about ClosedLoop AI. If they ask you to send it, use `closedloop-send-feedback` or call `send_closedloop_feedback(content=...)`. Keep the feedback about the ClosedLoop AI product/data experience, strip PII and customer-specific data, and do not treat it as customer evidence.

## Rules

- Use only the returned `find_launch_audience` evidence and drafts.
- Never send customer email.
- Never claim outreach was sent.
- Never call `create_proof_permission_request` for launch follow-up unless the user explicitly switches to proof-permission testing.
- Never call write/send notification routes.
- Keep customer-facing draft language natural; do not put internal safety notes inside the customer email body.
- Preserve verbatim evidence when quoting the customer.
- If the feature is not shipped or no shipped opportunity resolves, say that and stop.
- For P4 sales enablement, treat the output as internal AE context unless a human chooses to send a customer note.
