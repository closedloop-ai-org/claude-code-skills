---
name: "closedloop:pm-prep"
description: "Pre-call discovery brief for product managers. Not account health — learning goals, knowledge gaps, data-grounded questions, and whether this customer's pain is a market signal or an outlier. Turns a customer call into a research instrument."
---

# /closedloop:pm-prep

Pre-call discovery brief for product managers. Not "here's what this customer said before" — but "here's what you can learn from this call, what you already know from other customers, and what questions to ask."

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

Always starts with a company name. Person selection happens in a second step.

```
/closedloop:pm-prep Acme Corp
```

The skill resolves the company, runs the full brief, and shows a numbered contact list at the end. The user can then pick names to get per-person prep added.

If `search_customers(query="{input}")` returns multiple matches, show a numbered list and ask the user to pick one. If no match, say so.

## Execution

### Step 1: Resolve the customer and get the baseline

```
search_customers(query="{input}")
get_overview(time_range="all")
```

Pick the match with highest `insight_count`. Record `customer_id`, `name`, `segment`, `industry`.
From overview, record `unique_customers` — this is the denominator for relative positioning.

### Step 2: Launch 5 agents in parallel

**Agent 1: What they're trying to do (workflow + outcomes + workarounds)**

- `get_customer(id)` — full profile, feedback summary, strategic signals
- `search_insights(customer_id="{id}", sort="recency", limit=20)` — recent feedback
- `get_insight(id)` for the top 10 — read full content

For each insight, extract:
- The **underlying need** (not the feature request). Reframe: "requested Slack integration" → "needs alerts without switching tools"
- Any **workarounds** described — these prove the need is real. Note the sophistication: spreadsheet hack (mild) → custom tool (critical) → hired a person (budget exists)
- The **emotion** and **frustration score** — high usage + high frustration = trapped customer
- Group by underlying need/theme, not by category

Write to `/tmp/pm-prep/workflow.md`:
- Top 3-5 underlying needs, each with: the need (outcome-framed), evidence count, most vivid quote, workarounds if any, frustration level
- Feature requests translated to outcomes
- Workarounds listed separately with sophistication level

**Agent 2: What we know from others (relative positioning)**

For the customer's top 3 concern topics (from Agent 1's themes):
- `search_insights(query="{topic_1}", limit=5)` — WITHOUT customer_id filter
- `search_insights(query="{topic_2}", limit=5)` — WITHOUT customer_id filter
- `search_insights(query="{topic_3}", limit=5)` — WITHOUT customer_id filter

From each response, extract `customers_mentioned` — count unique companies.

Also get the platform's top concerns for comparison:
- `search_insights(sort="severity", limit=5)` — what are the most severe issues across all customers?
- `get_facets(dimension="feature_area")` — what are the biggest feature areas by volume?

Write to `/tmp/pm-prep/patterns.md`:
- For each of the customer's top concerns:
  - How many OTHER customers reported similar issues (from `customers_mentioned`)
  - What percentage of the total customer base that represents (using `unique_customers` from overview)
  - Rank: is this in the top 5 platform-wide? Top 20? Not in the top 20?
  - Name 2-3 other customers who share the same concern
- Summary: "Their concerns are [typical for the platform / concentrated in their segment / unique to this account]"

**Agent 3: Segment lens**

- `search_customers(segment="{customer_segment}", limit=10, sort="insight_count")` — find peers in same segment
- `search_insights(query="{segment_name}", limit=10)` — what does this segment talk about?

For the top 5 segment peers:
- What are their top concerns? Do they match this customer's concerns?
- What's the segment's average frustration? How does this customer compare?

Write to `/tmp/pm-prep/segment.md`:
- Segment name, total customers in segment, total insights from segment
- Top 3 segment-level concerns (the things most customers in this segment raise)
- Where this customer aligns vs. diverges from segment peers
- "This customer is [typical of / an outlier in] their segment because..."

**Agent 4: Last 2 conversations (for open threads and voice)**

- `list_conversations(customer_id="{id}", source_type="calls", limit=5)`
- `get_conversation(id, source)` for the 2 most recent calls

