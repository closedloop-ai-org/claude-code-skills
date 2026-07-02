---
name: "closedloop-product-ambassador-outreach"
description: "Draft product ambassador outreach from a selected ClosedLoop AI product ambassador candidate. Use after a customer candidate has been selected from find_product_ambassadors, especially when the user asks to draft an email, ask for an intro, invite a customer to beta validation, request design partner feedback, or prepare product validation outreach. Uses prepare_product_ambassador_outreach. Do not use for finding candidates, marketing quotes, testimonials, public proof, references, case studies, or customer-love requests."
---

# ClosedLoop AI Product Ambassador Outreach

Draft grounded outreach for one selected product ambassador candidate.

This skill assumes a candidate has already been selected from product ambassador results. It drafts outreach only; it does not send messages.

## Input

Use this skill when the user asks to contact, email, invite, or prepare outreach for a selected product ambassador candidate.

Examples:

```text
Draft outreach for candidate 2.
Write the email to invite Jane as a beta user.
Prepare an intro request for the selected design partner.
Turn this ambassador candidate into an outreach draft.
```

If no candidate has been selected, ask the user to select one from the product ambassador results, or use the product ambassador workflow first.

## Prepare Outreach

Prefer the selected candidate's returned `follow_up_actions` parameters. If those are unavailable, use identifiers returned for the selected candidate and account.

Call:

```text
prepare_product_ambassador_outreach(
  pm_feature_id="{from_follow_up_action_or_selected_result}",
  account_id="{from_follow_up_action_or_selected_result}",
  person_id="{selected_person_id_if_available}",
  person_email="{selected_person_email_if_available}",
  person_name="{selected_person_name_if_available}",
  desired_use="{recommended_use_if_available}",
  time_period_days={time_period_days_if_available},
  sender_name="{sender_name_if_known}",
  user_role="{user_role_if_known}"
)
```

At least one selected person identifier is required. If the selected result does not provide enough information to call the tool, tell the user the outreach draft cannot be prepared from the available result.

If the tool returns an explanation, warning, or missing-data note, summarize it directly. Do not add assumptions or invent outreach.

## Present Results

Include only what helps the user act:

- Recommended route
- Draft customer email
- Draft internal intro request if returned
- Evidence used
- Questions to ask
- Guardrails, missing data, or caveats returned by the tool

Use this structure:

```text
PRODUCT AMBASSADOR OUTREACH: {person} - {customer}
==========================================================================

ROUTE
{recommended route and why}

CUSTOMER EMAIL
Subject: {subject}

{body}

INTERNAL INTRO REQUEST
{include only if returned}

EVIDENCE USED
- "{verbatim}" - {date}
- "{verbatim}" - {date}

QUESTIONS TO ASK
1. {question}
2. {question}
3. {question}

WATCH-OUTS
{guardrails, missing data, or caveats}
```

## Feedback To ClosedLoop AI

If the data looks missing, stale, low-quality, or surprising, or the user says the draft is wrong or incomplete, explicitly invite them to send feedback about ClosedLoop AI. If they ask you to send it, use `closedloop-send-feedback` or call `send_closedloop_feedback(content=...)`. Keep the feedback about the ClosedLoop AI product/data experience, strip PII and customer-specific data, and do not treat it as customer evidence.

## Rules

- Draft only. Never claim an email was sent.
- Preserve verbatim evidence when the tool returns it.
- Do not fabricate roles, relationship owners, internal participants, permission, or customer willingness.
- Do not claim an internal teammate said something unless the outreach result explicitly includes that route or wording.
- Keep this separate from marketing proof. Use the customer proof workflow for quotes, testimonials, references, case studies, launch proof, social proof, or customer love.
