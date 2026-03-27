---
name: "closedloop:ship-notify"
description: "Find every customer who asked for something you just shipped, generate personalized outreach per customer. Closes the feedback loop — the thing 95% of companies fail to do."
---

# /closedloop:ship-notify

You shipped a feature. Now find every customer who asked for it and generate personalized outreach — referencing their own words, not a generic changelog.

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

## Input handling

The PM describes what they shipped in plain language.

```
/closedloop:ship-notify we shipped bulk CSV export for all report types
/closedloop:ship-notify SSO with SAML is now live
/closedloop:ship-notify redesigned the onboarding flow for new teams
```

The skill uses the description to search semantically — it does not require exact keyword matches with past requests.

## Execution

### Step 1: Expand the search

Take the PM's feature description and generate 3-5 alternative phrasings that customers might have used when requesting it. Customers don't use product language — they describe problems.

Example: "bulk CSV export" → also search for "download all data", "export reports", "get data out of the system", "batch download"

### Step 2: Launch 3 agents in parallel

**Agent 1: Find all customers who requested this**

For the primary description AND each alternative phrasing:
- `search_insights(query="{phrasing}", limit=50)`

Merge all results, deduplicate by insight ID. This is the master list.

For each unique insight:
- `get_insight(id)` — read full content, pain_point, workaround, customer_name, reporter_name, frustration_score, is_deal_blocker, is_churn_risk, source_date

Filter out false positives: use judgment to discard insights where the customer was talking about something unrelated that happened to match keywords.

Group insights by customer_name. For each customer, extract:
- Number of times they mentioned it
- Date range (earliest to latest)
- Most compelling verbatim quote (highest frustration, most specific)
- Whether it was flagged as deal_blocker or churn_risk
- Any workaround they described

Write to `/tmp/ship-notify/customers.md`:
- Deduplicated customer list with per-customer summary
- Total: N customers across N insights

**Agent 2: CRM enrichment**

For each unique customer from Agent 1:
- `search_customers(query="{customer_name}", limit=1)`
- `get_customer(id)` — full profile

Extract per customer:
- Segment, industry, country
- Deal value (won + pipeline)
- Deal stage (closed-won, evaluation, churned, etc.)
- Key contacts with titles and emails
- Churn risk indicators

Write to `/tmp/ship-notify/crm.md`:
- Per-customer CRM profile
- Sorted by deal value descending

**Agent 3: Competitive and strategic context**

- `search_signals(query="{feature_description}", limit=30)` — find any competitive mentions, purchase hesitations, or decision criteria related to this feature
- `get_signal(id)` for the most relevant results

Extract:
- Competitors mentioned alongside this feature gap
- Purchase hesitations citing this gap
- Win reasons where having a related capability helped
- Decision criteria that reference this capability

Write to `/tmp/ship-notify/strategic.md`:
- Competitor context (if any)
- Lost deals where this was cited as a factor

### Step 3: Prioritize into tiers

Read all 3 agent files. Assign each customer to a priority tier:

| Tier | Criteria | Action |
|---|---|---|
| **P0 — Deal unblockers** | is_deal_blocker=true OR deal_stage is evaluation/negotiation | CSM personally reaches out within 24h |
| **P1 — High-value existing** | deal_stage=closed-won AND high deal value or enterprise segment | Personalized email referencing their specific quote |
| **P2 — Active customers** | deal_stage=closed-won, lower value | Personalized email, can be batch-sent |
| **P3 — At-risk / churned** | deal_stage=churned OR is_churn_risk=true | Win-back email referencing "we heard you" |
| **P4 — Prospects** | deal_stage in evaluation/trial/lost | Sales enablement brief for AE |

### Step 4: Generate outreach

For each tier, generate draft messages.

## Output format

