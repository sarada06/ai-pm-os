# Copilot instructions for AI PM OS

This repo runs a gated, 9-stage pipeline that generates PM artifacts
(vision, discovery, strategy, roadmap, mvp, prd, validation,
phased_rollout, outcomes). Full agent instructions are in `AGENTS.md` at
the repo root - read it before generating or editing any stage artifact.

Key points for Copilot specifically:

- This project uses Azure DevOps, SQL Server, and Azure Data Explorer
  (Kusto). Always check whether the `ado`, `sql`, or `kusto` MCP tools
  (configured in `.vscode/mcp.json`) have something relevant before
  answering a question about backlog items, product metrics, or telemetry.
- Every stage's required structure lives in `.claude/skills/<stage>/SKILL.md`
  - read the relevant one before drafting an artifact.
- Artifacts go in `artifacts/<stage>.md`. Gate every stage with
  `python -m pipeline.runner eval <stage>` before treating it as done -
  don't decide pass/fail yourself.
- Query templates for pulling real metrics (adoption, retention, guardrails,
  north-star tracking) are in `queries/sql/` and `queries/kql/`.
