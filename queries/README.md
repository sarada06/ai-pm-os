# Analysis query templates

Parameterized SQL and KQL templates for the data pulls PM stages actually
need, so agents (and you) aren't writing queries from scratch each time.
`{{double_brace}}` placeholders are meant to be filled in per-product;
nothing here runs as-is.

| Template | Feeds stage | Question it answers |
|---|---|---|
| `sql/north_star_metric_trend.sql` | outcomes | Is the north star metric moving the right direction? |
| `sql/feature_adoption.sql` | validation, outcomes | What fraction of eligible users adopted the feature? |
| `sql/cohort_retention.sql` | validation, outcomes | Does usage stick week over week, or drop off? |
| `kql/guardrail_check.kql` | phased_rollout | Has a guardrail metric breached its threshold during this phase? |
| `kql/error_rate_by_phase.kql` | phased_rollout, validation | Is the treatment cohort's error rate worse than control? |
| `kql/feature_usage_trend.kql` | validation, outcomes | Is daily usage of the feature growing, flat, or declining? |

## How a stage agent should use these

1. Read the relevant stage's `SKILL.md` first - it says which section the
   result belongs in (e.g. `validation`'s "Results" section).
2. Pick the template that matches the question being asked. Fill in the
   placeholders based on the product's actual schema/table names - ask the
   user if they aren't obvious from context or from an ADO wiki page.
3. Run it via the `sql` or `kusto` MCP tool (see `docs/mcp-setup.md`).
4. Report the actual returned numbers in the artifact - don't round them
   into vague language ("significant growth") when a specific figure is
   available; the eval's `no_placeholder_text` and quality checks reward
   specificity.
5. If the MCP tool isn't connected or the query fails, say so explicitly in
   the artifact (e.g. "Data source unavailable at time of writing - manual
   pull needed") rather than fabricating a plausible-looking number.

## Adding a new template

Keep the same header comment style (Purpose / used-with-tool / Replace
list) so an agent reading the file cold knows what to fill in without
guessing at column names.
