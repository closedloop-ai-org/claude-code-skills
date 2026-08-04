---
name: "closedloop-bug-blast-radius"
description: "Answer how important a bug is: who reported it, how badly, what it is worth, and when it was last reported. Uses get_bug_blast_radius. Read only; reflects reported pain."
---

# ClosedLoop AI Bug Blast Radius

Answer one engineering question: **how important is this bug?**

This skill governs `get_bug_blast_radius` only. It reads. It writes nothing, notifies nobody, and calls no other tool.

The API computes every number. Your job is governance, interpretation, and refusal — deciding which of the retrieved evidence actually describes this bug, saying what the numbers can and cannot support, and never inventing a value the tool did not return.

## Input

One defect at a time, in the user's own words.

```text
How bad is the saved-card checkout failure?
Is the CSV export timeout worth fixing this sprint?
Blast radius for the SSO redirect loop
```

Default the categories. Add `Integration Issue` when the bug is about a third-party sync, webhook, or connector — it is deliberately not in the default set, so an integration bug looks smaller than it is until you ask for it.

Use `feature_area` when the user names one. Use `date_from` / `date_to` only when they ask about a window.

## Execute

```text
get_bug_blast_radius(
  query="{the bug in plain language}",
  categories={["Bug","Performance Issue","Security Issue","UX/UI Issue"] or the user's set},
  feature_area="{if named}",
  date_from="{if asked}",
  date_to="{if asked}",
  limit={default 25},
  insight_limit={default 50}   # by RELEVANCE; per-customer representatives are added on top
)
```

## Read the evidence before reporting

This is the step the tool cannot do and the reason it returns verbatim content.

Read `insights[]`. Semantic retrieval pulls in adjacent complaints — a different bug in the same feature area, a feature request phrased as a failure, a duplicate of something already fixed. Name the ones that are a **different problem** and exclude their customers.

Then report both numbers:

> {total} customers reported this. I excluded {k} ({names}) whose evidence is about expired cards, not saved-card decline — {remaining} customers, {ARR after exclusion}.

**Check `coverage.totals_decomposable` before you subtract anything.**

- **`true`** — every matched customer is in `customers[]`, so dropping one subtracts exactly that customer's row. **Subtract, never recompute.** Do not re-call with a narrower query to "clean up" the number.
- **`false`** — more customers matched than were returned, so the totals cover rows you never saw and cannot audit. **Do not subtract.** Report the census total as-is, say how many customers you were able to read, and name the ones you excluded without adjusting the headline. If the user needs a corrected figure, re-call with `limit` raised to 50; if it is still false at 50, say the bug is too widespread to correct by hand and give the census.

Never silently drop a customer, and never keep one that plainly does not match in order to protect the headline.

## Present results

```text
BUG BLAST RADIUS: {query}
=========================

Exposure: {exposure_score}/100
Searched: {bug.categories_searched}{, feature_area}
Reported by: {totals.customers_affected} customers, {totals.insights} insights
Revenue: {totals.arr_affected} {totals.arr_currency}
{if coverage.arr_includes_non_reporting_members: "  of which {totals.arr_affected_reporting_members} is the members that actually reported"}
Last reported: {totals.last_reported} ({trend.direction} over {trend.direction_window_days}d)

RECOMMENDATION: {HOTFIX | NEXT SPRINT | BACKLOG}
Rule: {the rule that fired, with the numbers that satisfied it}

CUSTOMERS
1. {name} — {arr} {currency}, {insight_count} reports{, deal blocker}{, churn_state}
   {if reporting_member_count < member_count: "(chain: {reporting_member_count} of {member_count} members reported; their ARR is {reporting_arr})"}
   "{verbatim from the linked insight}"
...

EXCLUDED AFTER READING THE EVIDENCE
- {name}: {why this is a different problem}
{if totals_decomposable is false: "Headline unchanged — N of M customers were
 returned, so the totals cannot be corrected by subtraction."}

COVERAGE
- {anything from the coverage block that bites}
- Reflects reported pain only. Customers hitting this bug who did not contact
  you are not represented.
```

