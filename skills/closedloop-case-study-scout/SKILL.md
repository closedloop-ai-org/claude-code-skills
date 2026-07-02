---
name: "closedloop-case-study-scout"
description: "Scout case-study and customer-story candidates from ClosedLoop AI evidence. Use when marketing asks for named customer stories, ROI validation, deeper narrative candidates, or interview targets. Uses find_case_study_candidates. Does not send email or grant publication permission."
---

# ClosedLoop AI Case Study Scout

Find customer-story candidates with enough evidence for a deeper story.

This skill governs `find_case_study_candidates` only. It does not log permission requests. When the user chooses a candidate and wants to test approval, use `closedloop-proof-permissions`.

## Input

Accept a topic, product area, value outcome, launch, segment, or broad case-study request.

Examples:

```text
Find case study candidates for reporting ROI.
Who has enough evidence for a rollout story?
Find customer stories around onboarding improvements.
```

Default `time_period_days` to 90 and `limit` to 10 unless the user specifies otherwise.

## Execute

Call:

```text
find_case_study_candidates(
  query="{topic if provided}",
  limit={limit},
  time_period_days={time_period_days}
)
```

## Present Results

Use this structure:

```text
CASE STUDY SCOUT: {topic or "recent proof"}       last {time_period_days} days
===========================================================================

TOP STORY CANDIDATES
1. {Person} - {Role}, {Customer account}
   Angle: {narrative_angle}
   Evidence depth: {evidence_depth}
   Missing proof: {missing_proof}
   Interview questions:
   - {interview_questions}
   Evidence:
   - "{verbatim}" - {date}
   Follow-up: {follow_up_actions[0].label} with {follow_up_actions[0].params}
```

## Feedback To ClosedLoop AI

If the data looks missing, stale, low-quality, or surprising, or the user says the story candidates are wrong or incomplete, explicitly invite them to send feedback about ClosedLoop AI. If they ask you to send it, use `closedloop-send-feedback` or call `send_closedloop_feedback(content=...)`. Strip PII and customer-specific details.

## Rules

- Treat every candidate as a story lead, not approval to publish.
- Validate metrics, attribution, and exact wording before publication.
- Ask for participation first; final story approval comes later.
- Never send customer email.
