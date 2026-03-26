---
name: "closedloop:weekly-brief"
description: "Weekly product intelligence brief from ClosedLoop AI. Reads ALL evidence behind every spike, deal blocker, churn risk, and competitor mention — then synthesizes into a 40-line brief a CPO can scan in 60 seconds. Use when the user asks for a weekly brief, weekly summary, weekly update, or what happened this week."
---

# /closedloop:weekly-brief

Generate a weekly intelligence brief. Reads everything, synthesizes to ~40 lines. Every claim is backed by evidence you actually read.

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

## How it works

Thousands of insights go in. A 40-line brief comes out. The reader never sees the raw inputs — only the judgment, backed by evidence you actually read.

This is NOT a dashboard. It's an intelligence brief. Every line carries a judgment call because you read the underlying data.

## Execution

### Step 1: Detect timezone and compute UTC dates

The MCP stores all dates in UTC. The user sees local time. The skill must bridge both.

**Detect local timezone:**
Run: !`date +%Z` to get the timezone abbreviation (e.g., "EDT", "CET").
Run: !`date -u +%Y-%m-%dT%H:%M` and !`date +%Y-%m-%dT%H:%M` — the difference tells you the UTC offset.

**Compute date boundaries:**
- `this_week`: last 7 days ending today. Example: if today is Tue Mar 25, this week = Mar 19 - Mar 25.
- `last_week`: the 7 days before that. Example: Mar 12 - Mar 18.
- Convert to UTC for MCP parameters: midnight local → UTC offset. ET (UTC-4): midnight Mar 19 ET = Mar 19 04:00 UTC.
- For MCP `date_from`/`date_to`, send the UTC-adjusted YYYY-MM-DD.

**When displaying dates to the user:**
- Show the range in the header: "Mar 19 - Mar 25, 2026"
- Convert UTC dates from MCP responses to local time. A source_date of "2026-03-20T03:00:00Z" in ET shows as "Mar 19" (Thursday night), not "Mar 20."

### Step 2: Launch 4 agents in parallel

**Agent 1: Numbers**

MCP calls:
- `get_overview(time_range="7d")`
- `get_facets(dimensions=["category", "feature_area", "source_type"], date_from="{this_week_start}")`
- `get_facets(dimensions=["category", "feature_area", "source_type"], date_from="{last_week_start}", date_to="{last_week_end}")`
- `get_competitors()`

Compute:
- This week vs last week: total insights, unique customers, deal blockers, churn risks
- Source split: how many from support vs calls (this week and last week)
- Category deltas (% change per category)
- Feature area deltas (% change per feature area)
- Identify ALL categories and feature areas that spiked >30%

Write to `/tmp/wb-numbers.md`:
- Headline numbers with deltas
- Source split: support vs calls with deltas
- Full category table with deltas
- Full feature area table with deltas
- List of spikes (>30%) that need investigation
- Competitor mention counts

**Agent 2: Urgent Items**

MCP calls:
- `search_insights(is_deal_blocker=true, date_from="{this_week_start}", limit=20)`
- `search_insights(is_churn_risk=true, date_from="{this_week_start}", limit=20)`
- `get_insight(id)` for EVERY deal blocker and churn risk
- `search_signals(type="churn_reason", date_from="{this_week_start}", limit=20)`
- `get_signal(id)` for EVERY churn_reason signal

After reading all details, write to `/tmp/wb-urgent.md`:
- For each deal blocker: customer name, one-sentence summary of what's blocked and why, severity
- For each churn risk: customer name, one-sentence summary, severity
- For each churn signal: customer name, urgency level, one-sentence summary
- Group related items (e.g., 3 issues from same customer = 1 entry)
- Your judgment: which are the most critical and why (you read everything, now rank them)

**Agent 3: Spike Investigation**

Wait for Agent 1 to identify spikes, OR independently run these (the most common spikes are predictable from the feature areas):

For EACH of the top 5 feature areas this week, search BOTH sources separately:
- `search_insights(feature_area="{area}", source_type="support", date_from="{this_week_start}", sort="severity", limit=30)`
- `search_insights(feature_area="{area}", source_type="calls", date_from="{this_week_start}", sort="severity", limit=30)`
- `get_insight(id)` for the top 15 by severity from each source

For EACH category that spiked >30%, same split:
- `search_insights(category="{cat}", source_type="support", date_from="{this_week_start}", sort="severity", limit=20)`
- `search_insights(category="{cat}", source_type="calls", date_from="{this_week_start}", sort="severity", limit=20)`
- `get_insight(id)` for the top 10 by severity from each source

After reading all these insights, write to `/tmp/wb-spikes.md`:
- For each spike: what's driving it FROM SUPPORT (what's breaking) vs FROM CALLS (what customers are asking for)
- One-sentence interpretation per spike that names both sides: "Integrations (248): 180 from support — OTA sync failures and automated partner errors. 68 from calls — operators asking for new connections and better reseller controls."
- Identify if automated sources (OTA errors, partner bots) inflate the support numbers
- Identify if a single onboarding call inflates the calls numbers
- Note cross-spike patterns (same customers appearing in multiple spikes)

**Agent 4: Competitive + Notable Voices**

