---
type: skill
name: outcomes
description: Methodology and required structure for the outcomes stage of the AI PM OS pipeline
version: 1.0.0
tags: [ai-pm-os, outcomes]
---

# Outcomes Stage

## Purpose

Close the loop - did this move the north star metric from the vision stage, what did we learn, and what should the next strategic cycle bet on.

## Required output structure

Write `artifacts/outcomes.md` with exactly these headings (the eval
matches them verbatim, case-insensitive):

```
# Outcomes: <Product Name>

## Results vs North Star
## Learnings
## Next Bets
```

## Quality bar per section

- **Results vs North Star**: honest comparison against the vision stage's
  north star metric, with the actual number if available, or an explicit
  note that it's too early to measure.
- **Learnings**: what surprised you - about users, about the strategy's
  assumptions, about execution. Genuine learnings, not a victory lap.
- **Next Bets**: candidate strategic bets for the next cycle, feeding back
  into a new strategy stage - this is where the pipeline loops.

## Downstream dependency

Reads `vision.north_star_metric` to ground the final comparison.

## Data sources

Results vs North Star should be backed by an actual query against the
metric defined in the vision stage - use `queries/sql/north_star_metric_trend.sql`
via the `sql` MCP tool, or the equivalent in `kusto` if the metric lives in
telemetry rather than a warehouse table. If it's genuinely too early to
measure, say that explicitly rather than estimating.
