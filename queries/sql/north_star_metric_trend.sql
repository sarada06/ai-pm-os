-- Purpose: track a north star metric's trend over time to feed the
-- "outcomes" stage's "Results vs North Star" section.
-- Used with the `sql` MCP tool.
--
-- Replace:
--   {{metric_table}}   - table containing the daily/weekly metric rollup
--   {{metric_column}}  - the numeric column representing the north star metric
--   {{date_column}}    - the date/timestamp column
--   {{lookback_days}}  - how far back to look (e.g. 90)

SELECT
    CAST({{date_column}} AS DATE) AS metric_date,
    SUM({{metric_column}})        AS metric_value
FROM {{metric_table}}
WHERE {{date_column}} >= DATEADD(DAY, -{{lookback_days}}, GETUTCDATE())
GROUP BY CAST({{date_column}} AS DATE)
ORDER BY metric_date ASC;
