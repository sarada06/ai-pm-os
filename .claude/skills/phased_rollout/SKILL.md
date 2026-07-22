---
type: skill
name: phased_rollout
description: Methodology and required structure for the phased rollout stage of the AI PM OS pipeline
version: 1.0.0
tags: [ai-pm-os, phased_rollout]
---

# Phased Rollout Stage

## Purpose

Sequence the validated MVP out to full availability without betting the whole user base on day one.

## Required output structure

Write `artifacts/phased_rollout.md` with exactly these headings (the eval
matches them verbatim, case-insensitive):

```
# Phased Rollout: <Product Name>

## Rollout Phases
## Rollback Plan
## Guardrail Metrics
```

## Quality bar per section

- **Rollout Phases**: named phases (e.g. internal, 5% beta, 25%, 100%)
  each with an explicit advance/hold criterion tied to a guardrail metric.
- **Rollback Plan**: the actual mechanism to revert (feature flag, config,
  data migration reversibility) - not just 'we would roll it back.'
- **Guardrail Metrics**: metrics that, if they move the wrong way, halt the
  rollout - distinct from the success metrics being optimized for.

## Downstream dependency

Reads `validation.results` to decide whether rollout should proceed as planned or with modifications.

## Data sources

Guardrail Metrics should be checked live via the `kusto` MCP tool during
each phase - see `queries/kql/guardrail_check.kql` and
`queries/kql/error_rate_by_phase.kql` for starting templates. A phase's
advance/hold decision should cite the actual query result, not a general
sense that "things look fine."
