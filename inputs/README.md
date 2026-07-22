# Research inputs

Raw primary and secondary research, plus SME domain context, lives here.
Stage agents (mainly `discovery`, but any stage can) read these before
writing an artifact, so problem statements, personas, insights, and edge
cases are grounded in real evidence rather than invented from a one-liner.

```
inputs/
  interviews/           Stakeholder/user interview notes (one file per interview)
  customer_feedback/     Support tickets, survey verbatims, app reviews, NPS comments
  secondary_research/    Market reports, analyst research, competitor teardowns
  sme_notes/              Domain expert context - terminology, regulatory
                         constraints, "how this industry actually works"
```

Each folder has a `TEMPLATE.md` - copy it, fill it in, name the copy
something identifiable (`priya_planner_2026-07-10.md`, not `interview1.md`).

## Citation convention

When a stage artifact's claim comes from one of these files, tag it inline:

```
- Planners check 3-5 spreadsheets before every S&OP meeting [source: inputs/interviews/priya_planner_2026-07-10.md]
```

`discovery_eval.py` checks for at least one citation like this across the
artifact (lenient - it's a nudge toward evidence, not a hard requirement per
bullet). Downstream stages and a human reviewer can trace any claim back to
where it came from.

## Domain context (SME know-how)

`inputs/sme_notes/` is different from the other three folders: it's not
observations *about users*, it's expertise *about the domain* - regulatory
constraints, industry jargon, what "good" looks like by industry standard,
common failure modes specific to this space. This gets rolled up into
`context.json`'s top-level `domain_context` field so every stage (not just
discovery) can write in language that sounds like it knows the domain,
rather than generic SaaS-speak.

Set it once, or update any time:

```bash
python -m pipeline.runner init --product-name "PulseBoard" \
  --one-liner "..." --domain-context-file inputs/sme_notes/supply_chain_basics.md

# or update later, without re-initializing:
python -m pipeline.runner set-domain-context --file inputs/sme_notes/supply_chain_basics.md
```