```
SHIP NOTIFY: {feature description}
==========================================================================

SUMMARY
  {N} customers asked for this across {N} insights.
  {N} deal blockers | {N} churn risks | {N} churned accounts
  Total revenue affected: ${amount} (won) + ${amount} (pipeline)

==========================================================================

P0 — DEAL UNBLOCKERS ({N} customers)
{These need personal CSM outreach within 24 hours.}

  {Customer Name} — {Segment} — ${deal_value} ({deal_stage})
  Contact: {name}, {title}, {email}
  Asked {N} times, first on {date}. Deal blocker.
  Their words: "{most compelling verbatim quote}"

  DRAFT MESSAGE:
  Subject: {Feature} is live — {personalized reference to their request}

  Hi {contact_first_name},

  {Reference their specific request in their own words from the quote
   above. Confirm the feature is live. Link to it. One sentence on what
   it does for them specifically. Thank them. Ask for feedback.}

  {3-5 sentences max. Not a changelog. A personal note.}

---

P1 — HIGH-VALUE CUSTOMERS ({N} customers)

  {Customer Name} — {Segment} — ${deal_value}
  Their words: "{quote}"
  Workaround they used: {workaround if any}

  DRAFT MESSAGE:
  Subject: {Personalized — reference their pain or workaround}
  {Same structure as P0 but can be slightly less personal.}

---

P2 — ACTIVE CUSTOMERS ({N} customers)

  {Grouped by what they specifically asked for. One template per group.}

  Group: "{sub-need}" ({N} customers: {names})
  Template:
  Subject: You asked for {capability} — it's live
  {Short, references the group's common need. Link to feature.}

---

P3 — WIN-BACK ({N} customers)
{Churned or at-risk. Different tone: "we heard you and built it."}

  {Customer Name} — churned {date} — was ${deal_value}
  Their words: "{quote from before they left}"

  DRAFT MESSAGE:
  Subject: We built what you asked for
  {Acknowledge they left. Reference their specific feedback. Show what
   changed. Invite them to re-evaluate. No pressure.}

---

P4 — SALES ENABLEMENT ({N} prospects)
{Internal brief for AEs, not customer-facing.}

  {Customer Name} — {deal_stage} — ${deal_value}
  They asked about: {capability}
  Quote: "{what they said during evaluation}"
  Talking point: "{How to bring this up proactively in the next call}"

==========================================================================

COMPETITIVE CONTEXT
{Only if competitors were mentioned alongside this feature gap.}

  {Competitor}: mentioned by {N} customers as having this capability.
  "{Most relevant quote}" — {customer}
  Implication: {What this means for positioning now that you've shipped it}

WHAT TO DO NEXT
  1. P0 customers: CSM outreach within 24 hours
  2. P1 customers: send personalized emails this week
  3. P2 customers: batch send next Tuesday-Thursday, 10am-2pm
  4. P3 customers: send win-back sequence starting next week
  5. P4 prospects: forward briefs to assigned AEs today

==========================================================================
```

## Rules

- **Their words, not yours.** Every draft message references the customer's own verbatim quote or described pain point. Never generic "we're excited to announce."
- **One feature per run.** The skill handles one shipped feature at a time. For multiple features, run multiple times.
- **Revenue-weighted priority.** P0-P4 tiers are driven by deal value and stage, not by how loudly they asked.
- **Draft, not send.** The skill generates draft messages. The PM/CSM reviews and sends. Never claim messages were sent.
- **False positive filtering.** Not every search result is a real match. Use judgment to exclude insights where the customer was talking about something else that happened to match keywords. When in doubt, exclude.
- **Timing guidance.** Outreach should happen 3-5 days after deployment (not same-day — bugs). Tuesday-Thursday mid-morning gets highest engagement.
- **Win-back tone is different.** P3 messages acknowledge the customer left and invite re-evaluation. No pressure, no guilt. "We heard your feedback and acted on it."
- **Sales enablement is internal.** P4 output is a brief for the AE, not a customer-facing message.
- **Group P2 by sub-need.** 30 customers don't each get a unique email. Group by what they specifically asked for (reporting export vs data migration vs archival) and generate one template per group.
- **Never show raw frustration scores.** Interpret: calm, mild, moderate, high, extreme.
- **Omit empty tiers.** No deal blockers? Skip P0. No churned customers? Skip P3. The output gets shorter when there's less to do.

## Data quality

- Silently exclude automated/bot-generated insights
- Deduplicate: same customer mentioning the same need multiple times = one entry with count
- When multiple contacts at the same company asked, pick the most senior for outreach
- Support ticket noise doesn't count as a "feature request"

## What this skill does NOT do

- **Does not send messages.** Generates drafts for human review.
- **Does not match automatically.** Semantic search finds candidates; the PM confirms relevance.
- **Does not handle "we built something different."** If you shipped an alternative solution to the requested feature, frame that manually. The skill finds exact and close matches, not lateral solutions.
- **Does not track delivery.** No email sending, no open rate tracking. Use your email/CRM tools for that.
- **Does not replace a changelog.** This is targeted outreach to requesters, not a public announcement. Run this AND update your changelog separately.
