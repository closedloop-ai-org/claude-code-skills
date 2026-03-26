---
name: "closedloop:competitor-gap"
description: "Competitive intelligence from your actual customer conversations. Shows what customers say about each competitor, where you're winning, where you're losing, and what's at stake commercially. Not desk research — real customer voice with deal context."
---

# /closedloop:competitor-gap

Competitive intelligence from what your customers actually say in their calls and support tickets — not desk research, not review sites. Real voice, real quotes, real deal impact.

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

- No argument → full landscape with quarterly trends (default: last 4 quarters)
- One competitor name → drill into that specific competitor
- Two competitor names → head-to-head comparison
- `monthly` / `weekly` → change the trend period (last 4 months or last 4 weeks)

```
/closedloop:competitor-gap                         → full landscape, quarterly trends
/closedloop:competitor-gap monthly                 → full landscape, monthly trends
/closedloop:competitor-gap Acme Corp                → drill into Acme Corp
/closedloop:competitor-gap Acme Corp vs Beta Inc    → head-to-head
```

## Execution

### Step 1: Get the landscape and compute time windows

```
get_competitors()
```

This returns all tracked competitors with total mention counts.

Compute 4 time periods based on the user's granularity (default: quarterly):
- **Quarterly** (default): Q-3, Q-2, Q-1, current quarter (e.g., Q3'25, Q4'25, Q1'26, Q2'26)
- **Monthly**: M-3, M-2, M-1, current month
- **Weekly**: W-3, W-2, W-1, current week

Calculate the start/end dates for each period. These boundaries are passed to Agent 1 for per-period counting.

### Step 2: Launch 3 agents in parallel

**Agent 1: Competitor signals + threat scoring + trend computation**

For each competitor with mentions > 0:
- `search_signals(type="competitor_mention", competitor_name="{name}", limit=50)`
- `get_signal(id)` for every signal — read the full content

For each signal, classify the INTENT:
- **Evaluating**: customer is considering the competitor ("we're looking at X")
- **Switching from**: customer came from this competitor ("we used to use X")
- **Switching to**: customer is threatening to leave for this competitor ("we might move to X")
- **Comparing features**: customer names a specific capability difference ("X does this but you don't")
- **Frustrated with competitor**: customer complains about the competitor (opportunity for us)
- **Praising competitor**: customer says competitor does something well (threat)

**Count mentions per time period.** Using each signal's date, bucket into the 4 time windows computed in Step 1. This gives a 4-column trajectory per competitor.

**Compute trend word** from the 4-period trajectory:
- **accelerating**: increasing across 3+ periods, or sharp spike in latest period
- **stable**: roughly flat (±20% variation across periods)
- **cooling**: decreasing across 3+ periods
- **new**: zero mentions before the latest 1-2 periods
- **gone**: mentions only in older periods, none in the latest period

Cross-reference with CRM data:
- `search_customers(query="{customer_name}")` for each customer who mentioned a competitor
- Get their deal value, deal stage, segment, churn risk status

Compute a threat score per competitor:
- Switching-to mentions weighted highest
- Deal value of affected accounts
- Churn risk flags on those accounts
- Recency (recent mentions > old ones)
- Trend direction (accelerating = higher threat)

Write to `/tmp/competitor-analysis/signals.md`:
- Ranked threat table with 4-period counts: competitor, P1, P2, P3, P4 (current), total, threat score, trend, top customer
- Per-competitor: intent breakdown, affected customers with CRM data, all verbatim quotes

**Agent 2: Feature gaps from feedback**

- `search_insights(query="{competitor_name}", limit=30)` for each top competitor
- `get_insight(id)` for each — read full content, especially `competitor_gap` field

Also:
- `search_signals(type="decision_criteria", limit=30)` — what customers evaluate when choosing
- `search_signals(type="competitive_positioning", limit=20)` — how customers position you vs alternatives

Group feature gaps by theme (pricing, integrations, UX, API, support, etc.)

Write to `/tmp/competitor-analysis/gaps.md`:
- Per-competitor feature gap list with customer quotes
- Market-level decision criteria (not per-competitor)
- Your advantages: where customers say you're better (from win reasons, value evidence)

**Agent 3: Conversation context for highest-stakes mentions**

For the top 3 most commercially impactful competitor mentions (highest deal value + switching-to or churn risk):
- `list_conversations(customer_id="{id}", source_type="calls", limit=3)`
- `get_conversation(id, source)` — load the transcript
- Read the conversation around where the competitor was discussed

Write to `/tmp/competitor-analysis/transcripts.md`:
- Per conversation: customer name, deal value, 5-10 lines of actual dialogue around the competitor mention
- Context: what was discussed before and after

### Step 3: Assemble the output

