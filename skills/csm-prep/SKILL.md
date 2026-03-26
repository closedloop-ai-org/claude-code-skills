---
name: "closedloop:csm-prep"
description: "90-second pre-call intelligence brief for CSMs and account managers. One opinionated headline, landmines, what changed, their top concerns in their own words, open threads, and how many other customers share the same pain. Not a data dump — a judgment call."
---

# /closedloop:csm-prep

90-second pre-call intelligence brief for CSMs and account managers. Walk into any customer call knowing the one thing that matters most, what was promised last time, and what landmines to avoid — without opening 5 tabs.

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

One argument: customer name or domain. The skill resolves it.

```
/closedloop:csm-prep Acme Corp
/closedloop:csm-prep acme.com
```

If `search_customers(query="{input}")` returns multiple matches, show a numbered list and ask the user to pick one. If no match, say so and show the closest alternatives.

## Execution

### Step 1: Resolve the customer

```
search_customers(query="{input}")
```

Pick the match with the highest `insight_count`. Record `customer_id`, `name`, `domain`.

### Step 2: Launch 5 agents in parallel

All agents receive the `customer_id` and `name`.

**Agent 1: Profile + CRM + deals**

- `get_customer(id)` — full profile, deals, contacts, feedback summary, strategic signals
- Extract: company profile (industry, segment, country, employees), key contacts (top 5 by seniority), active deals (open only), won revenue, account owner

Write to `/tmp/customer-prep/profile.md`:
- Account snapshot line: name, segment, country, revenue, deal count
- Key contacts: name, title (max 5)
- Active deals: name, stage, amount, close date (max 3)
- Account health numbers: insight_count, deal_blocker_count, churn_risk_count, avg_frustration

**Agent 2: Landmines (deal blockers + churn risks)**

- `search_insights(customer_id="{id}", is_deal_blocker=true, limit=10)`
- `search_insights(customer_id="{id}", is_churn_risk=true, limit=10)`
- `get_insight(id)` for each — read full content

For each landmine, extract: title, severity, verbatim quote, reporter name, date.
Deduplicate: if the same issue is both a deal blocker and churn risk, show once with both labels.

Write to `/tmp/customer-prep/landmines.md`:
- Max 3 landmines, ranked by severity then recency
- Each: label (DEAL BLOCKER / CHURN RISK), title, severity, verbatim quote, reporter, date

**Agent 3: Recent feedback + what changed**

- `search_insights(customer_id="{id}", sort="recency", limit=20)`
- `get_insight(id)` for the top 10 by severity

Group by topic/feature_area. For each topic:
- Count of insights
- Most vivid verbatim quote
- Severity and frustration level
- Date range (is this ongoing or a one-time mention?)

Identify "what changed": insights from the last 30 days that represent NEW topics not present in older feedback. These are the deltas.

Write to `/tmp/customer-prep/feedback.md`:
- Top 3 concerns ranked by severity x frequency x recency
- Each: topic, count, quote, speaker, date
- "What changed" section: new topics from last 30 days only

**Agent 4: Last 2 conversations + open threads**

- `list_conversations(customer_id="{id}", source_type="calls", limit=5)`
- `get_conversation(id, source)` for the 2 most recent calls — load full transcripts

Read each transcript and extract:
- What was discussed (3-5 key topics)
- What the customer asked for
- What was promised by your team (commitments, follow-ups, timelines)
- Any unresolved questions or open items
- Who was on the call

Also check support:
- `list_conversations(customer_id="{id}", source_type="support", limit=5)`
- Read the 1-2 most recent support conversations if they exist

Write to `/tmp/customer-prep/conversations.md`:
- Per conversation: date, title, participants, 3-5 line summary
- Open threads: list of unresolved items with who committed and when
- Support context: any active support issues

**Agent 5: Strategic signals + pattern context**

- `search_signals(customer_id="{id}", limit=30)` — all strategic intelligence

For strategic signals, group by type:
- Satisfaction: most recent level and quote
- Competitor mentions: which competitors, most recent quote
- Decision criteria: what they evaluate
- Churn signals: urgency and reason

For pattern context — check if this customer's top 2-3 pain points are shared:
- `search_insights(query="{top_concern_1}", limit=5)` — WITHOUT customer_id filter, to see how many OTHER customers report the same issue
- `search_insights(query="{top_concern_2}", limit=5)` — same
- `search_insights(query="{top_concern_3}", limit=5)` — same
- From the `customers_mentioned` field in each response, count how many unique customers reported similar issues

Write to `/tmp/customer-prep/strategic.md`:
- Per signal type: most recent signal with quote (only types that have data)
- Competitor context (only if mentioned in last 90 days)
- Pattern context: "Their concern about {X} was also reported by {N} other customers including {names}" or "This concern appears specific to this account"

### Step 3: Assemble the brief

Read all 5 files. Write the brief following the output format below.

**The headline is written LAST** — after reading all evidence. It is an opinionated one-sentence judgment about this account's current state and the single most important thing to know.

## Output format

