# AI PM OS

**Why this exists:** Product managers write the same
nine documents on every product — a vision, some research, a strategy, a
roadmap, a spec, a test plan, a rollout plan, a results overview and it's
easy for the later documents to drift from the earlier ones without anyone
noticing until much later. 
This project makes an AI write those nine
documents and checks its own work at every step: each document has to
cite real evidence, pass a quality check and clearly connect to the
document before it, before the next one gets started. The result is a
paper trail you can actually follow, from "here's the problem" all the way
to "here's what happened after we shipped it."

![AI PM OS pipeline: nine stages gated across three phases - Foundation, Build, and Prove It](docs/images/pipeline-diagram.png)

Built as a **Claude Code project**: each pipeline stage is a subagent
backed by a skill (methodology + required structure), orchestrated by a
top-level `orchestrator` subagent, checked by a Python eval harness after
every stage. It also runs from Codex, GitHub Copilot, and Gemini CLI - see
[Using this repo from other tools](#5-using-this-repo-from-codex-copilot-or-gemini).

## Contents

1. [How the pipeline works](#1-how-the-pipeline-works)
2. [Getting started](#2-getting-started)
3. [Repo layout](#3-repo-layout)
4. [Going deeper](#4-going-deeper) - LLM judge, research inputs, strategy
   grading, MCP tools and Slack sharing
5. [Using this repo from Codex, Copilot, or Gemini](#5-using-this-repo-from-codex-copilot-or-gemini)
6. [Status of this scaffold](#6-status-of-this-scaffold) - what's proven vs. what isn't yet

---

## 1. How the pipeline works

Nine stages run in a fixed order, and each one has to pass a quality check
before the next one is allowed to start:

```
vision -> discovery -> strategy -> roadmap -> mvp -> prd -> validation -> phased_rollout -> outcomes
```

**Step 1 - Read what's already known.** The stage reads
`artifacts/context.json`, the one shared file every earlier stage has
already written into, plus its own `.claude/skills/<stage>/SKILL.md` for
methodology and the exact section headings it has to produce.

**Step 2 - Write the artifact.** The stage produces `artifacts/<stage>.md`
using those exact headings.

**Step 3 - Get graded.** `python -m pipeline.runner eval <stage>` runs that
stage's automated eval - checking things like "does this section actually
exist and say something specific," "is a source cited," or (for the
strategy stage) "do the numbers in this scoring table actually add up."

**Step 4 - Pass or revise.** If the eval passes, the stage's answers get
parsed into `context.json` automatically (no LLM call - it's just markdown
parsing, see `pipeline/extract.py`), and the pipeline moves to the next
stage. If it fails, the stage revises and re-submits, up to a configurable
number of attempts (`max_attempts` in `pipeline/stage_config.py`) before a
human is asked to step in.

That's the whole loop, repeated nine times, with the record of every
attempt (pass, fail, score) kept in `context.json`'s history.

## 2. Getting started

**Option A - let the orchestrator run the whole thing:**

```
"Run the orchestrator for a new product: <name>, <one-liner>"
```

It will set up `context.json`, run each stage in order, grade each one,
and keep you posted as it goes.

**Option B - run just one stage:**

```
"Use the vision-agent to draft a vision doc for <product>"
```

**Option C - drive it from a terminal instead of asking Claude to:**

```bash
# 1. Create a new product
python -m pipeline.runner init --product-name "PulseBoard" --one-liner "..."

# 2. Grade a stage's artifact once it's written
python -m pipeline.runner eval vision --artifact examples/sample_vision.md

# 3. Check where things stand at any point
python -m pipeline.runner status
```

## 3. Repo layout

```
.claude/
  agents/         Claude Code subagents - one orchestrator + one per stage,
                  plus sharing-agent (on-demand, not part of the gated sequence)
  skills/         SKILL.md per stage - methodology, required headings, quality bar,
                  plus sharing/ (Slack posting conventions)
AGENTS.md         Cross-tool entrypoint (Codex reads this automatically; also
                  the reference other tools' entrypoint files are built from)
GEMINI.md         Same content, for Gemini CLI's auto-loaded context file
.github/
  copilot-instructions.md  Thin pointer to AGENTS.md, for GitHub Copilot
.mcp.json         Claude Code project-scoped MCP config (ado, sql, kusto, slack)
.vscode/mcp.json  Same 4 servers, VS Code/Copilot Agent Mode format
.gemini/settings.json  Same 4 servers, Gemini CLI format
.codex/config.toml     Same 4 servers, Codex CLI format (TOML)
inputs/
  interviews/, customer_feedback/, secondary_research/, sme_notes/
                  Raw research + domain expertise (see inputs/README.md)
docs/
  images/pipeline-diagram.png  README hero visual
  mcp-setup.md         Setting up the ado/sql/kusto/slack MCP servers
  cross-tool-setup.md  Running this pipeline from Codex, Copilot, or Gemini
queries/
  sql/, kql/      Parameterized query templates for adoption, retention,
                  guardrails, and north-star tracking (see queries/README.md)
schemas/
  product_context.schema.json   Shape of the shared state object
evals/
  rubric_base.py  Shared rubric engine (deterministic checks + optional LLM judge)
  <stage>_eval.py One eval per stage
pipeline/
  state.py        Load/save/update context.json (incl. domain_context)
  stage_config.py Ordered stage definitions, thresholds, max_attempts
  extract.py      Parses each stage's markdown sections into context.json's
                   structured per-stage fields (deterministic, no LLM call)
  option_scoring.py  Parses and grades the strategy stage's Option
                     Evaluation table - weighted totals, ranking, top option
  runner.py       CLI: init / eval <stage> / status / extract <stage> /
                  set-domain-context / record-share
artifacts/        Generated output lands here (gitignored except .gitkeep)
examples/         Worked sample artifacts + context.json for reference
tests/            Unit tests for state, stage config, extraction, and the vision eval
```

## 4. Going deeper

Five things worth understanding beyond the basic loop above - skip to
whichever's relevant.

### 4.1 Turning on the optional AI quality check

The eval gate above runs for free with zero setup - it's just checking
structure (are the right sections there, do they say something specific,
is a source cited). There's also an optional *qualitative* check, where
Claude itself judges whether an artifact is actually good, not just
well-formed. It's wired into `vision_eval.py` today as the reference
example; the same pattern can be copied into the other 8 stage evals.

To turn it on:

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-..."
```

Without a key set, that check quietly passes and the pipeline falls back
to the structural checks only - nothing breaks either way.

### 4.2 Grounding artifacts in real research, not assumptions

Four folders under `inputs/` hold raw material the pipeline reads before
writing anything:

| Folder | What goes in it |
|---|---|
| `inputs/interviews/` | Notes from stakeholder or user interviews |
| `inputs/customer_feedback/` | Support tickets, survey verbatims, app reviews |
| `inputs/secondary_research/` | Market reports, analyst research, competitor teardowns |
| `inputs/sme_notes/` | Domain-expert context - terminology, regulations, industry norms |

The first three get cited inline in artifacts as `[source: inputs/<folder>/<file>.md]`
- the discovery stage's eval checks that at least one citation shows up
(a nudge toward evidence, not a strict per-bullet rule). The fourth,
`sme_notes/`, is different: it feeds `context.json`'s `domain_context`
field so *every* stage writes using the domain's real vocabulary instead of
generic product-speak:

```bash
# set it when you create the product...
python -m pipeline.runner init --product-name "PulseBoard" \
  --one-liner "..." --domain-context-file inputs/sme_notes/supply_chain_basics.md

# ...or update it later without starting over
python -m pipeline.runner set-domain-context --file inputs/sme_notes/some_notes.md
```

Full folder structure, templates, and the citation convention are in
`inputs/README.md`.

### 4.3 Strategy: several options, graded, not one opinion

The `strategy` stage doesn't just write up one direction. It generates 2-4
real alternatives, scores each one in a table against weighted criteria
(impact, feasibility, time-to-value, risk), and only then commits to a set
of strategic bets:

```bash
python -m pipeline.option_scoring artifacts/strategy.md
```

That command - and the eval, automatically - recomputes the weighted totals
itself rather than trusting whatever total is hand-typed in the artifact's
table, and stores the ranking in `context.json`'s `strategy.option_scores`
so it's visible later whether a decision was a landslide or a close call.
If the committed bets don't match the top-scoring option, the artifact is
expected to explain why instead of silently overriding the math. Exact
table format is in `.claude/skills/strategy/SKILL.md`.

### 4.4 Pulling in real data instead of guessing (MCP tools)

Four external tools are wired in - three for pulling real data into an
artifact, one for pushing a finished artifact out to people:

| Tool | Used for | Used by these stages |
|---|---|---|
| `ado` (Azure DevOps) | Backlog context, in-flight work, past bugs | discovery, roadmap, prd |
| `sql` (SQL database) | Usage / adoption metrics | validation, outcomes |
| `kusto` (Azure Data Explorer) | Telemetry, guardrail metrics | validation, phased_rollout, outcomes |
| `slack` (Slack's official MCP server) | Sharing a finished artifact with stakeholders | on-demand, any stage |

The same four servers are configured for four different tools -
`.mcp.json` (Claude Code), `.vscode/mcp.json` (Copilot), `.gemini/settings.json`
(Gemini CLI), `.codex/config.toml` (Codex) - so set the connection details
once and any of the four can use them. Full setup steps, required
environment variables, and security notes are in **`docs/mcp-setup.md`**.
Query starting points for the data-pulling three are in `queries/sql/` and
`queries/kql/` (see `queries/README.md`).

### 4.5 Sharing a finished artifact with stakeholders

Ask for this any time, on any artifact - it isn't a pipeline stage, so it
doesn't need to wait for a particular point in the sequence:

```
"Share the PRD with #product-updates"
```

The `sharing-agent` will confirm the channel and a short preview of the
message before sending anything (posting to Slack can't be quietly undone
the way an ignored query result can), post a short summary rather than
pasting the raw file into chat, and create a Slack Canvas for anything
longer than a couple of paragraphs. Every share gets logged for an audit
trail:

```bash
python -m pipeline.runner record-share --artifact artifacts/prd.md --channel "#product-updates"
```

See `.claude/skills/sharing/SKILL.md` for the full conventions.

## 5. Using this repo from Codex, Copilot, or Gemini

This isn't Claude-Code-only. `AGENTS.md` (and its Gemini-CLI mirror,
`GEMINI.md`) describe the same pipeline loop in plain instructions any
agentic tool can follow, since underneath it's just a CLI
(`pipeline/runner.py`) plus a folder of markdown methodology docs. See
**`docs/cross-tool-setup.md`** for exactly how to point each tool at this
repo.

## 6. Status of this scaffold

What's been proven end-to-end versus what's built but not yet exercised
against something real:

- **Fully proven, start to finish**: the `vision` stage (skill, agent,
  eval, a passing and a failing example) and the `vision -> discovery ->
  strategy` chain (`examples/`), including the strategy stage's option
  grading catching a wrong hand-calculation in its own test artifact.
- **Structurally complete, not yet run for real**: the other 8 stages have
  working agents, skills, and evals, but haven't processed real generated
  output yet - expect to tune word-count minimums and required sections
  once real artifacts start coming through.
- **Structured-field extraction** (`pipeline/extract.py`): built and
  tested. Parses strings, bulleted lists, and `- **Key**: value` pairs out
  of every stage's markdown into `context.json` automatically on a passing
  eval - no LLM call.
- **MCP tools**: `ado`'s config was live-handshake tested (the real
  package, a real MCP protocol exchange - see `docs/mcp-setup.md`). `sql`
  and `kusto` were not - the config matches each server's documented
  format, but connection details will need adjusting for your actual
  database/cluster. Swap `sql` for a different engine (Postgres, MySQL) if
  that's what your metrics live in.
- **Slack sharing**: built, not yet tested against a real workspace (none
  available from here to connect to). Uses Slack's own official remote MCP
  server, confirmed against their current developer docs rather than a
  community package - the `.codex/config.toml` entry specifically is
  flagged as unverified syntax in that file.
- **Research inputs & domain context**: built and proven end-to-end with a
  full worked example (PulseBoard's interview, support tickets, market
  research, and SME notes all live under `inputs/`).
- **Cross-tool support**: `AGENTS.md`, `GEMINI.md`, and
  `.github/copilot-instructions.md` exist and follow each tool's current
  documented format, but haven't been tested in a live Codex, Gemini CLI,
  or Copilot session - flag it here if something's drifted.
