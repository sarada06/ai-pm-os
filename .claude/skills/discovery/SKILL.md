---
type: skill
name: discovery
description: Methodology and required structure for the discovery stage of the AI PM OS pipeline
version: 1.0.0
tags: [ai-pm-os, discovery]
---

# Discovery Stage

## Purpose

Turn the vision's problem statement into validated (or invalidated) understanding of users, their workflows, and where the real opportunity lies - before committing to a strategy.

## Required output structure

Write `artifacts/discovery.md` with exactly these headings (the eval
matches them verbatim, case-insensitive):

```
# Discovery: <Product Name>

## Research Questions
## Key Insights
## Personas
## Opportunity Areas
```

## Quality bar per section

- **Research Questions**: specific, answerable questions derived from the vision's
  problem statement - not generic ('what do users want?').
- **Key Insights**: findings, each tied to evidence (interview, data, observed
  behavior) - not opinions dressed as insights.
- **Personas**: 1-3 personas max, each with their actual current workaround
  for the problem, not just demographics.
- **Opportunity Areas**: prioritized list of where to focus, explicitly
  connected back to the vision's target users.

## Downstream dependency

Reads `vision.problem_statement` and `vision.target_users` from context to scope research questions.

## Data sources

Before writing Research Questions or Opportunity Areas from scratch, check
the `ado` MCP tool (Azure DevOps) for existing backlog items, past feature
requests, or bug patterns in the relevant area - real signal beats invented
research questions. See `docs/mcp-setup.md` for connecting it.
