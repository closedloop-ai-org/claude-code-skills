---
name: "closedloop-customer-proof"
description: "Find marketing-ready customer proof from ClosedLoop AI evidence. Use when marketing, product marketing, sales enablement, CMO, CEO, or leadership asks for quotes, testimonials, case-study candidates, customer love, launch proof, ROI/value proof, adoption stories, social proof, or reference candidates. Uses find_customer_proof. Do not use for permission outreach drafts; hand selected candidates to closedloop-customer-proof-outreach."
---

# ClosedLoop AI Customer Proof

Find customers and verbatim evidence that marketing can turn into proof: website quotes, testimonials, sales proof, case studies, launch quotes, customer love, ROI proof, adoption stories, social proof, or live reference candidates.

This skill governs discovery only. It does not draft outreach. When the user chooses a candidate or asks for a permission email, use `closedloop-customer-proof-outreach`.

The `proof_type` parameter is a marketing intent, not a raw evidence type. The tool ranks real ClosedLoop AI evidence including satisfaction, value evidence, adoption milestones, social proof, product-market-fit evidence, win reasons, and aha moments.

## Input

Accept a topic, product area, feature, initiative, value theme, or broad proof request.

Examples:

```text
Find customer quotes about memberships.
Find case study candidates for API exports.
Find ROI proof for reporting from the last 180 days.
Show recent customer love.
```

If no topic is provided, browse strongest recent proof.

Map intent to `proof_type`:

| User intent | `proof_type` |
|---|---|
| quote, testimonial, website quote | `website_quote` |
| case study, story | `case_study` |
| ROI, value, savings, business impact | `roi_proof` |
| launch quote, release proof | `launch_quote` |
| love, happy customers, praise | `customer_love` |
| reference, logo, social proof | `social_proof` |
| adoption, rollout, usage story | `adoption_story` |
| unclear or broad request | `all` |

Default `time_period_days` to 90 unless the user specifies a different window. Default `limit` to 50 unless the user asks for a different count.

## Execute

When a topic is provided, call:

```text
find_customer_proof(
  query="{topic}",
  proof_type="{proof_type}",
  limit={limit},
  time_period_days={time_period_days}
)
```

When no topic is provided, call:

```text
find_customer_proof(
  proof_type="{proof_type}",
  limit={limit},
  time_period_days={time_period_days}
)
```

Do not manually stitch lower-level searches. The tool ranks candidates, joins person/account detail, returns verbatim evidence, recommends one of four usage scopes, excludes inactive or unresolved customer accounts, and includes follow-up actions.

The four `recommended_usage_scope` values are:

| Scope | Meaning |
|---|---|
| `website` | Public website quote, wall of love, homepage, testimonial page, or customer page. |
| `sales` | Sales decks, follow-up emails, sales collateral, or prospect conversations handled by the vendor team. |
| `case_study` | Interview, ROI validation, named customer story, or written/video case study. |
| `live_reference` | Customer directly participates in reference activity such as an email intro, short call, webinar, analyst/media reference, or similar. |

If the tool returns no candidates, an explanation, warnings, excluded candidates, or suggested alternatives, summarize that response directly. Do not add assumptions or invent proof.

## Present Results

Show strongest proof candidates first. Include only what helps the user act:

- Person and customer account
- Recommended usage scope and percentage scores
- Suggested ask or recommended action
- Why this is strong proof
- 1-3 verbatim evidence excerpts
- Permission status or permission caveat from the result
- Warnings, exclusions, or caveats from the result
- Follow-up action label and params when present

Use this structure:

```text
CUSTOMER PROOF: {query or "recent proof"}       last {time_period_days} days
==========================================================================

SUMMARY
{N} usable proof candidates. Best fit: {quotes/case studies/ROI/etc.}

TOP PROOF CANDIDATES
1. {Person} - {Role}, {Customer account}
   Best use: {recommended_usage_scope} ({usage_scope_scores})
   Action: {recommended_action or suggested_ask}
   Why: {short evidence-based reason}
   Evidence:
   - "{verbatim}" - {date}
   - "{verbatim}" - {date}
   Permission: {permission status or "ask before public use"}
   Watch-outs: {warnings or "none surfaced"}
   Follow-up: {follow_up_actions[0].label} with {follow_up_actions[0].params}

DO NOT USE PUBLICLY YET
{Excluded candidates and reasons returned by the tool.}

NEXT STEPS
1. Pick the strongest 3-5 candidates by usage scope and evidence specificity.
2. Ask for explicit permission before using any quote publicly.
3. For case studies, ask for a short discovery call before requesting approval.
4. For ROI proof, validate the metric with the customer before publishing.
5. Route PM design partner or beta requests to the product ambassador workflow.
```

## Handoff To Outreach

If the user chooses a candidate or asks for a draft, stop using this skill and use `closedloop-customer-proof-outreach`.

Pass the selected candidate's `follow_up_actions[0].params` to `prepare_customer_proof_outreach`; those params include the recommended `usage_scope`. Add `sender_name` or `user_role` only when the user provides them.

## Feedback To ClosedLoop AI

If the data looks missing, stale, low-quality, or surprising, or the user says the candidates are wrong or incomplete, explicitly invite them to send feedback about ClosedLoop AI. If they ask you to send it, use `closedloop-send-feedback` or call `send_closedloop_feedback(content=...)`. Keep the feedback about the ClosedLoop AI product/data experience, strip PII and customer-specific data, and do not treat it as customer evidence.

## Rules

- Use this workflow for marketing proof, public evidence, sales enablement proof, and customer-love requests.
- Keep customer proof separate from PM design partner, beta, workflow discovery, and product validation workflows.
- Preserve verbatim evidence with every recommendation.
- Treat willingness to advocate as askability, not permission.
- Never imply public permission unless the result explicitly says permission is known.
- Do not fabricate roles, relationship owners, permission, or customer willingness.
- Do not draft outreach in this skill. Draft only through `closedloop-customer-proof-outreach`.
