# AI PM OS

An agent/skill/MCP-orchestrated system that generates the artifacts a product
manager produces across a product's lifecycle - vision, discovery, strategy,
roadmap, MVP, PRD, validation, phased rollout, outcomes - with automated
evals gating each stage before the next begins.

Built as a **Claude Code project**: each pipeline stage is a subagent backed
by a skill (methodology + required structure), orchestrated by a top-level
`orchestrator` subagent, checked by a Python eval harness after every stage.

## How it works

```
vision -> discovery -> strategy -> roadmap -> mvp -> prd -> validation -> phased_rollout -> outcomes
```

This is a **strict, gated pipeline**: a stage's artifact must pass its eval
(structural completeness + optional LLM-judge quality check) before the
pipeline advances. If it fails, the stage agent revises and re-submits (up
to `max_attempts`, configured per stage in `pipeline/stage_config.py`)
before the orchestrator stops and asks a human to intervene.

Every stage:
1. Reads `artifacts/context.json` - the single shared state object every
   prior stage has written into
2. Reads its own `.claude/skills/<stage>/SKILL.md` for methodology and the
   exact section headings it must produce
3. Writes `artifacts/<stage>.md`
4. Gets scored by `evals/<stage>_eval.py` via `python -m pipeline.runner eval <stage>`
5. On pass, the orchestrator updates `context.json` and moves to the next stage

## Repo layout

```
.claude/
  agents/         Claude Code subagents - one orchestrator + one per stage
  skills/         SKILL.md per stage - methodology, required headings, quality bar
schemas/
  product_context.schema.json   Shape of the shared state object
evals/
  rubric_base.py  Shared rubric engine (deterministic checks + optional LLM judge)
  <stage>_eval.py One eval per stage
pipeline/
  state.py        Load/save/update context.json
  stage_config.py Ordered stage definitions, thresholds, max_attempts
  runner.py       CLI: init / eval <stage> / status
artifacts/        Generated output lands here (gitignored except .gitkeep)
examples/         A worked sample vision.md + context.json for reference
tests/            Unit tests for state, stage config, and the vision eval
```

## Getting started

**Run the full pipeline through Claude Code:**

```
"Run the orchestrator for a new product: <name>, <one-liner>"
```

The orchestrator subagent will initialize context, invoke each stage
subagent in order, run the eval gate after each, and keep you posted.

**Run one stage directly:**

```
"Use the vision-agent to draft a vision doc for <product>"
```

**Check pipeline status any time (from a terminal, or ask Claude to run it):**

```bash
python -m pipeline.runner status
```

**Run the eval for a stage manually** (useful while iterating on a skill or
an artifact by hand):

```bash
python -m pipeline.runner init --product-name "PulseBoard" --one-liner "..."
python -m pipeline.runner eval vision --artifact examples/sample_vision.md
```

## Adding the optional LLM-judge quality check

The deterministic structural checks (required sections present, no
placeholder text, product name referenced) run with zero setup. To turn on
the qualitative LLM-judge criterion (currently wired into `vision_eval.py`
as the reference implementation - copy the pattern into other stage evals
as they mature):

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-..."
```

Without a key set, the judge criterion auto-passes and the eval falls back
to the deterministic checks only - the pipeline still runs end to end.

## Wiring up MCP tools

Add MCP servers your organization uses (Jira, Confluence, Linear, Slack,
analytics platforms) to your Claude Code MCP config, then reference them in
the relevant stage's subagent `tools:` frontmatter and skill instructions -
e.g. the `roadmap-agent` publishing to Jira, or `outcomes-agent` pulling
real metrics from an analytics MCP server instead of relying on the user to
paste numbers in.

## Status of this scaffold

- **Fully built and tested end-to-end**: the `vision` stage - skill, agent,
  eval (deterministic + LLM-judge pattern), and a passing/failing example
  in `examples/`.
- **Structurally scaffolded**: the remaining 8 stages have working agents,
  skills with real methodology, and deterministic evals - but haven't been
  run against real generated output yet. Expect to tune each stage's
  rubric (word minimums, required sections) once you see real artifacts
  come through.
- **Not yet built**: MCP tool wiring (config is a placeholder), the
  structured-field extraction step that populates `context.json`'s
  per-stage objects (the orchestrator prompt describes this; no code
  enforces it yet).
