# MCP tool setup: ADO, SQL, Kusto

Three MCP servers give the pipeline real data instead of relying on the
user to paste numbers into artifacts. Config files for four different
agentic tools are already in this repo, all pointing at the same three
servers via the same environment variables - you only need to set the
environment variables once.

| Tool | Config file | Format |
|---|---|---|
| Claude Code | `.mcp.json` (repo root) | JSON, `mcpServers` |
| GitHub Copilot (VS Code Agent Mode) | `.vscode/mcp.json` | JSON, `servers` |
| Gemini CLI | `.gemini/settings.json` | JSON, `mcpServers` |
| Codex CLI | `.codex/config.toml` | TOML, `[mcp_servers.*]` (project-scoped, trusted projects only) |

## Required environment variables

Export these in your shell before launching any of the above tools for the
`ado`, `sql`, and `kusto` servers. `slack` needs none of these - see its
own section below.

```bash
export ADO_ORG="your-ado-org"                 # e.g. "contoso" (org, not full URL)

export SQL_HOST="your-server.database.windows.net"
export SQL_DATABASE="your-database"
export SQL_USER="your-username"
export SQL_PASSWORD="your-password"

export KUSTO_CLUSTER_URI="https://yourcluster.kusto.windows.net"
export KUSTO_DATABASE="your-database"
```

None of these are committed anywhere in this repo - the config files only
reference the variable names.

## 1. Azure DevOps (`ado`)

Uses Microsoft's official server, `@azure-devops/mcp` (npx, no install
needed - Node.js 20+ required). Default auth (`interactive`) opens a
browser for login on first use, matching whatever Microsoft account has
access to `ADO_ORG`. For CI or headless use, pass `-a pat` (with
`AZURE_DEVOPS_PAT` set), `-a env`/`-a envvar`, or `-a azcli` (uses an
existing `az login` session) instead - add `-a <mode>` to the `args` array
in whichever config file you're using.

**Verified**: spawned this exact server (`npx -y @azure-devops/mcp <org> -d
core`) and confirmed it speaks MCP correctly over stdio - `initialize`
returns real server info (`Azure DevOps MCP Server` v2.8.1), and
`tools/list` returns real tool schemas (`core_list_projects`,
`core_list_project_teams`, `core_get_identity_ids`, etc.) with full
JSON-schema input definitions. A tenant-lookup call against a placeholder
org correctly failed with a 403 (proving it really reaches
`dev.azure.com`), which is exactly what should happen without valid
credentials - the protocol layer and package are confirmed working; you
still need real `ADO_ORG` + credentials for actual data.

Domains loaded: `core`, `work`, `work-items`, `wiki` - kept narrow on
purpose so the tool list stays manageable. Add more (`repositories`,
`pipelines`, `test-plans`, `search`, `advanced-security`) in the config's
`args` array if a stage needs them.

Used by: `discovery` (existing backlog/epics as research input), `roadmap`
(cross-checking against in-flight work), `prd` (related work items and
historical bugs for a feature area).

## 2. SQL Server (`sql`)

Config points at a community server, `@bilims/mcp-sqlserver` - read-only by
design. If your product's metrics live in Postgres, MySQL, or another
warehouse instead, swap the `command`/`args`/`env` block in each config
file for the equivalent server (e.g. the official
`@modelcontextprotocol/server-postgres` for Postgres) - the rest of the
pipeline doesn't care which SQL engine it's talking to, only that a `sql`
tool exists.

Used by: `validation` (pulling actual test/beta cohort results instead of
guessing), `outcomes` (querying the north star metric's actual trend).

## 3. Azure Data Explorer / Kusto (`kusto`)

Config points at `kusto-mcp` (johnib/kusto-mcp), which authenticates via
Azure CLI (`az login`) rather than a stored secret. Install the Azure CLI
first if you haven't (`brew install azure-cli` / `winget install
Microsoft.AzureCLI` / see Microsoft's install docs for Linux).

Used by: `validation` and `outcomes` (telemetry-based metrics), and
especially `phased_rollout` (querying guardrail metrics live during a
staged release to decide whether to advance or hold).

## 4. Slack (`slack`)

Uses Slack's own official remote MCP server (`https://mcp.slack.com/mcp`) -
this is different from the other three in an important way: it's not a
local process you spawn with `npx`, it's a hosted endpoint you connect to
over HTTP, and it authenticates via OAuth instead of an env-var token.

Setup:
1. A workspace admin needs to approve the MCP integration for your Slack
   workspace once (Slack's App Directory review/approval process - see
   [Slack's MCP security docs](https://slack.com/blog/news/slackbot-mcp-security)).
2. The first time any of the four tools tries to use `slack`, it opens a
   browser OAuth flow - no token to generate or store yourself.
3. Claude Code specifically also supports `claude plugin install slack`,
   which configures this same server automatically - the config already in
   `.mcp.json` is equivalent, so either approach works.

Available actions (per Slack's docs): search channels/messages, read and
send messages, manage Canvases, look up users. Used by the `sharing-agent`
(not tied to a pipeline stage - it's invoked on demand whenever you ask to
share an artifact) to post a summary and, for longer documents, create a
Slack Canvas rather than dumping raw markdown into a channel. See
`.claude/skills/sharing/SKILL.md`.

**Caveat**: the Codex CLI entry in `.codex/config.toml` for `slack` was not
independently verified the way the other three servers were (see the note
in that file) - Codex's syntax for remote/OAuth MCP servers wasn't
confirmed against current docs. Run `codex mcp list` after loading to check
it actually connected.

## Verifying a server is connected

- Claude Code: run `/mcp` inside a session
- Gemini CLI: run `/mcp list`
- Copilot (VS Code): open the Copilot Chat panel in Agent Mode, click the
  tools icon - connected servers show their tool count
- Codex CLI: `codex mcp list` (requires the project to be marked trusted -
  see `docs/cross-tool-setup.md`)

## Security notes

- All three configs default to read-only or read-only-by-convention
  servers. If you swap in a server with write access (e.g. one that can
  create ADO work items or run `INSERT`/`UPDATE` SQL), review its
  permission model before pointing it at a production system.
- Prefer scoped credentials: an ADO PAT with read-only scopes, a SQL login
  with `SELECT`-only grants, a Kusto viewer role - rather than admin
  credentials, regardless of what the MCP server itself supports.
- `slack` is the one server here that's write-by-design - posting messages
  and Canvases is the point. That's exactly why `.claude/skills/sharing/SKILL.md`
  and `sharing-agent.md` both require confirming the channel and content
  with you before anything gets sent - a Slack post to the wrong channel
  can't be quietly walked back the way a bad query result can be ignored.
