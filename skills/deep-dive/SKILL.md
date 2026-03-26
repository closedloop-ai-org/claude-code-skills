---
name: "closedloop:deep-dive"
description: "Deep-dive into any topic against ALL customer evidence from ClosedLoop AI. Reads every matching insight and signal, looks up CRM data for affected customers, and synthesizes the complete picture — what customers say, how severe it is, what revenue is at stake, what competitors are doing, and what workarounds exist."
---

# /closedloop:deep-dive

Deep-dive into any topic against all customer feedback, strategic intelligence, and CRM data from ClosedLoop AI. Reads everything. Synthesizes it. You decide what to do with it.

## When to use

- "What do customers say about checkout flow?"
- "Is there real demand for API rate limits?"
- "What's the evidence around dashboard reliability?"
- "Deep-dive into dashboard loading issues"
- Validating a roadmap item before committing engineering time
- Preparing evidence for a stakeholder discussion
- Understanding a problem area before writing a spec

## Check ClosedLoop AI MCP is available

Before doing anything, try calling `get_overview(time_range="all")`.

**If the call fails or the tool is not found:**

```
ClosedLoop AI MCP is not connected. This skill needs it to access your customer feedback data.

Set it up in 30 seconds:

  claude mcp add --transport http closedloop-ai https://mcp.closedloop.sh

Then restart Claude Code, type /mcp, select closedloop-ai, and authorize.

Full guide: https://closedloop.sh/docs/mcp-server/overview
```

Then stop.

**If it succeeds:** Note total insights, customers, date range. If total insights = 0, tell the user to connect a data source first. If < 100, warn results may be incomplete.

## Input handling

**If the user provides ONE topic:** Proceed directly to deep-dive.

**If the user provides MULTIPLE topics:**
Present them as a numbered list and ask which one to investigate first. After finishing one, ask "Want me to deep-dive the next one?"

## Deep-dive execution

### Step 1: Gather ALL matching evidence

No limits. Get everything.

**Search insights (product feedback):**
```
search_insights(query="{topic}", limit=100, sort="relevance")
```
If 100 results returned, paginate with offset=100 and continue until exhausted.

**Search strategic signals:**
```
search_signals(query="{topic}", limit=100, sort="relevance")
```
Same pagination.

### Step 2: Read FULL details for every match

For EVERY insight ID: `get_insight(id="{id}")`
For EVERY signal ID: `get_signal(id="{id}")`

Do NOT skip this. Search results return 300-char truncated previews. You need full verbatim content, pain_point, workaround, competitor_gap, entities_competitors, emotion, frustration_score, kano_category, job_statement, is_deal_blocker, is_churn_risk, and for signals: intelligence_type, competitor_name, churn_urgency, satisfaction_level, quantified_impact, signal_strength.

Read in parallel batches to save time.

### Step 3: Look up CRM data for affected customers

Collect all unique `customer_name` values from insights and signals.

For each unique customer (or top 20-30 by mention count): `search_customers(query="{customer_name}", limit=1)`

This returns data that `get_insight` does NOT include:
- Company profile: industry, country, employee_count, annual_revenue, segment
- Deals: amount, stage, is_won/is_closed, pipeline
- Deal blockers, churn risks, frustration for this company

From this compute: total revenue affected, won deal value, open pipeline at risk, industry breakdown, segment breakdown, size breakdown, geography.

**If CRM data is sparse:** Say so. "CRM data not available for most customers. Revenue analysis not possible."

### Step 4: Load key conversations for full context

After reading all insights and signals, identify the 3-5 most important ones (highest severity, deal blockers, churn risks, or most compelling quotes). For each:

1. `list_conversations(customer_name="{customer_name}", source_type="calls", limit=3)` — find the actual call where this was said
2. `get_conversation(id="{conversation_id}", source="{source}")` — load the full transcript

Read the conversation around the relevant quote. This gives you:
- What was discussed before and after — the full context
- The back-and-forth between customer and your team
- Other topics from the same call that may be related
- The tone and urgency that a 1-sentence extraction can't capture

Only do this for the top 3-5 insights. Loading every transcript would be excessive — the extracted insights cover most of the picture. The transcripts add depth where it matters most.

### Step 5: Read everything, THEN write

Do not start writing after reading 10 insights. Read ALL of them first — insights, signals, CRM data, and the key transcripts. The synthesis quality depends on seeing the full picture.

## Output format

Lead with synthesis. Evidence supports, not leads.

