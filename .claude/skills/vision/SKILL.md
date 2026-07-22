---
type: skill
name: vision
description: Methodology and required structure for the product vision stage of the AI PM OS pipeline - problem statement, target users, vision statement, north star metric, non-goals
version: 1.0.0
tags: [ai-pm-os, vision, north-star]
---

# Vision Stage

## Purpose

Establish the foundation everything else in the pipeline builds on: what
problem are we solving, for whom, what does winning look like, and what are
we deliberately not doing. A weak vision produces a weak everything-after -
this is the highest-leverage stage to get right.

## Required output structure

Write `artifacts/vision.md` with exactly these headings (the eval matches
them verbatim, case-insensitive):

```
# Vision: <Product Name>

## Problem Statement
## Target Users
## Vision Statement
## North Star Metric
## Non-Goals
```

## Quality bar per section

- **Problem Statement**: specific and falsifiable. Should name who has the
  problem, what they currently do instead, and why that's costly (time,
  money, risk, trust). Reject "there is no good way to do X" without saying
  what people do today and why it hurts. Minimum ~25 words of substance.
- **Target Users**: named segments, not "everyone." If there are multiple
  segments, note which is primary.
- **Vision Statement**: one to three sentences, concrete enough that you
  could tell if a feature is on-vision or off-vision from it. Avoid
  generic phrases like "best-in-class" or "seamless experience" without
  something specific underneath them.
- **North Star Metric**: a single metric, not a list. It should move when
  users get real value, not just when they use the product more. State
  the direction (increase/decrease) and roughly how it would be measured.
- **Non-Goals**: at least one or two explicit exclusions. This is often
  the most valuable section for preventing scope creep later - don't skip it.

## Common failure modes to avoid

- Vision statements that could apply to any product ("empower users to
  achieve their goals faster")
- North star metrics that are vanity metrics (signups, page views) rather
  than value metrics
- Missing non-goals entirely, which the eval will flag as a thin section

## Downstream dependency

The `discovery` stage will reference `vision.problem_statement` and
`vision.target_users` to scope research questions. Keep these specific
enough to be useful, not just inspirational.

## Data sources

If `inputs/sme_notes/` or `context.json`'s `domain_context` field is
already populated (see `inputs/README.md`), use the domain's real
vocabulary and constraints when framing the Problem Statement - even at
this earliest stage, "planners reconcile S&OP forecasts" reads more
credibly to a domain expert than "users manage business data."
