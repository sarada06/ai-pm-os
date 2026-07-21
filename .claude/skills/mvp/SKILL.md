---
type: skill
name: mvp
description: Methodology and required structure for the mvp stage of the AI PM OS pipeline
version: 1.0.0
tags: [ai-pm-os, mvp]
---

# Mvp Stage

## Purpose

Define the smallest thing that tests the riskiest assumption in the 'Now' horizon of the roadmap - not the smallest thing that's easy to build.

## Required output structure

Write `artifacts/mvp.md` with exactly these headings (the eval
matches them verbatim, case-insensitive):

```
# Mvp: <Product Name>

## Scope In
## Scope Out
## Success Criteria
```

## Quality bar per section

- **Scope In**: the minimum needed to test the core hypothesis - justify
  each inclusion by the assumption it tests, not by 'users will expect it.'
- **Scope Out**: explicitly named exclusions, especially ones a stakeholder
  is likely to push for. This section prevents scope creep in prd stage.
- **Success Criteria**: measurable, tied to the strategy's success metrics,
  with a stated threshold for what counts as validating vs invalidating the bet.

## Downstream dependency

Reads `roadmap` Now horizon and `strategy.strategic_bets`.
