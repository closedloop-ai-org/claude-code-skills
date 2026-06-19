---
name: "closedloop:submit-feedback"
description: "Capture a piece of customer feedback into ClosedLoop AI — translate it to English, strip unrelated PII, preview it, then submit on your confirmation. The other half of the closed loop: get feedback IN as cleanly as the read skills get insights OUT."
---

# /closedloop:submit-feedback

A customer told you something about the product — on a call, in a Slack thread, in an email, or right here in this conversation. Capture it in ClosedLoop AI so it joins your product insights. This skill takes the raw feedback, translates it to English, strips PII that isn't the signal, shows you a preview, and submits **only after you confirm**.

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

Also confirm `submit_feedback` is in the tool list. If you see the read tools (`get_overview`, `search_insights`, …) but **not** `submit_feedback`, your MCP connection predates the write tool — reconnect (`/mcp` → re-authorize) to pick it up.

## Input handling

The user gives you the feedback in plain language, or points at it in the conversation.

```
/closedloop:submit-feedback the customer said export keeps timing out on big reports
/closedloop:submit-feedback log the SSO complaint from the call just now
/closedloop:submit-feedback <a pasted customer message, in any language>
```

If the user says "log that" / "submit this" referring to something earlier in the conversation, use that — do not make them retype it.

## Execution

### Step 1: Identify the actual feedback

Pull the real product feedback the customer expressed — the complaint, request, praise, or bug report. Use **only** what's in the conversation or the user's input. Do not invent details, severity, a quote, or a customer who wasn't named.

### Step 2: Translate to English

If the feedback isn't in English, translate it **faithfully** — preserve the meaning verbatim, keep the customer's own framing. Do NOT summarize or paraphrase. (ClosedLoop AI content is English-by-contract downstream.) Keep the original text to show in the preview.

### Step 3: Scrub PII from the content

The feedback `content` is the product signal — not a data dump. Remove:

- people unrelated to the feedback (other names / emails mentioned in passing),
- secrets, tokens, internal IDs, credentials,
- sensitive personal data that isn't about the product.

KEEP the substance of what the customer said. The customer's **own** identity (who gave the feedback) does NOT go in the content — it goes in `metadata` as a hint (Step 4). There is no server-side scrubbing; this skill is the only PII gate.

### Step 4: Assemble metadata (hints, not facts)

Put triage context into `metadata` — only what's actually known from the conversation:

- `customer` / `reporter` — who gave the feedback (name and/or email), if known
- `source` — where it came from ("sales call", "support thread", "in-app", …)
- `original_language` — if you translated
- `feature` / `area` — the product area, if the user named it

Everything in `metadata` is an unverified hint. Never fabricate a value to fill a field — omit it.

### Step 5: Preview and confirm

Show the user exactly what will be submitted, then stop for confirmation:

```
PREVIEW — submit to ClosedLoop AI?

  Feedback (English):
    "{translated, PII-scrubbed content}"
  {Original ({lang}): "{verbatim original}"   ← only shown if you translated}

  Metadata:
    customer: {…}
    source: {…}
    {…}

  Submit this?  (yes / edit / cancel)
```

Only on **yes** → Step 6. On **edit**, apply the change and re-preview. On **cancel**, stop.

### Step 6: Submit

Call `submit_feedback(content="{English content}", metadata={…})`. Report the returned `id`. Describe the result honestly as **recorded** — do not claim it was "analyzed", "turned into an insight", or that credits were charged. Processing happens separately, later.

## Output format

```
✓ Feedback recorded in ClosedLoop AI
  id: {returned id}
  customer: {from metadata, if known}
  logged: {one-line restatement of what was captured}
```

## Rules

- **Faithful, not summarized.** Translation preserves the customer's meaning verbatim. Never compress feedback into your own words.
- **Their feedback, not your inference.** Submit only what the customer actually conveyed. Keep verbatim separate from any inferred context. Never invent a quote, a severity, or a customer.
- **PII discipline.** Strip unrelated people, emails, secrets, and credentials from the content. The customer's own identity belongs in `metadata`, not in the verbatim. This skill is the only gate.
- **Preview before every submit.** Never submit silently — the user sees the exact `content` + `metadata` and confirms first.
- **One piece of feedback per call.** For several distinct items, submit each separately so each becomes its own record.
- **English only in `content`.** If the source was another language, translate; keep the original in the preview / `metadata`, never as non-English text in `content`.
- **Honest confirmation.** Report it as "recorded" — never "analyzed into insights".

## What this skill does NOT do

- **Does not analyze.** It records feedback; the read skills (`/closedloop:deep-dive`, `/closedloop:weekly-brief`) surface insights once it's processed.
- **Does not research.** Enrichment is limited to what's in the conversation — it will not call other tools to dig up details the user didn't give.
- **Does not submit without confirmation.** Always previews first.
- **Does not store raw PII.** Unrelated personal data, secrets, and credentials are scrubbed before submission.
- **Does not de-duplicate.** Submit the same feedback twice and it's recorded twice.
