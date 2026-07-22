---
type: skill
name: roadmap
description: Methodology and required structure for the roadmap stage of the AI PM OS pipeline
version: 1.0.0
tags: [ai-pm-os, roadmap]
---

# Roadmap Stage

## Purpose

Sequence the strategic bets into a time-horizon roadmap. Now/Next/Later over fixed dates - dates go stale, sequencing logic doesn't.

## Required output structure

Write `artifacts/roadmap.md` with exactly these headings (the eval
matches them verbatim, case-insensitive):

```
# Roadmap: <Product Name>

## Now
## Next
## Later
```

## Quality bar per section

- **Now**: what's committed and in progress, tied to a specific strategic bet.
- **Next**: what's planned once Now ships, with the dependency reasoning
  stated (why this comes after, not before).
- **Later**: directionally likely but explicitly not committed - frame as
  hypotheses to revisit, not promises.
- Every horizon should name which strategic bet(s) it serves - a roadmap
  item with no traceable bet behind it is a smell.

## Downstream dependency

Reads `strategy.strategic_bets` to make sure every horizon traces back to a bet.

## Data sources

Cross-check the `Now` horizon against the `ado` MCP tool's current
iteration/backlog before finalizing - if something is already in flight or
already shipped in Azure DevOps, the roadmap should reflect that rather
than duplicate it.
