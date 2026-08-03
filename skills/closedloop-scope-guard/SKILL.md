---
name: "closedloop-scope-guard"
description: "Check a spec, PRD, or ticket against customer evidence before it gets built, and say what to change about it: which requirements to sharpen and how, which to split or merge, which customer needs the spec misses, and which have no evidence behind them. Uses check_scope_evidence. Read only; never recommends against building anything."
---

# ClosedLoop AI Scope Guard

Check a spec against what customers actually said, before engineering time goes into it.

This skill governs `check_scope_evidence` only. It reads; it writes nothing.

## Check ClosedLoop AI MCP is available

Before doing anything, try calling `get_overview(time_range="all")`.

**If the call fails or the tool is not found:**

```
ClosedLoop AI MCP is not connected. This skill needs it to access your customer feedback data.

Set it up in 30 seconds — use the endpoint that matches your ClosedLoop AI app URL:
  US  (app.closedloop.sh)     https://mcp.closedloop.sh
  EU  (eu.app.closedloop.sh)  https://eu.mcp.closedloop.sh

Then add it with your agent (swap in your region's URL):
  Claude Code   claude mcp add --transport http closedloop-ai <URL>   then /mcp and authorize
  Codex CLI     codex mcp add closedloop-ai --url <URL>               then codex mcp login closedloop-ai

Full guide: https://closedloop.sh/docs/mcp-server/overview
```

Then stop.

## Input

Accept a spec, PRD, ticket, or a plain description of what is about to be built. A file path, pasted text, and a linked issue are all fine.

```text
Check this spec against customer evidence: <pasted PRD>
Does anyone actually want the things in ENG-1204?
We're about to build tiered export permissions. Is that grounded?
```

Split it into one short statement per requirement, in the spec's own words. Then **show the numbered list back and ask the user to correct it before calling the tool.** A decomposition the user can see is a decomposition they can fix; every match downstream depends on it.

```text
I read this spec as 4 requirements:
  1. Admins can bulk-export tickets as CSV
  2. Exports include custom fields
  3. Exports are signed with a customer-supplied PGP key
  4. Export jobs can be scheduled weekly

Area: ticket exports

Correct anything before I check it against evidence.
```

## Execute

One call:

```text
check_scope_evidence(
  requirements=["{one statement per requirement}"],
  area="{the feature area or topic the spec sits in}",
  include_scope_extras={true when the user wants the area's full picture},
  date_from="{YYYY-MM-DD if the user scoped a window}",
  date_to="{YYYY-MM-DD if the user scoped a window}"
)
```

Always pass `area` when you can name one. It is what `missing_from_scope` is measured against, and what an absence is judged against.

## Judge the matches

The tool retrieves candidate themes by similarity and returns their real evidence. Similarity
cannot tell you whether a theme is actually *about* a requirement, and it is not trying to:
`match_strength` is a retrieval hint. **The judgment is yours, and it is the point of this
skill.**

For each requirement, read the matched theme names against the requirement's own words and
decide:

- **covered**: at least one matched theme is plainly the same need, in different words.
- **partly covered**: a matched theme is adjacent but not the same thing (say what the gap is).
- **not covered**: no matched theme is about this requirement, whatever their similarity.

**Every number and every quote belongs to a theme, and there is no requirement-level total.**
That is deliberate. One requirement routinely matches several *different* needs — a request to
export in bulk can come back matched to an export theme, a bulk-*edit* theme and an *import*
theme — so a combined figure would assert they are the same need. Rejecting a theme therefore
just drops its line; there is nothing to correct.

**Never add the per-theme numbers together.** One insight can belong to two themes, so the
per-theme counts overlap and their sum overstates the evidence. Report each accepted theme's
own numbers.

Two failure shapes to expect, both real:

- A requirement spans a big broad theme *and* a small niche one. Both come back; the broad one
  usually carries the evidence that matters. Do not report only the first.
- A requirement nobody has raised still returns themes, because something is always nearest.
  "Exports are signed with a customer-supplied PGP key" matching *Exports time out on large
  accounts* is a **not covered**, not a weak yes. Reject it out loud rather than passing its
  numbers through. When nothing clears the bar at all the tool returns `nearest_themes` with no
  counts and no quotes: report that as a genuine absence.

State which themes you accepted and which you rejected. A reader who disagrees with you can
only do so if they can see what you discarded.

## Present Results

