---
name: "closedloop:sales-playbook"
description: "Pain-point sales talk tracks from real customer quotes, workarounds, and competitor gaps. General playbook per topic, or micro-targeted for a specific customer with social proof from their peers."
---

# /closedloop:sales-playbook

Generate a sales playbook grounded in what customers actually say — pain points with verbatim quotes, cost of inaction from real workarounds, competitive positioning from real mentions, and proof points from won deals. General or micro-targeted to a specific customer.

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

Topic required. Customer optional — use `@` to target a specific company.

```
/closedloop:sales-playbook checkout flow
/closedloop:sales-playbook API rate limits @ Acme Corp
```

**No `@`** → general playbook for the topic across all customers.
**With `@`** → micro-targeted playbook: what THIS customer said + social proof from their peers.

Parse by splitting on `@`. Left side = topic (trimmed). Right side = customer name (trimmed). If `@` is absent, entire input = topic.

If the customer name after `@` doesn't match any company in `search_customers`, say so and show closest alternatives.

## Execution — General Mode (no customer)

### Step 1: Launch 4 agents in parallel

**Agent 1: Pain points with verbatim quotes**

- `search_insights(query="{topic}", sort="severity", limit=50)`
- `search_insights(query="{topic}", sort="frustration", limit=50)`
- `get_insight(id)` for the top 15 by severity and frustration

Group by pain theme. For each theme:
- Count of unique customers mentioning it
- Severity distribution
- Most vivid verbatim quote (highest frustration, most specific)
- Workaround if described (note sophistication: manual process → spreadsheet → hired person → custom tool)

Write to `/tmp/sales-playbook/pain.md`

**Agent 2: Competitive positioning**

- `search_insights(query="{topic} competitor", limit=30)`
- `search_signals(type="competitor_mention", query="{topic}", limit=30)`
- `search_signals(type="competitive_positioning", query="{topic}", limit=20)`
- `get_signal(id)` for the top 10

For each competitor mentioned in context of this topic:
- What customers say the competitor lacks or does differently
- Trap questions that expose competitor weaknesses
- Talk track: "When they bring up {competitor}, say..."

Write to `/tmp/sales-playbook/competitive.md`

**Agent 3: Win reasons and objection handling**

- `search_signals(type="win_reason", query="{topic}", limit=30)`
- `search_signals(type="decision_criteria", query="{topic}", limit=30)`
- `search_signals(type="purchase_hesitation", query="{topic}", limit=30)`
- `get_signal(id)` for the top 10 per type

Extract:
- Top win reasons with customer quotes (why they chose you)
- Decision criteria customers cite (what they evaluate)
- Purchase hesitations (objections to prepare for)
- For each hesitation: the rebuttal + proof point from a won deal

Write to `/tmp/sales-playbook/win.md`

**Agent 4: Segment context**

- `search_insights(query="{topic}", limit=50)` — collect all customer names
- For the top 10 customers by mention count: `search_customers(query="{name}", limit=1)`

Build segment breakdown: which segments report this pain? Enterprise vs mid-market vs SMB — do they describe it differently? Which segments have the most evidence?

Write to `/tmp/sales-playbook/segments.md`

### Step 2: Assemble the playbook

Read all 4 files. Write the playbook following the output format.

## Execution — Micro-Targeted Mode (with customer)

### Step 1: Resolve the customer

```
search_customers(query="{customer_name}")
```

Record customer_id, name, segment, industry, deal value, deal stage.

### Step 2: Launch 5 agents in parallel

**Agents 1-4:** Same as general mode — gather all evidence about the topic across ALL customers.

**Agent 5: This customer's specific context**

- `get_customer(id)` — full profile, deals, contacts
- `search_insights(customer_id="{id}", query="{topic}", limit=20)`
- `get_insight(id)` for each — what THIS customer said about this topic
- `search_signals(customer_id="{id}", limit=20)` — their competitor mentions, decision criteria, hesitations
- `list_conversations(customer_id="{id}", source_type="calls", limit=5)`
- `get_conversation(id, source)` for the 1-2 most recent calls — read for context about this topic

Extract:
- What THIS customer specifically said about the topic (verbatim quotes)
- Their workaround
- Their deal value and stage
- Their decision criteria and hesitations
- Competitors they mentioned
- Key contacts and their roles

Write to `/tmp/sales-playbook/customer.md`

### Step 3: Assemble the micro-targeted playbook

Read all 5 files. The output leads with THIS customer's specific context, then layers in social proof from peers in their segment.

## Output format — General Mode