Read each transcript and extract:
- What the customer was TRYING TO DO (the job, not the complaint)
- What questions they asked (reveals what they're evaluating)
- What they said about their own workflow and internal context
- Workarounds they described
- Competitors or alternatives they mentioned
- Emotional moments (frustration, excitement, resignation)
- Open threads: things promised but not confirmed as resolved

Write to `/tmp/pm-prep/conversations.md`:
- Per call: date, title, participants, what the customer was trying to accomplish, key quotes showing their voice
- Open threads with who committed and when
- Workarounds described in the calls

**Agent 5: Strategic signals + competitive context**

- `search_signals(customer_id="{id}", limit=30)` — all strategic intelligence
- For churn signals, competitor mentions, satisfaction: `get_signal(id)` for the most important ones

Write to `/tmp/pm-prep/strategic.md`:
- Satisfaction signals (if any): level and quote
- Competitor mentions: which competitors, what the customer said about them, and — critically — what UNDERLYING NEED the competitor mention reveals (not just "they mentioned X")
- Decision criteria: what they evaluate when choosing
- Churn signals: what's driving risk (is it product gaps or operational issues?)

**Agent 6: Per-person deep profiles (runs ONLY after user picks names)**

This agent does NOT run during the initial brief. It runs when the user responds to the WHO'S ON THE CALL section by picking names.

When triggered, launch one agent per selected person (in parallel). Each agent builds a **mini pm-prep brief scoped to one human** — not a summary card.

For each named person:
- `search_insights(customer_id="{id}", query="{person_name}", limit=30)` — find ALL insights reported by this person
- `get_insight(id)` for every result — read full content
- `list_conversations(customer_id="{id}", source_type="calls", limit=15)` — find all calls
- `get_conversation(id, source)` for the 2-3 most recent calls where this person spoke — read full transcripts
- `search_insights(customer_id="{id}", query="{person_name}", date_from="{30_days_ago}", limit=10)` — recent insights for "what changed"

For each person, extract a FULL profile:

**Last call analysis:**
- What did THIS person specifically raise, ask, and commit to on their most recent call?
- What was discussed that's still open?
- Not a one-liner — the full picture of their participation

**What changed since their last call:**
- New insights from them or about their topics since that call date
- Open threads that resolved or didn't
- New topics they hadn't raised before

**3-month trend:**
- Are their concerns escalating, stable, or cooling?
- Are they raising new topics or repeating the same ones?
- Is their frustration level increasing, flat, or decreasing?
- Mention count by month (e.g., "Mar: 8, Feb: 5, Jan: 3 — escalating")

**All open threads for this person:**
- What was promised TO them (by your team)
- What THEY committed to do
- Status of each: resolved, unknown, still open

**Their workarounds:**
- What do they personally cope with?
- Sophistication level of each workaround

**Their recurring questions:**
- What questions do they keep asking across calls? Recurring questions reveal what they're evaluating or what remains unsolved.

**Their voice — verbatim quotes organized by topic:**
- Not 1 quote. Their 5-8 most characteristic quotes across topics.
- Organized by theme, with dates.

**Communication style and decision role:**
- How they talk, how they decide, who they defer to, who defers to them

**Knowledge boundary:**
- Topics active at the company level that this person has NEVER mentioned
- This tells the PM what NOT to ask this person about

**Tailored questions (3-5):**
- Must-ask (2): from their open threads and last call
- Should-ask (1-2): from their trend or knowledge gaps about their domain
- All Mom Test compliant, traceable to their specific data

### Step 3: Assemble the brief

Read all agent files (5 if no names, 6 if names provided). Write the brief following the output format.

**The learning goal is written LAST** — after reading all evidence. It frames what this specific call could teach the PM that they don't already know.

## Output format

```
PM PREP: {Company Name}                                     {today's date}
==========================================================================

LEARNING GOAL
{What can this call teach you? Written LAST, after reading all evidence.
 Frame as a hypothesis to test or a knowledge gap to fill.
 Examples:
 - "114 customers report dashboard crashes but we don't know if the manual
   spreadsheet workaround is acceptable or deal-breaking. This call can answer that."
 - "This customer asked for custom reporting with external data — 3 others
   mentioned similar needs. Test whether the underlying job is 'build
   executive dashboards' or 'automate compliance reports.'"
 - "New CSV export bugs appeared this week. This customer was
   affected. Learn whether this blocks a core workflow or is an edge case."}

WHAT THEY'RE TRYING TO DO
{Their underlying needs, reframed as outcomes. Not feature requests.}

  1. {Outcome-framed need} ({n} mentions, frustration: {interpreted level})
     "{verbatim quote}" — {speaker}, {date}
     {If workaround exists: "Workaround: {description} ({sophistication})"}

  2. {Outcome-framed need} ({n} mentions)
     "{quote}" — {speaker}, {date}

  3. {Outcome-framed need} ({n} mentions)
     "{quote}" — {speaker}, {date}

  {Max 5. Grouped by underlying job, not by category.}

WHAT WE KNOW FROM OTHERS
{Adaptive relative positioning. No fixed thresholds.}

  | Their concern | Other customers | % of base | Platform rank |
  |---|---|---|---|
  | {need 1} | {n} of {total} | {%} | #{rank} |
  | {need 2} | {n} of {total} | {%} | #{rank} or "not in top 20" |
  | {need 3} | {n} of {total} | {%} | #{rank} or "not in top 20" |

  {Interpretation: "Their top 2 concerns are the platform's top 2 concerns.
   Their third concern is niche — only 12 customers, likely edge case."
   Or: "All 3 concerns are unique to this account — outlier, not pattern."}

WHAT WE DON'T KNOW
{Knowledge gaps this call could fill. The highest-value section.}

  - {Gap 1}: "{What we've heard from others but don't know about THIS
    customer, or what we've heard from this customer but lack context for}"
  - {Gap 2}: "{A contradiction in evidence, or a topic where data is thin}"
  - {Gap 3}: "{An assumption the PM holds that hasn't been tested}"

  {Max 3. Each should be answerable in a single conversation.
   If there are no clear gaps: "Strong evidence base on this customer.
   Use this call to validate or challenge existing understanding."}

SUGGESTED QUESTIONS
{Data-grounded. Mom Test compliant. Past behavior, never hypothetical.}

  Must-ask:
  - "{Question generated from open thread or landmine data}"
  - "{Question generated from the top knowledge gap}"

  Should-ask:
  - "{Question generated from cross-customer pattern}"
  - "{Question about a workaround or workflow}"

  If-time:
  - "{Forward-looking question about underlying need}"

  {5-7 total. Every question traceable to a specific data point.
   Never "would you use X?" Always "walk me through the last time..."}

THEIR VOICE
{2-3 verbatim quotes that capture how this customer talks and thinks.
 Organized by underlying need, not category. Include emotional moments.}

  On {topic}: "{vivid quote showing their perspective}"
  — {speaker}, {date}

  On {topic}: "{quote showing frustration or excitement}"
  — {speaker}, {date}

WHO'S ON THE CALL?
{Always shown at the end of the initial brief. Lists known contacts
 with their insight count and top topics so the PM can pick names.}

  Known contacts at {company}:
  {Numbered list of ALL known contacts with insights, sorted by insight count.
   Each line: number, name, title, insight count, top 2 topics.}

  Pick names for per-person prep — use numbers or first names from the list above:

==========================================================================
```

### When the user picks names — output per-person briefs (~30-40 lines each):

The agents compute full dossiers. The output balances depth with scannability.

```
==========================================================================
{NAME} — {Title}                                    {decides/recommends/executes}
==========================================================================

LAST CALL ({date})
{What THIS person raised, asked, and committed to. 4-6 lines covering
 their topics, their questions, what's still unresolved. Not a one-liner
 but not a transcript either.}

WHAT CHANGED SINCE
{New activity from them or about their topics since that call. Open
 threads that resolved or didn't. 2-4 lines. If nothing: "No new
 activity since {date}."}

3-MONTH TREND
  {month}: {n} insights | {month}: {n} | {month}: {n} — {direction}
  {One line: are they escalating, stable, cooling? New topics or repeating?}

THEIR CONCERNS (top 3, with quotes)

  {Topic 1}: "{most vivid quote}" — {date}
  {Topic 2}: "{quote}" — {date}
  {Topic 3}: "{quote}" — {date}

OPEN THREADS
  - {What was promised or committed}: {status} ({date})
  - {Another thread}: {status}

WORKAROUND: {their most notable workaround with sophistication level}

WON'T KNOW ABOUT: {company-level topics they've never mentioned}

ASK {FIRST NAME}:
  - "{Must-ask from open threads or last call}"
  - "{Should-ask from trend or knowledge gap}"
  - "{If-time from workaround or forward-looking}"

==========================================================================
{Repeat for each selected person. Max 3 people.}

Type "more on {first name}" for full dossier: all quotes by topic,
recurring questions, style analysis, and detailed knowledge boundary.

EXPLORE MORE
  - "{Suggestion 1 — a relevant follow-up using /closedloop:deep-dive}"
  - "{Suggestion 2 — a relevant follow-up using /closedloop:synthetic-customer}"
  - "{Suggestion 3 — a relevant follow-up using /closedloop:competitor-gap}"

{3 suggestions grounded in what was discovered during THIS brief.
 Each shows the exact command to run. Never use hardcoded topic examples
 in this template — generate from the actual data at runtime.}
```

## Output format (continued)

```
SEGMENT LENS
{Where this customer sits relative to peers in their segment.}

  Segment: {name} ({n} customers)
  Segment's top concerns: {topic 1}, {topic 2}, {topic 3}

  This customer [aligns with / diverges from] segment peers:
  - {How they're typical or atypical, with specific evidence}

{Only if competitor data exists:}
COMPETITIVE CONTEXT
{What the competitor mention REVEALS about the customer's underlying need.}

  {competitor}: mentioned in context of {underlying need}.
  "{quote}" — {date}
  {What this tells the PM: "They're not evaluating a competitor — they're
   looking for {capability} that happens to exist in {competitor}."}

==========================================================================
```

## Rules

- **Never show raw frustration scores.** Interpret the 0-1 number into plain language: 0-0.2 = calm, 0.2-0.4 = mild frustration, 0.4-0.6 = moderate frustration, 0.6-0.8 = high frustration, 0.8-1.0 = extreme frustration.
- **Learning goal, not headline.** The brief opens with what the PM can learn, not what the account looks like. Written last, shown first.
- **Outcomes, not features.** Every customer request is reframed as the underlying need. "Requested CSV export" → "Cannot incorporate data into existing reporting workflows."
- **Adaptive positioning.** Show rank and percentage against the full customer base. Never use fixed thresholds like "10+ = market signal." The rank tells the story.
- **Knowledge gaps are mandatory.** Even if well-understood, say "strong evidence base — use this call to validate." The section is never skipped.
- **Questions come from data.** Every suggested question traces to a specific insight, signal, open thread, or knowledge gap. No generic templates.
- **Mom Test compliant.** All questions ask about past behavior, never hypothetical future. "Walk me through the last time..." not "Would you use...?"
- **Workarounds = gold.** Always surface workarounds with their sophistication level. They prove the need is real and indicate willingness to pay.
- **Segment context prevents bias.** Show where this customer sits vs. peers so the PM doesn't over-index on one voice.
- **Competitor mentions decoded.** Don't just say "they mentioned X." Say what underlying need the mention reveals.
- **People, not companies.** The brief always ends with a contact list. When the user picks names, run Agent 6 and show per-person profiles with tailored questions, communication style, and knowledge boundaries.
- **Knowledge boundaries per person.** Show what each person has NOT discussed — it tells the PM where this person's expertise stops and someone else's starts.
- **Two-step flow.** First run: company brief + contact list. Second run (after user picks names): per-person profiles. Never try to parse person names from the initial input — always resolve company first, then ask.
- **250-400 words for initial brief.** Per-person follow-up is a full mini-brief per person — as deep as needed. No artificial word limit on per-person sections.
- **Omit empty sections.** No competitor data? Skip it. No strategic signals? Skip it. Thin accounts get shorter briefs.

## Data quality

- Silently exclude automated/bot-generated insights
- Deduplicate: same customer, same topic, same call = one mention
- When counting "other customers" for relative positioning, count unique companies, not mention volume
- Support ticket noise doesn't count as a "concern" for the PM brief

## What this skill does NOT do

- **Does not show account health, renewal dates, or deal status.** That's `/closedloop:csm-prep`.
- **Does not replace the deep-dive.** For full evidence on a topic, run `/closedloop:deep-dive {topic}`.
- **Does not build a persona.** For understanding how a customer thinks, use `/closedloop:synthetic-customer {name}`.
- **Does not generate a spec or PRD.** It's pre-call prep, not a planning document.
- **Does not tell the PM what to build.** It shows what customers need. The PM decides.
