---
name: "closedloop-product-ambassadors"
description: "Find product ambassador candidates from ClosedLoop AI evidence. Use when a product manager, product leader, or founder wants customers for design partnership, beta validation, workflow discovery, expert review, internal championing, or feature feedback for a product area or feature. Uses find_product_ambassadors. Do not use for drafting outreach, marketing quotes, testimonials, case studies, launch proof, references, social proof, or customer-love requests."
---

# ClosedLoop AI Product Ambassadors

Find customers a product team should involve for a product area or feature, then propose the right next action.

This is for product discovery and validation, not public marketing proof.

## Input

Accept a feature, product area, workflow, or product initiative in plain language.

Examples:

```text
Find product ambassadors for memberships.
Find beta users for API exports from the last 180 days.
Who should we invite as design partners for the booking engine?
```

If the user gives no product scope, ask:

```text
Which feature, product area, or workflow should I find product ambassadors for?
```

Map the user's intent to `desired_use`:

| User intent | `desired_use` |
|---|---|
| design partner, discovery, co-design, shape solution | `design_partner` |
| beta, early access, validation, test with users | `beta_user` |
| champion, stakeholder buy-in, rollout help | `internal_champion` |
| expert review, critique, power user, domain review | `expert_reviewer` |
| unclear or broad request | `all` |

Default `time_period_days` to 90 unless the user specifies a different window. Default `limit` to 20 unless the user asks for a different count.

## Find Candidates

Call:

```text
find_product_ambassadors(
  query="{feature_or_product_area}",
  desired_use="{desired_use}",
  limit={limit},
  time_period_days={time_period_days}
)
```

If the tool returns no candidates, an explanation, warnings, or suggested alternatives, summarize that response directly. Do not add assumptions or invent candidates.

## Present Results

Show candidates in priority order. Include only what helps the user act:

- Person and customer
- Recommended use
- Suggested ask or recommended action
- Why they are a fit
- 1-3 verbatim evidence excerpts
- Warnings or caveats from the result
- Follow-up actions returned by the tool

Use this structure:

```text
PRODUCT AMBASSADORS: {query}                  last {time_period_days} days
==========================================================================

SUMMARY
{N} candidates found. Best uses: {design/beta/champion/expert/etc.}

1. {Person} - {Role}, {Customer}
   Best use: {recommended_use}
   Action: {recommended_action or suggested_ask}
   Why: {short evidence-based reason}
   Evidence:
   - "{verbatim}" - {date}
   - "{verbatim}" - {date}
   Watch-outs: {warnings or "none surfaced"}
   Next: {best follow-up action, or use closedloop-product-ambassador-outreach to draft outreach}

NEXT STEPS
1. Pick 3-5 candidates for the first outreach wave.
2. Use design partners for problem and solution shaping before beta.
3. Use beta users only when there is something concrete to validate.
4. Use expert reviewers for workflow critique, not public advocacy.
5. Ask each customer for one specific action.
```

## Outreach Hand-Off

If the user selects a candidate and asks to draft outreach, use the `closedloop-product-ambassador-outreach` skill. Pass along the selected candidate, returned follow-up action, and time period from this result.

## Feedback To ClosedLoop AI

If the data looks missing, stale, low-quality, or surprising, or the user says the candidates are wrong or incomplete, explicitly invite them to send feedback about ClosedLoop AI. If they ask you to send it, use `closedloop-send-feedback` or call `send_closedloop_feedback(content=...)`. Keep the feedback about the ClosedLoop AI product/data experience, strip PII and customer-specific data, and do not treat it as customer evidence.

## Rules

- Use product language: "product insights", "customers", and "evidence".
- Keep product ambassador work separate from marketing proof. Use the customer proof workflow for quotes, testimonials, references, case studies, launch proof, social proof, or customer love.
- Preserve verbatim evidence with every recommendation.
- Do not fabricate roles, relationship owners, internal participants, permission, or customer willingness.
- Do not draft outreach in this skill. Use the product ambassador outreach workflow after the user selects a candidate.
