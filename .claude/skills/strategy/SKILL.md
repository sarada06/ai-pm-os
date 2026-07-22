---
type: skill
name: strategy
description: Methodology and required structure for the strategy stage of the AI PM OS pipeline - generate multiple strategic options, grade them against weighted criteria, and commit to strategic bets, success metrics, competitive positioning, and constraints
version: 2.0.0
tags: [ai-pm-os, strategy, decision-making]
---

# Strategy Stage

## Purpose

Convert discovery's opportunity areas into a committed strategy - but
before committing, generate real alternatives and grade them. A strategy
artifact that only ever shows one option was never actually a decision; it
was a foregone conclusion written up after the fact. This stage exists to
make the tradeoffs explicit and auditable.

## Required output structure

Write `artifacts/strategy.md` with exactly these headings (the eval
matches them verbatim, case-insensitive):

```
# Strategy: <Product Name>

## Strategic Options
## Option Evaluation
## Strategic Bets
## Success Metrics
## Competitive Positioning
## Constraints
```

## Strategic Options

Generate 2-4 genuinely different approaches to the opportunity areas from
discovery - not variations on the same idea. Each option gets a short name
and 1-2 sentence description. Good option sets usually span a spectrum like
"narrow and fast to ship" vs. "broader and more defensible" vs. "the
expensive but complete answer" - if all your options would take the same
effort and carry the same risk, you haven't actually generated alternatives.

Format each as `- **Option A: Short Name** - description...` and refer to
that exact name (e.g. "Option A: Short Name") in the Option Evaluation
table's column headers, so scores map back to the right option. Keep the
bolded name itself free of additional colons (the extractor splits on the
first colon after the bullet) - put the name after "Option A:" and let the
colon there do the separating, rather than nesting another one inside it.

## Option Evaluation

A markdown table scoring every option from Strategic Options against a
shared set of weighted criteria. This is the mechanism that turns "best
approach" from a vibe into a number - `pipeline/option_scoring.py` parses
this table and recomputes the weighted totals itself (don't trust a
hand-typed total row; the eval will recompute and flag if it disagrees).

**Format** (exact - the parser depends on this shape):

```
| Criterion (weight) | Option A | Option B | Option C |
|---|---|---|---|
| Impact on North Star (x3) | 4 | 5 | 5 |
| Feasibility (x2, lower is better) | 2 | 2 | 5 |
| Time to Value (x2) | 4 | 5 | 1 |
| Risk (x1, lower is better) | 2 | 2 | 5 |
| **Weighted Total** | 30 | 34 | 20 |
```

Rules:
- First column: criterion name, weight in `(x<number>)`, defaults to 1 if
  omitted. Add `, lower is better` inside the same parentheses for
  criteria like Risk or Cost where a *lower* raw score is actually better
  (the parser inverts these before weighting).
- Score every cell 1-5.
- Default criteria if the user hasn't specified their own: **Impact on
  North Star**, **Feasibility** (lower is better), **Time to Value**,
  **Risk** (lower is better), **Strategic Fit** with the vision.
- The trailing `Weighted Total` row is optional and purely for human
  readability while drafting - it is never trusted by the eval, which
  recomputes from the raw scores. If your hand-typed total disagrees with
  the recomputed one, trust the recomputed one and fix your arithmetic (or
  your scores).

## Quality bar per section

- **Strategic Options**: 2-4 real alternatives, not near-duplicates.
- **Option Evaluation**: table parses (exact format above), at least 2
  options scored across at least 2 criteria.
- **Strategic Bets**: 2-4 bets max, each a hypothesis ("if we do X, we
  believe Y will happen because Z"), drawn from the **top-scoring option**
  in Option Evaluation. If you're committing to a bet that *didn't* score
  highest, say so explicitly and explain the judgment call - don't just
  silently override the numbers.
- **Success Metrics**: leading indicators tied to the vision's north star
  metric, not vanity metrics.
- **Competitive Positioning**: where this fits relative to alternatives
  (including "do nothing" / current workaround), not just named competitors.
- **Constraints**: real limits - budget, timeline, technical, regulatory -
  that shape what's feasible.

## Data sources

Ground Competitive Positioning and Constraints in `inputs/secondary_research/`
where available (market sizing, competitor teardowns) - see
`inputs/README.md` for the citation convention. Also honor `domain_context`
in `context.json` (SME notes) so Constraints reflects real regulatory/
operational limits for this domain, not generic ones.

## Downstream dependency

`roadmap` reads `strategy.strategic_bets` (the committed direction) and can
also check `strategy.option_scores` in context.json to see how close the
decision was - a narrow margin between top options is worth flagging if the
roadmap later needs to pivot.
