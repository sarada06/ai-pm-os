# AI PM OS - Agent Instructions

This repo is a gated, 9-stage pipeline that generates the artifacts a
product manager produces across a product's lifecycle: vision, discovery,
strategy, roadmap, mvp, prd, validation, phased_rollout, outcomes.

This file is read by Codex and used as a fallback by other agentic tools
that don't have native "subagent" or "skill" concepts (Claude Code has both
natively - see `.claude/agents/` and `.claude/skills/` for the richer
version of these same instructions).

## How to work in this repo

1. **Read the methodology before writing an artifact.** Every stage has a
   `SKILL.md` at `.claude/skills/<stage>/SKILL.md` - this is not
   Claude-specific, it's just a markdown file. It defines the exact section
   headings required (the eval matches them verbatim) and the quality bar
   for that stage. Read it before drafting anything.

2. **Check the shared state first.** `artifacts/context.json` is the single
   source of truth for everything prior stages have established. Run
   `python -m pipeline.runner status` to see the current stage and history.
   If it doesn't exist yet, initialize it:
   `python -m pipeline.runner init --product-name "<name>" --one-liner "<one-liner>"`

3. **Write the artifact** to `artifacts/<stage>.md` using the skill's exact
   headings.

4. **Run the eval gate** - this is not optional, and don't decide pass/fail
   yourself:
   `python -m pipeline.runner eval <stage> --artifact artifacts/<stage>.md --attempt <n>`
   This also automatically extracts the artifact's sections into
   `context.json`'s structured per-stage object (see `pipeline/extract.py` -
   deterministic markdown parsing, no LLM call).

5. **On FAIL**, read which criteria failed in the eval's printed report,
   revise the same file, and re-run with `--attempt` incremented (stages
   have a `max_attempts` in `pipeline/stage_config.py`, default 3).

6. **On PASS**, move to the next stage in order:
   vision -> discovery -> strategy -> roadmap -> mvp -> prd -> validation -> phased_rollout -> outcomes

## Research inputs and domain context

`inputs/interviews/`, `inputs/customer_feedback/`, and
`inputs/secondary_research/` hold raw primary/secondary research - read
what's relevant before writing `discovery` (or any stage making a factual
claim), and cite it inline with `[source: inputs/<folder>/<file>.md]` (see
`inputs/README.md`). `inputs/sme_notes/` holds domain-expert context that
gets rolled into `context.json`'s `domain_context` field via
`python -m pipeline.runner init --domain-context-file <path>` (or
`set-domain-context` later) - every stage should write in that domain's
actual vocabulary, not generic product language.

## Strategy: options and grading

The `strategy` stage isn't a single write-up - it generates 2-4 real
alternative approaches, scores them in a markdown table against weighted
criteria (impact, feasibility, time-to-value, risk, etc.), and only then
commits to strategic bets. `python -m pipeline.runner eval strategy` runs
`pipeline/option_scoring.py` automatically and stores the ranking in
`context.json`. If the committed bets aren't the top-scoring option, the
artifact should say why - don't silently override the numbers. See
`.claude/skills/strategy/SKILL.md` for the exact table format required.

## Data-sourcing MCP tools

Several stages pull real data instead of relying on the user to paste
numbers in. Three MCP servers are configured (see `docs/mcp-setup.md` for
setup and required environment variables):

- **ado** (Azure DevOps) - existing epics/backlog for `discovery` and
  `roadmap`, related work items and historical bugs for `prd`
- **sql** (SQL Server) - product usage/metrics tables for `validation` and
  `outcomes`
- **kusto** (Azure Data Explorer / KQL) - telemetry and guardrail metrics
  for `validation`, `phased_rollout`, and `outcomes`

Parameterized query templates for common PM analysis (adoption, retention,
guardrail thresholds, north-star tracking) are in `queries/sql/` and
`queries/kql/` - read `queries/README.md` before writing a query from
scratch.

## Sharing artifacts with stakeholders

When asked to share, send, post, or distribute an artifact, use the `slack`
MCP tool per `.claude/skills/sharing/SKILL.md`: confirm the target channel
and a one-line preview of the message before sending anything, write a
short summary rather than pasting raw markdown into chat, and use a Slack
Canvas for anything longer than a couple of paragraphs. Log every share
with `python -m pipeline.runner record-share --artifact <path> --channel <channel>`
so there's an audit trail. This isn't a gated pipeline stage - it can
happen after any stage, on demand.

## Rules

- Never skip a stage's eval, even if the artifact looks fine.
- Never invent data for validation/outcomes when a real MCP data source is
  configured and reachable - query it. If it isn't reachable, say so
  explicitly in the artifact rather than fabricating numbers.
- If asked to jump stages out of order, this pipeline is gated by design -
  confirm with the user before skipping ahead, since earlier context may be
  missing.
