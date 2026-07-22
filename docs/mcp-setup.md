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

Export these in your shell before launching any of the above tools:

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
needed - Node.js 20+ required). Authenticates via browser login on first
use (matching whatever Microsoft account has access to `ADO_ORG`).

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
