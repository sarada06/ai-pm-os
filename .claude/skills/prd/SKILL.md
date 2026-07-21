---
type: skill
name: prd
description: Methodology and required structure for the prd stage of the AI PM OS pipeline
version: 1.0.0
tags: [ai-pm-os, prd]
---

# Prd Stage

## Purpose

Translate the MVP scope into something engineering can build without guessing - the highest-detail artifact in the pipeline.

## Required output structure

Write `artifacts/prd.md` with exactly these headings (the eval
matches them verbatim, case-insensitive):

```
# Prd: <Product Name>

## Requirements
## User Stories
## Edge Cases
## Open Questions
```

## Quality bar per section

- **Requirements**: functional requirements traced to MVP scope-in items,
  written as testable statements, not vague goals.
- **User Stories**: standard 'as a [user], I want [goal], so that [reason]'
  format, covering the primary persona's core flow end to end.
- **Edge Cases**: explicitly enumerated - empty states, error states,
  permission boundaries, concurrent-use conflicts.
- **Open Questions**: anything genuinely unresolved - do not silently
  resolve ambiguity by picking an arbitrary answer; surface it here instead.

## Downstream dependency

Reads `mvp.scope_in` and `mvp.scope_out` as the requirements boundary.
