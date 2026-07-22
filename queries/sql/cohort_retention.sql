-- Purpose: week-over-week retention for users who adopted a feature in a
-- given cohort week - useful for "validation" (is the behavior sticking?)
-- and "outcomes" (did it hold up post-rollout?).
-- Used with the `sql` MCP tool.
--
-- Replace:
--   {{events_table}}   - table logging user actions/events
--   {{user_id_column}} - column identifying the user/account
--   {{cohort_start}}   - cohort week start date, e.g. '2026-06-01'

WITH cohort AS (
    SELECT {{user_id_column}} AS user_id, MIN(CAST(event_timestamp AS DATE)) AS first_seen
    FROM {{events_table}}
    WHERE CAST(event_timestamp AS DATE) >= '{{cohort_start}}'
    GROUP BY {{user_id_column}}
),
activity AS (
    SELECT e.{{user_id_column}} AS user_id,
           DATEDIFF(WEEK, c.first_seen, CAST(e.event_timestamp AS DATE)) AS week_number
    FROM {{events_table}} e
    JOIN cohort c ON c.user_id = e.{{user_id_column}}
)
SELECT week_number, COUNT(DISTINCT user_id) AS active_users
FROM activity
WHERE week_number BETWEEN 0 AND 8
GROUP BY week_number
ORDER BY week_number ASC;
