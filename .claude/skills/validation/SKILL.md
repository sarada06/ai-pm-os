---
type: skill
name: validation
description: Methodology and required structure for the validation stage of the AI PM OS pipeline
version: 1.0.0
tags: [ai-pm-os, validation]
---

# Validation Stage

## Purpose

Test the MVP's core hypothesis against real usage or real users before committing to a full rollout.

## Required output structure

Write `artifacts/validation.md` with exactly these headings (the eval
matches them verbatim, case-insensitive):

```
# Validation: <Product Name>

## Hypotheses
## Test Plan
## Results
```

## Quality bar per section

- **Hypotheses**: pulled directly from the MVP's success criteria, stated
  so they can be falsified.
- **Test Plan**: concrete method (beta cohort, A/B test, usability sessions),
  sample size or duration, and the specific decision each result would drive.
- **Results**: what actually happened - if this stage runs before real data
  exists, this section should say so explicitly rather than being invented.

## Downstream dependency

Reads `mvp.success_criteria` to define what's being tested.