Read all 3 files. Write the competitive intelligence brief.

## Output format

```
COMPETITIVE LANDSCAPE
=====================
Based on {N} competitor mentions across {N} customers.
Period: {granularity} ({P1 label} → {P4 label})

THREAT RANKING
--------------
  #  Competitor       {P1}  {P2}  {P3}  {P4}  Total  Threat  Trend
  1. {name}            35    23    18    12     88    HIGH    cooling
  2. {name}             0     2     6    11     19    MEDIUM  accelerating
  3. {name}             5     4     6     5     20    LOW     stable
  ...
  {Competitors with 1-2 total mentions: one line, no drill}

  Top signal: {competitor} — "{intent}" from {customer} (${deal})

================================================================================

{For top 3 competitors, auto-drill:}

## {Competitor Name}                                        THREAT: {HIGH/MEDIUM/LOW}
   {Mentions}: {n} from {n} customers | Trend: {trend} ({P1}: {n} → {P4}: {n})

   THREAT ASSESSMENT
   {2-3 sentence synthesis: what's happening with this competitor in your
   customer base. Who's talking about them, in what context, and what's
   at stake commercially.}

   WHAT THEY DO BETTER (from your customers' mouths)
   - {Feature gap}: "{verbatim quote}" -- {customer} ({deal value})
   - {Feature gap}: "{quote}" -- {customer}
   {Group by theme if multiple gaps}

   WHAT WE DO BETTER
   - {Advantage}: "{verbatim quote}" -- {customer}
   - {Advantage}: "{quote}" -- {customer}
   {If no explicit win reasons found, note: "No explicit advantages cited
   against this competitor in the data."}

   WHO'S TALKING
   | Customer | Revenue | Stage | Intent | Quote |
   |----------|---------|-------|--------|-------|
   | {name} | ${rev} | {stage} | switching-to | "{short quote}" |
   | {name} | ${rev} | {stage} | comparing | "{short quote}" |

   FROM THE CALL
   {For the highest-stakes mention, show 5-10 lines of actual conversation:}
   > [timestamp] [EXT] {speaker}: {what they said about the competitor}
   > [timestamp] [INT] {your team}: {how they responded}
   > [timestamp] [EXT] {speaker}: {follow-up}

================================================================================

DECISION CRITERIA (market-level)
--------------------------------
What customers evaluate when choosing — across all competitors:
- {criterion}: cited by {n} customers. "{representative quote}"
- {criterion}: cited by {n} customers. "{quote}"
...

YOUR ADVANTAGES (across all competitors)
-----------------------------------------
What customers say you do better than alternatives:
- {advantage}: "{quote}" -- {customer}
- {advantage}: "{quote}" -- {customer}
{If no advantages found: "No explicit win reasons in the data. Consider
 running search_signals(type='win_reason') or search_signals(type='value_evidence')
 for positive evidence."}

================================================================================
```

## Rules

- **Customer voice only.** Every claim must come from what a customer said, not from desk research about the competitor. If nobody mentioned a competitor's feature, don't invent it.
- **Fact-Impact-Act.** For every gap: what was said (fact), why it matters commercially (impact), what to do about it (the reader decides the act — we provide the evidence).
- **"What we do better" is mandatory.** Never produce a competitive brief that only shows weaknesses. If you can't find explicit advantages, say so — don't skip the section.
- **Intent matters more than volume.** 3 "switching-to" mentions from $200K accounts are more dangerous than 30 "comparing features" mentions from free-tier users.
- **Thin evidence gets one line.** Competitors with 1-2 mentions appear in the threat table with their quote inline. No separate drill section.
- **Trends as one word.** Accelerating / stable / cooling / new / gone. Computed from the 4-period trajectory, not just current vs previous. A competitor going 0→2→6→11 is "accelerating" even if 11 seems low.
- **Load transcripts selectively.** Maximum 3 transcripts total — only for deal blockers, churn risks, or the most vivid comparison moments.
- **Anti-paranoia guardrail.** Every feature gap in the output should be traceable to a customer asking for it, not just a competitor shipping it. If customers don't care about a competitor's feature, it doesn't belong in this brief.
- **120-150 lines.** Enough depth for the top 3 competitors plus landscape. Not a 50-page report.

## Data quality

- Silently exclude automated/bot-generated insights
- Deduplicate: same customer mentioning same competitor in same call = one mention, not N
- Don't inflate mention counts with support ticket noise

## What this skill does NOT do

- **Does not research competitors externally.** Only shows what YOUR customers say. For external research, the user can ask separately.
- **Does not recommend "build this because competitor has it."** Shows the gap and the commercial impact. The PM decides if it's worth building.
- **Does not compare feature-by-feature.** That commoditizes the conversation. Shows thematic gaps and advantages instead.