```
CUSTOMER PREP: {Company Name}                               {today's date}
==========================================================================

{THE HEADLINE — one opinionated sentence. Not a summary of data. A judgment.
 What is the story of this account right now? What's the one thing that
 would change how you walk into this call?
 Examples:
 - "Stable $250K account but terminal reliability is eroding trust — 23 churn signals, all operational."
 - "New $50K deal at risk — they're evaluating a competitor and raised pricing twice in the last month."
 - "Happy power user with 3 expansion signals. This is a growth call, not a save call."}

ACCOUNT
  {name} | {segment} | {country} | ${won_revenue} won | ${pipeline} open
  {insight_count} insights | {blocker_count} blockers | {churn_count} churn risks
  Frustration: {interpreted level} | Last interaction: {date}

CONTACTS
  {Name} — {Title}
  {Name} — {Title}
  {Name} — {Title}
  {max 5, most senior first}

{If active deals exist:}
DEALS
  {deal_name} — {stage} — ${amount} — closes {date}

================================================================================

LANDMINES
{Only if deal_blockers > 0 or churn_risks > 0. Otherwise omit entirely.}

  {DEAL BLOCKER / CHURN RISK}: {title} ({severity})
  "{verbatim quote}" — {reporter}, {date}

  {Max 3. These are the things that could blow up in the call.}

WHAT CHANGED (last 30 days)
{Only new topics, usage shifts, or risk signals since last interaction.
 If nothing changed: "No new themes since last interaction on {date}."}

  - {New topic or change}: "{quote}" — {speaker}, {date}

THEIR TOP CONCERNS (in their own words)
{Top 3 topics ranked by severity x frequency x recency. Customer voice only.}

  1. {topic} ({n} mentions, {severity}):
     "{most vivid verbatim quote}" — {speaker}, {date}

  2. {topic} ({n} mentions):
     "{quote}" — {speaker}, {date}

  3. {topic} ({n} mentions):
     "{quote}" — {speaker}, {date}

LAST CONVERSATIONS
{2 most recent. Summary, not transcript. What was discussed and what was left open.}

  {date} — {title} ({source})
  {Who was there. What was discussed in 3-5 lines. What was promised.
   What's still open.}

  {date} — {title} ({source})
  {Same format.}

OPEN THREADS
{Commitments from conversations that have not been resolved.
 Frame as preparation, not blame. "Committed Jan 15" not "OVERDUE 70 DAYS".}

  - {What was promised}: committed by {who} on {date}
  - {What was promised}: committed by {who} on {date}
  {If nothing is clearly open, omit this section.}

PATTERN CONTEXT
{Is this customer's pain unique or shared across the customer base?}

  "{top concern}": also reported by {N} other customers including {customer names}.
  "{second concern}": also reported by {N} other customers.
  {If unique: "This concern appears specific to this account."}

{Only if competitor data exists in last 90 days:}
COMPETITIVE
  {competitor_name}: mentioned {n} times. "{most recent quote}" — {date}

==========================================================================
```

## Rules

- **Never show raw frustration scores.** Interpret the 0-1 number into plain language: 0-0.2 = calm, 0.2-0.4 = mild frustration, 0.4-0.6 = moderate frustration, 0.6-0.8 = high frustration, 0.8-1.0 = extreme frustration.
- **250-400 words.** This is a 90-second brief, not a report. If the output exceeds 50 lines, cut the weakest section.
- **BLUF — headline first.** The headline is an opinionated judgment written LAST, shown FIRST. If the reader stops after one sentence, they have the most important thing.
- **Evidence, not labels.** Show "3 open tickets, NPS dropped 8→4" not "Customer: Frustrated." Labels anchor and create bias.
- **What changed, not everything.** If nothing is new in the last 30 days, say "stable" — don't rehash old themes.
- **Customer voice only.** Every concern backed by a verbatim quote. No paraphrasing, no invented sentiment.
- **3 concerns max.** Paradox of choice — 10 talking points means 0 get used. 3 means 2-3 get used.
- **Open threads as preparation, not blame.** "Committed Jan 15" — never "OVERDUE" or "FAILED."
- **Pattern context is mandatory.** Even if the answer is "unique to this account" — say so. This is the section no other tool provides.
- **Omit empty sections.** No landmines? Skip the section entirely. No competitors? Skip it. No open threads? Skip it. The brief gets shorter for healthy accounts — that IS the signal.
- **Thin accounts get short briefs.** If a customer has <5 insights and no calls, show the account snapshot + CRM data and note: "Limited feedback history. {N} insights on record." Don't pad.

## Data quality

- Silently exclude automated/bot-generated insights
- Deduplicate: same customer, same topic, same call = one mention
- Support ticket noise (password resets, generic errors) doesn't count as a "concern"
- If the same issue is both deal blocker and churn risk, count it once, label both

## What this skill does NOT do

- **Does not replace the deep-dive.** Customer-prep is 90 seconds. For full evidence on a topic, run `/closedloop:deep-dive {topic}`.
- **Does not build a persona.** For understanding how a customer thinks and talks, use `/closedloop:synthetic-customer {name}`.
- **Does not prioritize across customers.** This is one customer's brief. For portfolio-level intelligence, use `/closedloop:weekly-brief`.
- **Does not generate a slide deck or QBR doc.** It's a pre-call scan, not a presentation.
