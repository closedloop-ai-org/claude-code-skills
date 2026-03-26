# ClosedLoop AI Skills for Claude Code

Turn every customer conversation into structured product insights — inside Claude Code. These skills connect to your ClosedLoop AI data so you can deep-dive into any topic, get a weekly intelligence brief, talk to a synthetic customer persona, prepare for calls, or analyze the competitive landscape.

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
for skill in deep-dive weekly-brief synthetic-customer competitor-gap csm-prep pm-prep; do
  mkdir -p ~/.claude/skills/closedloop-$skill
  curl -so ~/.claude/skills/closedloop-$skill/SKILL.md \
    https://raw.githubusercontent.com/closedloop-ai-org/claude-code-skills/main/skills/$skill/SKILL.md
done
```

## Skills

### `/closedloop:deep-dive`

Deep-dive into any topic against all your product insights and strategic intelligence. Reads every matching insight, looks up CRM data for affected customers, loads key conversation transcripts, and synthesizes the complete picture.

```
/closedloop:deep-dive checkout flow
/closedloop:deep-dive API rate limits
```

### `/closedloop:weekly-brief`

Weekly intelligence brief. 4 parallel agents read ALL evidence behind every spike, deal blocker, churn risk, and competitor mention — then synthesize into a 40-line brief you can scan in 60 seconds.

```
/closedloop:weekly-brief
```

### `/closedloop:synthetic-customer`

Talk to any customer or segment as an AI persona built from their actual call transcripts, product feedback, CRM data, and public research. The persona knows what they said, how they talk, and what frustrates them.

```
/closedloop:synthetic-customer Acme Corp
/closedloop:synthetic-customer Enterprise customers
```

### `/closedloop:competitor-gap`

Competitive intelligence from customer conversations — threat ranking with 4-period trend analysis, feature gaps, your advantages, and actual call dialogue. Not desk research — real customer voice.

```
/closedloop:competitor-gap
/closedloop:competitor-gap monthly
```

### `/closedloop:csm-prep`

90-second pre-call brief for CSMs and account managers. Headline, landmines, what changed, top concerns in their own words, open threads, and how many other customers share the same pain.

```
/closedloop:csm-prep Acme Corp
```

### `/closedloop:pm-prep`

Discovery brief for product managers. Learning goals, knowledge gaps, data-grounded Mom Test questions, adaptive cross-customer positioning, workaround analysis, and segment context. Turns a customer call into a research instrument.

```
/closedloop:pm-prep Acme Corp
```

## Requirements

- [Claude Code](https://claude.ai/code)
- [ClosedLoop AI](https://closedloop.sh) account with connected data sources (Gong, Intercom, Fireflies, etc.)
- ClosedLoop AI MCP configured (see Prerequisites above)
