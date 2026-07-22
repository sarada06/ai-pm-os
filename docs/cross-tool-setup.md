# Using this repo from Codex, Copilot, or Gemini (not just Claude Code)

The pipeline itself is tool-agnostic: it's a Python CLI (`pipeline/runner.py`)
plus a folder of markdown methodology docs (`.claude/skills/*/SKILL.md`) and
markdown-parsed state (`artifacts/context.json`). Any agentic coding tool
that can run shell commands and read files can drive it. What differs
between tools is (a) how each one discovers instructions automatically, and
(b) whether it has a native "subagent" concept the way Claude Code does.

## What's native to Claude Code vs. what's portable

| Concept | Claude Code | Everyone else |
|---|---|---|
| Per-stage methodology | `.claude/skills/<stage>/SKILL.md` | Same files - just markdown, readable by any tool |
| Stage orchestration | `.claude/agents/orchestrator.md` + 9 stage subagents | `AGENTS.md` / `GEMINI.md` describe the same loop in plain instructions; the tool just follows them turn by turn instead of spawning a sub-session |
| Eval gating | `pipeline/runner.py eval <stage>` | Identical - it's a CLI, not a Claude Code feature |
| Structured extraction | `pipeline/extract.py`, called by the runner | Identical |
| MCP tools | `.mcp.json` | `.vscode/mcp.json` (Copilot), `.gemini/settings.json` (Gemini CLI), `.codex/config.toml` (Codex) - same three servers, different file per docs/mcp-setup.md |

So importing this repo into another tool mostly means: clone it, get that
tool to read its entrypoint file, set the MCP environment variables, go.

## GitHub Copilot (VS Code, Agent Mode)

1. Open the repo folder in VS Code with GitHub Copilot installed.
2. `.vscode/mcp.json` is picked up automatically - open Copilot Chat,
   switch to **Agent Mode**, click the tools icon, and enable the `ado`,
   `sql`, `kusto` servers (first ADO tool call opens a browser login).
3. `.github/copilot-instructions.md` is Copilot's auto-loaded repo
   instructions file - it points at `AGENTS.md` for the full pipeline
   description, so you don't need to paste anything into chat.
4. Drive it conversationally: *"Read AGENTS.md, then check
   artifacts/context.json and draft the next stage."*

## Gemini CLI

1. `gemini` in the repo root auto-loads `GEMINI.md` as context.
2. `.gemini/settings.json` already has the three MCP servers configured
   under the project scope - run `/mcp list` inside a Gemini CLI session to
   confirm they connected (ADO needs a one-time browser login; Kusto needs
   `az login` first).
3. Ask it directly: *"Run the pipeline: initialize a product called X,
   then draft the vision stage."*

## Codex CLI

1. Codex only auto-loads `.codex/config.toml` and `AGENTS.md` for
   **trusted** project directories. From the repo root:
   `codex --trust-project` (or mark the directory trusted the first time
   Codex prompts you), then `codex mcp list` to confirm the three servers
   loaded.
2. Codex reads `AGENTS.md` automatically as part of its project-doc
   discovery (it walks up from the working directory looking for it).
3. Same conversational pattern as the others: ask it to check
   `artifacts/context.json`, read the relevant `SKILL.md`, draft the
   artifact, then run the eval gate via shell.

## Keeping instructions in sync

`AGENTS.md` and `GEMINI.md` are intentionally near-duplicates (Gemini CLI
doesn't reliably chain-load `AGENTS.md`, so the content is mirrored rather
than referenced). If you change the pipeline's instructions, update both.
`.github/copilot-instructions.md` stays thin and just points at `AGENTS.md`,
since Copilot's repo-instructions file is meant to be short.

## What doesn't carry over

- Claude Code's subagents (`.claude/agents/*.md`) run as isolated
  sub-sessions with their own tool scoping - other tools will instead run
  the same steps inline in the main conversation. Functionally similar
  output, less isolation.
- Skill auto-triggering (Claude Code deciding on its own when a skill is
  relevant) doesn't exist elsewhere - other tools need to be told which
  `SKILL.md` to read for a given stage, which `AGENTS.md`/`GEMINI.md`
  already do explicitly.
