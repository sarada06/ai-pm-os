---
type: skill
name: strategy
description: Methodology and required structure for the strategy stage of the AI PM OS pipeline
version: 1.0.0
tags: [ai-pm-os, strategy]
---

# Strategy Stage

## Purpose

Convert discovery's opportunity areas into a small number of committed bets with clear success criteria - the strategy is what you say no to as much as what you say yes to.

## Required output structure

Write `artifacts/strategy.md` with exactly these headings (the eval
matches them verbatim, case-insensitive):

```
# Strategy: <Product Name>

## Strategic Bets
## Success Metrics
## Competitive Positioning
## Constraints
```

## Quality bar per section

- **Strategic Bets**: 2-4 bets max. Each should be a hypothesis
  ('if we do X, we believe Y will happen because Z'), not a feature list.
- **Success Metrics**: leading indicators tied to the vision's north star
  metric, not vanity metrics.
- **Competitive Positioning**: where this fits relative to alternatives
  (including 'do nothing' / current workaround), not just named competitors.
- **Constraints**: real limits - budget, timeline, technical, regulatory -
  that shape what's feasible.

## Downstream dependency

Reads `discovery.opportunity_areas` and `vision.north_star_metric`.
