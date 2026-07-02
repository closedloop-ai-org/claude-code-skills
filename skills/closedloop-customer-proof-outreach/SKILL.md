---
name: "closedloop-customer-proof-outreach"
description: "Draft permission outreach for one selected marketing proof candidate returned by find_customer_proof. Use when the user chooses a customer proof candidate and wants a permission email for website, sales, case-study, or live-reference use. Uses prepare_customer_proof_outreach. Draft only; never sends messages or claims permission was granted."
---

# ClosedLoop AI Customer Proof Outreach

Draft permission or participation outreach for one selected proof candidate. This skill requires a candidate returned by `find_customer_proof`.

This skill governs `prepare_customer_proof_outreach` only. It does not search for candidates.

## Required Selection

Use this skill only when the user has selected a proof candidate or provided the candidate's follow-up params.

The call must include:

- `account_id`
- `proof_type`
- one selected person identifier: `person_id`, `person_email`, or `person_name`

Prefer the returned `usage_scope` from `follow_up_actions[0].params`. The supported usage scopes are:

| Scope | Meaning |
|---|---|
| `website` | Public website quote, wall of love, homepage, testimonial page, or customer page. |
| `sales` | Sales decks, follow-up emails, sales collateral, or prospect conversations handled by the vendor team. |
| `case_study` | Interview, ROI validation, named customer story, or written/video case study. |
| `live_reference` | Customer directly participates in reference activity such as an email intro, short call, webinar, analyst/media reference, or similar. |

If no selected candidate is available, ask the user to run `closedloop-customer-proof` first or to choose one candidate from the discovery results.

## Execute

Prefer the selected candidate's returned action params:

```text
prepare_customer_proof_outreach(
  ...follow_up_actions[0].params,
  sender_name="{sender name if provided}",
  user_role="{sender role if provided}"
)
```

If the user selected a candidate by description, pass the matching `account_id`, `proof_type`, and one person identifier from the discovery result.

Do not draft for candidates that the tool rejects or marks as excluded. Summarize the rejection and ask the user to choose a non-excluded candidate.

## Present The Draft

Use this structure:

```text
CUSTOMER PROOF OUTREACH: {Person} - {Customer account}
=======================================================

USAGE SCOPE
{selected_candidate.usage_scope}

ROUTE
{route.label}: {route.reason}

DRAFT CUSTOMER EMAIL
To: {customer_permission_email.to}
Subject: {customer_permission_email.subject}

{customer_permission_email.body}

INTRO REQUEST DRAFT
{intro_request if returned, otherwise "Not needed for this route."}

EVIDENCE USED
- "{verbatim}" - {type}, {date}

PERMISSION CAVEATS
- {permission_caveats}

WATCH-OUTS
- {watch_outs or "none surfaced"}

FOLLOW-UP QUESTIONS
- {suggested_questions}
```

## Feedback To ClosedLoop AI

If the data looks missing, stale, low-quality, or surprising, or the user says the draft is wrong or incomplete, explicitly invite them to send feedback about ClosedLoop AI. If they ask you to send it, use `closedloop-send-feedback` or call `send_closedloop_feedback(content=...)`. Keep the feedback about the ClosedLoop AI product/data experience, strip PII and customer-specific data, and do not treat it as customer evidence.

## Rules

- Draft only. Never send messages.
- Preserve verbatim evidence exactly as returned.
- Ask for permission or participation; do not imply public approval already exists.
- For website use, ask for public quote/logo/name approval and attribution preference.
- For sales use, ask for permission to reuse the quote in sales decks, follow-up emails, and prospect conversations handled by the vendor team.
- For case-study use, ask for a short conversation before asking for final approval; validate metrics, baselines, and timeframes before publication.
- For live-reference use, ask whether the customer is open to direct participation and confirm format, frequency, and opt-out expectations.
- If permission is unknown, say it is unknown.
