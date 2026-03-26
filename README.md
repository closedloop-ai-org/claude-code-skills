# ClosedLoop AI Skills for Claude Code

Turn every customer conversation into structured product insights — inside Claude Code. These skills connect to your ClosedLoop AI data so you can deep-dive into any topic and get the complete picture: every customer quote, pain point, business impact, workaround, and competitive signal extracted from your conversations.

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

## Install

```
/plugin install closedloop-skills
```

## Skills

### `/closedloop:deep-dive`

Deep-dive into any topic against all your product insights and strategic intelligence. Reads every matching insight and signal, looks up CRM data for affected customers, and synthesizes the complete picture.

```
/closedloop:deep-dive dynamic pricing
/closedloop:deep-dive SSO support
/closedloop:deep-dive mobile app reliability
```

**What you get:**
- Synthesis of the real underlying problem (after reading ALL evidence)
- Every customer quote, grouped by sub-theme
- Business impact — deal blockers, churn risks, revenue at stake
- Affected customers with CRM data — segment, industry, deals
- Competitive context — which competitors customers mention and why
- Workarounds — what customers do today to cope
- Strategic signals — satisfaction, churn, decision criteria
- Evidence gaps — what the data doesn't cover

### More skills coming soon

- `/closedloop:sales-playbook` — Pain-point sales talk tracks from real customer quotes
- `/closedloop:ship-notify` — Find customers who asked for something you shipped
- `/closedloop:customer-prep` — Pre-call intelligence brief
- `/closedloop:competitor-gap` — Competitive intel from conversations
- `/closedloop:weekly-brief` — Weekly digest of what changed

## Requirements

- [Claude Code](https://claude.ai/code)
- [ClosedLoop AI](https://closedloop.sh) account with connected data sources (Gong, Intercom, Fireflies, etc.)
- ClosedLoop AI MCP configured (see Prerequisites above)