```
SALES PLAYBOOK: {topic}
==========================================================================

THE PAIN ({N} customers, {N} insights)
{Top 3 pain themes ranked by frequency x severity. Customer voice only.}

  1. {Pain theme} ({N} customers, {severity})
     "{Most vivid verbatim quote}" — {customer}
     Workaround: {what they do today} ({sophistication})

  2. {Pain theme} ({N} customers)
     "{quote}" — {customer}

  3. {Pain theme} ({N} customers)
     "{quote}" — {customer}

COST OF INACTION
{Quantified from workarounds. The "do nothing" price tag.}

  {N} customers describe manual workarounds for this problem.
  Common patterns:
  - {workaround type}: {N} customers. "{representative quote}"
  - {workaround type}: {N} customers. "{quote}"

  Talk track: "We hear from teams like yours that they spend
  {time/effort} on {workaround}. What does that look like for you?"

WHY WE WIN
{From actual won deals where this topic was a factor.}

  1. {Win reason}: "{customer quote}" — {customer}, {segment}
  2. {Win reason}: "{quote}" — {customer}

  Decision criteria customers cite:
  - {criterion}: mentioned by {N} customers
  - {criterion}: mentioned by {N} customers

COMPETITIVE POSITIONING
{Per competitor mentioned in context of this topic.}

  {Competitor}:
    What customers say: "{gap quote}" — {customer}
    Trap question: "{question that exposes their weakness}"
    Talk track: "{what to say when they bring up this competitor}"

  {If no competitors mentioned for this topic, omit section.}

OBJECTION HANDLING (top 3)

  "{Objection as the prospect would say it}"
  → Acknowledge: "{validation}"
  → Reframe: "{pivot to your strength}"
  → Proof: "{customer name} had the same concern — {outcome}"

  {Repeat for top 3 purchase hesitations.}

BY SEGMENT
{Only if segments have genuinely different concerns about this topic.}

  {Segment}: lead with {pain theme}, best proof: "{quote}" — {customer}
  {Segment}: lead with {pain theme}, best proof: "{quote}" — {customer}

==========================================================================
```

## Output format — Micro-Targeted Mode

```
SALES PLAYBOOK: {topic} @ {Customer Name}
==========================================================================

{Customer Name} — {segment} — ${deal_value} — {deal_stage}
Contact: {name}, {title}

WHAT THEY SAID ABOUT THIS
{What THIS customer specifically told you about this topic.}

  "{Their verbatim quote}" — {contact}, {date}
  {If multiple quotes, show 2-3 most relevant}

  Workaround: {what THEY do today}
  Deal impact: {is this blocking the deal? churn risk? expansion opportunity?}

WHAT THEIR PEERS SAY (social proof ammunition)
{Other customers in the same segment who raised the same concern.}

  {N} other {segment} customers report the same pain:
  - "{quote}" — {similar company}
  - "{quote}" — {similar company}

  Ready to use: "Companies like yours in {industry} tell us {pattern}."

THEIR DECISION CRITERIA
{From THIS customer's signals — what they evaluate.}

  - {criterion}: "{their quote about it}"
  {If no decision criteria from this customer, use segment-level.}

COMPETITIVE CONTEXT FOR THIS CUSTOMER
{Did THIS customer mention a competitor? What did they say?}

  {competitor}: "{their quote}" — {date}
  When they bring up {competitor}: "{targeted talk track}"
  {If no competitor mentions from this customer, show general competitive.}

COST OF THEIR WORKAROUND
{Their specific workaround, quantified if possible.}

  They currently: {workaround description}
  Talk track: "You mentioned {their workaround}. Teams like yours
  in {segment} typically spend {estimate} on that. What if..."

OBJECTIONS TO EXPECT
{Based on THIS customer's purchase hesitations and prior conversations.}

  "{Likely objection from their signals}"
  → Response: "{rebuttal}" + proof from {similar customer in segment}

  {If no customer-specific hesitations, use top 3 general objections.}

PROOF POINTS FOR THEIR SEGMENT
{Won deals in same segment where this topic was the win reason.}

  "{Customer} chose us because {reason}" — {same segment/industry}

==========================================================================
```

## Rules

- **Customer voice only.** Every claim backed by a verbatim quote. No invented positioning.
- **FIA per competitive entry.** Fact (what's true), Impact (why it matters in a deal), Act (what to say/do/show).
- **Conversational language.** Talk tracks must sound like something a human would say on a call. Not marketing copy. If it sounds like a press release when read aloud, rewrite it.
- **Workarounds = strongest ammunition.** A customer who built a workaround has proven the need is real and the budget exists. Always surface workarounds with sophistication level.
- **Loss aversion framing.** Cost of Inaction beats ROI. "You're spending $X on manual workarounds" beats "you could save $X."
- **Similarity matters.** Social proof from a company in the same segment/industry/size is 3x more persuasive than from a different segment. Match proof points to the prospect.
- **Top 3, not top 10.** Paradox of choice — 3 pain points, 3 objections, 3 proof points. More dilutes the message.
- **Preemptive for top 3 objections.** Bake the most common hesitations into the talk track narrative. Reactive framework (LAARC) for unexpected ones.
- **Never show raw frustration scores.** Interpret: calm, mild, moderate, high, extreme.
- **Omit empty sections.** No competitors mentioned? Skip it. No win reasons? Skip it.
- **Micro-targeted mode leads with THIS customer.** General evidence is social proof, not the lead. The customer's own words come first.

## Data quality

- Silently exclude automated/bot-generated insights
- Deduplicate: same customer mentioning the same pain = one entry with count
- Count unique customers, not mentions. 5 mentions from 1 customer ≠ 5 customers
- Workaround sophistication: manual process (mild) → spreadsheet (moderate) → hired person (strong) → custom tool (very strong)

## What this skill does NOT do

- **Does not generate slide decks or PDFs.** Output is a scannable text playbook. Copy sections into your presentation tool.
- **Does not update automatically.** Run again for fresh data. The output is a snapshot.
- **Does not replace CRM notes.** This is sales ammunition, not account planning.
- **Does not fabricate competitive claims.** Only shows what YOUR customers say about competitors. Never invents competitor weaknesses.
