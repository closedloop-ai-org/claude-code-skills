# ClosedLoop AI Skills for Claude Code

Turn every customer conversation into structured product insights — inside Claude Code. These skills connect to your ClosedLoop AI data so you can deep-dive into any topic, get a weekly intelligence brief, talk to a synthetic customer persona, prepare for calls, analyze the competitive landscape, find customer proof and references, or send the ClosedLoop AI team feedback about the platform.

## Prerequisites

Connect the ClosedLoop AI MCP before installing skills:

**US workspaces:**
```bash
claude mcp add --transport http closedloop-ai https://mcp.closedloop.sh
```

**EU workspaces:**
```bash
claude mcp add --transport http closedloop-ai https://eu.mcp.closedloop.sh
```

Restart Claude Code, select `closedloop-ai` from `/mcp`, and authorize.

Full setup guide: https://closedloop.sh/docs/mcp-server/overview

## Manual Install

```bash
for skill in closedloop-deep-dive closedloop-weekly-brief closedloop-synthetic-customer \
  closedloop-competitor-gap closedloop-csm-prep closedloop-pm-prep closedloop-sales-playbook \
  closedloop-ship-notify closedloop-watch closedloop-send-feedback \
  closedloop-product-ambassadors closedloop-product-ambassador-outreach \
  closedloop-customer-proof closedloop-customer-proof-outreach closedloop-sales-proof \
  closedloop-reference-customers closedloop-case-study-scout closedloop-proof-permissions; do
  mkdir -p ~/.claude/skills/$skill
  curl -fso ~/.claude/skills/$skill/SKILL.md \
    https://raw.githubusercontent.com/closedloop-ai-org/claude-code-skills/main/skills/$skill/SKILL.md
done
```

## Skills

### `/closedloop-deep-dive`

Deep-dive into any topic against all your product insights and strategic intelligence. Reads every matching insight, looks up CRM data for affected customers, loads key conversation transcripts, and synthesizes the complete picture.

```
/closedloop-deep-dive checkout flow
/closedloop-deep-dive API rate limits
```

### `/closedloop-weekly-brief`

Weekly intelligence brief. 4 parallel agents read ALL evidence behind every spike, deal blocker, churn risk, and competitor mention — then synthesize into a 40-line brief you can scan in 60 seconds.

```
/closedloop-weekly-brief
```

### `/closedloop-synthetic-customer`

Talk to any customer or segment as an AI persona built from their actual call transcripts, product feedback, CRM data, and public research. The persona knows what they said, how they talk, and what frustrates them.

```
/closedloop-synthetic-customer Acme Corp
/closedloop-synthetic-customer Enterprise customers
```

### `/closedloop-competitor-gap`

Competitive intelligence from customer conversations — threat ranking with 4-period trend analysis, feature gaps, your advantages, and actual call dialogue. Not desk research — real customer voice.

```
/closedloop-competitor-gap
/closedloop-competitor-gap monthly
```

### `/closedloop-csm-prep`

90-second pre-call brief for CSMs and account managers. Headline, landmines, what changed, top concerns in their own words, open threads, and how many other customers share the same pain.

```
/closedloop-csm-prep Acme Corp
```

### `/closedloop-pm-prep`

Discovery brief for product managers. Learning goals, knowledge gaps, data-grounded Mom Test questions, adaptive cross-customer positioning, workaround analysis, and segment context. Turns a customer call into a research instrument.

```
/closedloop-pm-prep Acme Corp
```

### `/closedloop-product-ambassadors`

Find customers a product team should involve for a product area or feature. Returns action-specific PM candidates, evidence, next steps, and follow-up actions for design partners, early validators, internal champions, and expert reviewers.

```
Find product ambassadors for memberships.
Find beta users for API exports.
```

### `/closedloop-product-ambassador-outreach`

Draft grounded outreach for one selected product ambassador candidate. Uses the selected candidate and follow-up action returned by product ambassador results to prepare a customer email, intro request, evidence packet, and questions to ask.

```
Draft outreach for candidate 2.
Write an invite for the selected beta user.
```

### `/closedloop-customer-proof`

Find marketing-ready customer proof from ClosedLoop AI evidence: quotes, testimonials, case-study candidates, customer love, launch proof, social proof, adoption stories, and ROI/value proof. Keeps public proof separate from PM product ambassador workflows.

```
Find customer quotes about memberships.
Find case study candidates for API exports.
```

### `/closedloop-customer-proof-outreach`

Draft permission outreach for one selected customer proof candidate. Use after `closedloop-customer-proof` returns a candidate and follow-up action.

```text
Draft permission outreach for candidate 1
Prepare a case-study ask for Quentin from Quote Hotel
```

### `/closedloop-send-feedback`

Send feedback about ClosedLoop AI itself: bugs, feature requests, missing or low-quality data, confusing results, or praise.

```text
Send feedback that this brief missed recent call data
```

### `/closedloop-sales-playbook`

Pain-point sales talk tracks from real customer quotes, workarounds, and competitor gaps. General playbook per topic, or micro-targeted for a specific customer with social proof from their peers.

```
/closedloop-sales-playbook integration pain points
/closedloop-sales-playbook Acme Corp
```

### `/closedloop-ship-notify`

Find every customer who asked for something you just shipped and draft personalized launch follow-up. Uses `find_launch_audience`; draft only — it never sends customer email. Closes the feedback loop — the thing 95% of companies fail to do.

```
/closedloop-ship-notify CSV export feature
/closedloop-ship-notify API rate limit fix
```

### `/closedloop-watch`

Set up a notification watch — get alerted (Slack / Teams / in-app) when something crosses a threshold in your ClosedLoop AI product insights.

```
/closedloop-watch alert me when bug insights about checkout spike
```

### `/closedloop-sales-proof`

Build a sales proof packet for a prospect conversation: short snippets, customer examples, permitted/unpermitted use caveats, and follow-up asks — grounded in real customer evidence.

```text
Build sales proof for a museum prospect worried about reconciliation
```

### `/closedloop-reference-customers`

Find customers sales can safely ask for a private reference call about a topic — best-fit candidates, why they match, owner route, suggested ask, and topics to avoid.

```text
Who can we ask for a reference call about reporting?
```

### `/closedloop-case-study-scout`

Find customers with enough depth for a full story, not just a quote — narrative angle, measurable outcomes, interview questions, and missing proof.

```text
Find case study candidates for onboarding improvements
```

### `/closedloop-proof-permissions`

Log and track proof permission requests for a selected proof candidate. Logs an internal record only — it never sends customer email.

```text
Create a permission request for the selected candidate
```

## Requirements

- [Claude Code](https://claude.ai/code)
- [ClosedLoop AI](https://closedloop.sh) account with connected data sources (Gong, Intercom, Fireflies, etc.)
- ClosedLoop AI MCP configured (see Prerequisites above)