```text
SCOPE GUARD: {area}
===================

{your count} of {summary.requirements_checked} requirements are covered by what customers raised.

1. {requirement}  [covered]
   {matched_themes[0].theme}
     {matched_themes[0].insight_count} insights, {matched_themes[0].customer_count} customers, {matched_themes[0].deal_blocker_count} deal blockers
     "{matched_themes[0].top_evidence[0].quote}"
     {matched_themes[0].top_evidence[0].account_name}, {matched_themes[0].top_evidence[0].at}
   {matched_themes[1].theme}
     {matched_themes[1].insight_count} insights, {matched_themes[1].customer_count} customers
     "{matched_themes[1].top_evidence[0].quote}"
     {matched_themes[1].top_evidence[0].account_name}, {matched_themes[1].top_evidence[0].at}
   Rejected: {matched_themes[2].theme} — about {what it is actually about}, not this requirement.

3. {requirement}  [not covered]
   Nothing matched. Nearest was {nearest_themes[0].theme}, which is about something else.
   {coverage.reads_as}

NOT IN THE SPEC
- {need} ({insight_count} insights, {customer_count} customers)
```

**Every figure sits under the theme it came from.** That is what makes your judgment checkable:
a reader who disagrees with one theme can discount that line and keep the rest. Never merge the
lines into a single number for the requirement, and never present a theme's numbers without its
name.

## Say what changes about the spec

Everything above tells the reader what customers said. **This section is the only part that
tells them what to do next, and it is required.** Without it you have handed someone an
organised list and left the actual work — deciding what the spec should now say — exactly where
it was. End every run here.

Under a `WHAT TO CHANGE` heading, one line per requirement, in the imperative, numbered to match
the decomposition. Each verdict must be grounded in something the tool returned — a verbatim
quote, the matched theme's own `description`, or a `missing_from_scope` entry — and must name
that grounding inline. Never derive a verdict from the spec's own wording, from the theme title
alone, or from what you assume the product already does.

Each verdict below is a rule with a boundary. Read both halves before assigning one.

- **Sharpen** — the accepted evidence describes the need more precisely than the requirement
  does, so building the line as written could leave the described problem unfixed. Say which
  words to change and to what. Boundary: a requirement that is merely BROADER than one quote is
  not automatically imprecise; the test is whether a reasonable implementation of the line as
  written would miss what the evidence describes. This is the highest-value verdict, because a
  requirement can be genuinely well covered and still be wrong in the detail that matters.
- **Split** — the accepted evidence for one requirement describes two mechanics that would be
  built and tested separately. Name both. Boundary: two quotes about the same mechanic in
  different words are not a split; two symptoms of one cause are not a split.
- **Merge** — customers describe two of your requirements as steps in one workflow, so scoping
  them apart ships two half-answers. Boundary: requirements that merely share a matched theme
  are not a merge — retrieval groups by topic, and a topic is not a workflow.
- **Add** — a `missing_from_scope` entry names a need in this area no requirement covers. Give
  its numbers. Boundary: only from that field. Never invent a gap by reasoning about what the
  spec "ought" to include.
- **No evidence** — nothing in the returned feedback describes this requirement. State it with
  the coverage verdict and stop. Boundary: this reports an absence, it never recommends
  removing anything — see Rules.
- **Build as written** — covered, precise, nothing to change. Say so in one line rather than
  padding it.

Assign exactly one verdict per requirement. Where two seem to apply, prefer the one that changes
the most about what gets built.

## Feedback To ClosedLoop AI

If the data looks missing, stale, low-quality, or surprising, or the user says a requirement was matched or missed wrongly, explicitly invite them to send feedback about ClosedLoop AI. If they ask you to send it, use `closedloop-send-feedback` or call `send_closedloop_feedback(content=...)`. Keep the feedback about the ClosedLoop AI product/data experience, strip PII and customer-specific data, and do not treat it as customer evidence.

## Rules

- **Always end with "What to change".** A run that stops at the evidence has done half the job: the reader still has to work out what the spec should now say, which is the work they came to you for. Every requirement gets a verdict.
- Never say "do not build this". A weak match may be a compliance need, a platform bet, or something nobody has been asked about — support channels are where people report what is broken, not where they ask for what they are contractually required to have. Report it with its coverage; the build decision is the user's. This is exactly why "no evidence" is a verdict and "cut it" is not.
- **A verdict must quote its evidence.** "Sharpen this" with nothing under it is an opinion. Every instruction cites the quote, theme description or `missing_from_scope` entry it came from, so the reader can disagree with the specific line rather than the whole report.
- Never present a number without the theme name it came from, and never sum the per-theme numbers into a requirement total — the themes can be different needs, and their insights can overlap.
- `match_strength` is a retrieval hint, never a verdict. You decide covered / partly / not covered by reading the theme names, and you say which you rejected.
- Never render a weak match without its coverage sentence.
- Quote customers verbatim and name them. Never paraphrase a quote into a stronger claim.
- Use only what the tool returned. Never fill a gap from the spec's own wording or from memory.
- Never estimate engineering cost, effort, or sequencing, and never rank this spec against other work.
- If the decomposition is ambiguous, ask rather than guessing. A wrong split produces confident wrong matches.
- `missing_from_scope` needs an `area`. Without one it is empty by construction, not because the spec is complete.