MCP calls:
- `search_signals(type="competitor_mention", date_from="{this_week_start}", limit=30)`
- `get_signal(id)` for EVERY competitor mention
- `search_insights(sort="frustration", date_from="{this_week_start}", limit=20)`
- `search_signals(type="satisfaction", date_from="{this_week_start}", limit=10)`
- `get_signal(id)` for satisfaction signals

For the 2 most compelling quotes found, load the actual conversation for full context:
- `list_conversations(customer_name="{customer}", source_type="calls", limit=1)` — find the call
- `get_conversation(id="{id}", source="{source}")` — load the transcript
- Read the conversation around the quote to get 2-3 sentences of context (what was said before/after)

After reading everything, write to `/tmp/wb-voices.md`:
- Each competitor mentioned this week: name, which customer, what they said, whether it's a threat or an opportunity
- Your judgment: which competitive mentions are most actionable?
- Top 2 most vivid customer quotes with full conversation context (not just the extracted snippet — the actual back-and-forth from the call)
- Any notable positive signals worth mentioning

### Step 3: Assemble the brief

Read all 4 files. You now have:
- The numbers and what spiked (Agent 1)
- Every deal blocker and churn risk in full detail (Agent 2)
- The real story behind every spike (Agent 3)
- Competitive context and best quotes (Agent 4)

Now write the brief. Every line should carry judgment because you read the evidence.

## Output format

```
================================================================================
  WEEKLY BRIEF                                      {date_range}
================================================================================

{4-6 line executive summary. Written LAST, after you've read everything.
This is the "if you read nothing else" section. State what happened this
week in plain language. Name the biggest risks. Name the biggest changes.
No numbers — just the story.}

NUMBERS
-------
  Insights: {n} ({+/-x%})  |  Customers: {n}  |  Blockers: {n}  |  Churn: {n}

ATTENTION
---------
  {Each urgent item gets exactly 2 lines: customer name + what happened.
  Grouped by type. Max 5 items — if more exist, pick the most critical.}

  {customer} -- {one sentence: what's blocked/broken and the business impact}
  {customer} -- {one sentence}
  ...

WHAT'S DRIVING THE NUMBERS
--------------------------
  {This is the section that makes the brief valuable. For each notable
  change this week, explain WHY — and separate what's breaking (support)
  from what customers are asking for (calls). This distinction is critical:
  support = operational health, calls = strategic direction.}

  {Area}: {N from support — what's broken}. {N from calls — what they want}.
  {Area}: {explanation with source split}
  ...

VOICES
------
  "{One killer quote}" -- {customer}
  "{Another quote, different theme}" -- {customer}

COMPETITIVE
-----------
  {Only if competitors were mentioned this week. 1-2 lines per competitor.
  Omit entirely if none.}

  {Competitor}: {what was said, by whom, and whether it's a threat or opportunity}

================================================================================
```

## The executive summary

This is the most important part. It goes at the top but you write it LAST — after reading all 4 agent files. It should read like a news lede:

Good example:
"Rough week on the support side — two critical outages took down ticket sales and POS payments. An upcoming go-live is blocked by import gaps. But the calls tell a different story: feature requests surged (+49%) as operators ramp up for season, asking for membership management and dynamic pricing. The fix-vs-build tension is real: 66% of this week's volume is support fires, 34% is strategic product demand."

Bad example:
"This week there were 1,423 insights from 258 customers. There were 3 deal blockers and 7 churn risks. Categories that spiked include..."

The good example tells a story. The bad example reads data.

## Data quality: clean before you count

When reading insights, silently exclude noise and report only real human feedback:

- **Automated/bot-generated insights:** If you see insights where the reporter is an email address (not a person name), the content is a system error template repeated identically across many entries, or the same error message appears 10+ times with only a product ID changed — exclude these from your counts and analysis. These are machine-generated alerts, not customer feedback.
- **Over-extracted calls:** If you find 10+ insights from the same speaker in the same call that are clearly variations of 3-4 topics (similar titles, same theme), count them as the distinct topics, not the raw insight count. "15 insights about 3 topics" = 3 topics from that customer.
- **Don't mention the noise.** The reader doesn't need to know about data quality artifacts. Just present the clean picture. If a category shows 248 raw insights but 125 are automated templates, report the real number (~120 from real customers) without explaining the inflation.

## Rules

- **40-50 lines total.** Hard cap 55. If you can't fit it, your sentences are too long.
- **Every claim is backed by evidence you read.** Never say "integrations spiked" without knowing why.
- **No raw numbers without interpretation.** "+54%" alone is banned. "+54% — OTA sync failures across 8 customers" is required.
- **No jargon.** No RIC scores, frustration floats, kano categories. Business language.
- **Never show raw frustration scores.** Interpret the 0-1 number into plain language: 0-0.2 = calm, 0.2-0.4 = mild frustration, 0.4-0.6 = moderate frustration, 0.6-0.8 = high frustration, 0.8-1.0 = extreme frustration.
- **Group related items.** 3 bugs from the same customer = 1 entry, not 3.
- **Omit empty sections.** No competitors this week? Skip the section entirely.
- **Exact numbers.** "47" not "45+".
- **2 quotes max.** Pick for specificity and vividness. Different themes.
- **Executive summary is the whole brief for 80% of readers.** Design it to stand alone.
- **Quiet weeks are short.** If nothing spiked, nothing urgent, say "Stable week" and show 25 lines.