```
DEEP DIVE: {Topic}
===================

THE REAL PROBLEM
----------------
{3-5 sentence synthesis written AFTER reading ALL evidence. What is the
underlying pain? Why does it matter? How do different customers experience
it? If there are distinct sub-problems, name them here.}

{If sub-problems exist:}
This breaks into {N} distinct sub-problems:
1. **{Sub-problem}** ({N} customers): {one sentence}
2. **{Sub-problem}** ({N} customers): {one sentence}
...

EVIDENCE STRENGTH
-----------------
{exact number} insights + {exact number} signals from {exact number} customers
Data range: {earliest date} to {most recent date}
Trend: {growing/stable/declining} ({last 60 days count} vs {prior 60 days count})
{If < 10 customers: "Limited evidence -- may be noise, not a pattern."}
{If > 50 customers: "Broad evidence across the customer base."}

Severity: {exact counts} Critical, {n} High, {n} Medium, {n} Low
Deal blockers: {n} ({customer names and deal amounts if known})
Churn risks: {n} ({customer names if known})
Avg frustration: {interpreted level, e.g. "moderate" or "high"}

REVENUE IMPACT
--------------
{Only if CRM data exists. If not, say "CRM not connected -- no revenue data."}

Won revenue from affected customers: ${amount} across {n} companies
Open pipeline at risk: ${amount} from {n} companies
{List top 5 affected accounts: name, revenue, segment, what they said}

{If no CRM: skip this section entirely, don't show empty fields}

WHAT CUSTOMERS SAY
------------------
{Group by sub-theme if they exist. For each theme, show 3-5 most
compelling verbatim quotes with attribution.}

**{Sub-theme}** ({n} customers)
- "{Exact verbatim quote}" -- {customer_name} ({segment/industry/size if known})
- "{Exact verbatim quote}" -- {customer_name}
- "{Exact verbatim quote}" -- {customer_name}
{and {N} more said similar things}

**{Another sub-theme}** ({n} customers)
- ...

FULL CONVERSATION CONTEXT
-------------------------
{For the 2-3 most critical insights (deal blockers, churn risks, or most
vivid quotes), show a longer excerpt from the actual conversation transcript.
This gives the reader the back-and-forth, not just the extracted quote.}

**{customer_name}** ({source}, {date}):
> {3-5 lines of the actual conversation around the key moment,
> including what was said before and after. Speaker labels included.}

{If no transcripts were loaded, omit this section entirely.}

WORKAROUNDS
-----------
{What customers do today. Workarounds = the problem is real enough to invest
effort. No workaround = either not critical or truly blocking.}
- {customer}: "{what they do}"
- {customer}: "{what they do}"
{If none: "No workarounds mentioned."}

COMPETITIVE CONTEXT
-------------------
{Only if competitors are mentioned in the evidence.}
- {Competitor}: mentioned by {n} customers. "{what they say}"
- ...
{Decision criteria customers cite, if present}
{If none: "No competitors mentioned in this context."}

STRATEGIC SIGNALS
-----------------
{Group by type. Only show types that have matches.}
Satisfaction ({n}): "{quote}" -- {customer}
Churn signals ({n}): "{quote}" -- {customer}
Decision criteria ({n}): "{quote}" -- {customer}
Competitor mentions ({n}): "{quote}" -- {customer}

CUSTOMERS AFFECTED
------------------
| Customer | Revenue | Segment | Industry | Mentions | Deal Blocker | Deals |
|----------|---------|---------|----------|----------|--------------|-------|
| {name} | ${rev} | {segment} | {industry} | {n} | {yes/no} | {stage} |
| ... |

WHAT WE DON'T KNOW
-------------------
{Explicitly call out evidence gaps. This builds trust.}
- {e.g., "No closed-lost deals attributed to this -- unclear if deals were
  lost or if attribution is missing"}
- {e.g., "No product usage data -- we know what customers SAY but not
  how they USE the feature"}
- {e.g., "Evidence is 80% from support tickets -- may overrepresent
  frustrated users vs. satisfied ones"}
```

## What this skill does NOT do

- **Does not prioritize.** We only see one topic. Can't rank it against things we haven't investigated. Run deep-dives on multiple topics and compare.
- **Does not score or grade.** 47 customers and 5 deal blockers IS the score.
- **Does not recommend build/don't build.** We show evidence. You weigh it against engineering cost, strategy, capacity, and everything else we can't see.

## What this skill DOES do

- **Shows everything.** Every matching quote, signal, and data point.
- **Synthesizes.** Reads all evidence, writes what the real underlying problem is, groups by sub-themes.
- **Adds revenue and CRM context.** Looks up every affected customer — revenue, deals, segment, industry, size.
- **Surfaces what's hidden.** Workarounds, competitor mentions, churn signals, deal blockers — things only visible when you read ALL evidence together.
- **Is honest about gaps.** Calls out what the evidence doesn't cover.

## Data quality: clean before you count

When reading insights, silently exclude noise and report only real human feedback:

- **Automated/bot-generated insights:** If you see insights where the reporter is an email address (not a person name), the content is a system error template repeated identically across many entries, or the same error message appears 10+ times with only a product ID changed — exclude these from your counts and analysis.
- **Over-extracted calls:** If you find 10+ insights from the same speaker in the same call that are clearly variations of 3-4 topics, count them as the distinct topics, not the raw insight count.
- **Don't mention the noise.** Just present the clean picture.

## Guidelines

- **Never show raw frustration scores.** Interpret the 0-1 number into plain language: 0-0.2 = calm, 0.2-0.4 = mild frustration, 0.4-0.6 = moderate frustration, 0.6-0.8 = high frustration, 0.8-1.0 = extreme frustration.
- **Read everything before writing anything.** Synthesis quality depends on the full picture.
- **Quote verbatim.** Exact customer words. Never paraphrase.
- **Attribute every quote.** Customer name + company context if CRM data available.
- **Use exact numbers.** Never "45+" — say "47." Precision builds trust.
- **Group intelligently.** 40 insights about the same thing? Pick 3-5 best quotes, note "and {N} more said similar things."
- **Flag contradictions.** Some customers want X, others don't? Call it out.
- **Note source distribution only if it reveals something.** "90% from support" = support burden. "90% from sales calls" = prospect blocker. If the split is unremarkable, skip it.
- **Be honest about thin evidence.** 2 customers? Say "limited evidence."
- **Be honest about missing data.** No CRM? Say so. Don't show empty sections.
- **Never fabricate.** Only present what MCP tools return.
- **Synthesis first, data second.** "THE REAL PROBLEM" is the most important section. It goes at the top.