Recommendation thresholds, printed every time so the reader can disagree with the rule rather than the number:

- **HOTFIX** — any deal blocker, or any Critical, still reported within 30 days.
- **NEXT SPRINT** — `exposure_score >= 50`, or accelerating trend with more than one customer.
- **BACKLOG** — everything else.

## Read the coverage block out loud when it bites

- `insights_without_crm_link > 0` — the ARR is a **floor**, not a total. N more reports could not be attributed to a customer.
- `window_predates_coverage` — say this **first**. The requested window starts before this team has any feedback, so an empty early period is missing coverage, not an absence of reports.
- `customers_without_priced_deals > 0` — those customers are affected and contribute 0 to ARR. Zero ARR is not zero impact.
- `arr_includes_non_reporting_members` — at least one counted customer is a family whose other members did **not** report, and the default `customer_scope: 'family'` rolls the whole family's ARR into `arr_affected`. That is the right answer to "what is this customer worth" and reads as an overstatement of "revenue affected". Print **both** figures and say which is which; never present `arr_affected` alone when this is true. One domain can map to thousands of companies, so the gap can be large.
- `trend.direction` of `no_recent_reports` — nothing in either 14-day window. Say the bug has gone quiet and give `totals.last_reported`; do **not** call it steady, which reads as "still happening at a constant rate".
- `customers_truncated` / `totals_decomposable: false` — more customers matched than were returned. The totals still cover all of them, but you cannot subtract from them; see above.
- `keyword_matching_available: false` — the keyword query failed (a database error, not a missing credential). Say the search was semantic-only and the counts may be short.
- `matched_insights_capped` — retrieval hit its bound, so the counts are a floor. This should be rare; when it fires, say the counts are a floor rather than a census.
- `semantic_matching_available: false` — matching was keyword-only, so a report phrased differently was not found. Say this; it is not the same as "no such reports exist".
- `keyword_terms_used: 0` — the query had fewer than two significant words, so keyword matching was skipped and only semantic matching ran. A single word names an area, not a bug: ask for the failure, or pass it as `feature_area`.
- `feature_area_exists: false` — the area you filtered on does not exist for this team. The empty result is the filter, not an absence of reports. Suggest the real spelling or drop the filter.
- `semantic_pool_capped` — the semantic candidate pool filled and its weakest member still cleared the bar, so more reports may qualify than were considered. Counts are a floor.
- `semantic_floor` — the cosine cut applied to semantic matches. Report it if the user questions why something they expected is missing; it is published so the cut can be audited rather than trusted.

## Feedback To ClosedLoop AI

If the data looks missing, stale, low-quality, or surprising, or the user says the customers, counts, revenue, or evidence are wrong or incomplete, explicitly invite them to send feedback about ClosedLoop AI. If they ask you to send it, use `closedloop-send-feedback` or call `send_closedloop_feedback(content=...)`. Keep the feedback about the ClosedLoop AI product/data experience, strip PII and customer-specific data, and do not treat it as customer evidence.

## Rules

- Use only values returned by `get_bug_blast_radius`. Never infer a number it did not return.
- If a field is absent, say it is absent. Never substitute a plausible value.
- Never call write tools. This skill reads.
- Say "N customers **reported** this", never "N customers are affected".
- When ARR is 0, say "no priced deals resolved for these customers", never "no revenue at risk".
- When `deal_blockers` is 0, say nothing about deal blockers. Marking is rare on defect rows, so absence is not evidence.
- Never say a bug is fixed. State the last reported date and let the reader conclude.
- Never estimate affected users, severity, or impact for a customer that returned none.
- Quote evidence verbatim as returned. Do not paraphrase a quote into severity language.
- `customer_name` / `customer_email` on an insight are for attribution ("reported by X at Acme"), never for outreach. This skill does not contact anyone; if the user wants to follow up, hand them the name and stop.
- Always print which categories were searched, so a thin result names its own constraint. If the query looks integration-shaped and returned little, suggest re-running with `Integration Issue`.
- If zero customers match, say the query matched nothing within the categories searched and suggest widening. Never report "no customers are affected".
- Always surface the reported-pain-only caveat.
