-- Purpose: measure adoption of a specific feature/scope-in item, to feed
-- the "validation" stage's hypothesis testing or the "outcomes" stage's
-- learnings.
-- Used with the `sql` MCP tool.
--
-- Replace:
--   {{events_table}}     - table logging user actions/events
--   {{feature_event}}     - the event name identifying use of the feature
--   {{user_id_column}}    - column identifying the user/account
--   {{total_users_table}} - table (or subquery) of the eligible user base
--   {{lookback_days}}     - rollout/observation window

WITH feature_users AS (
    SELECT DISTINCT {{user_id_column}}
    FROM {{events_table}}
    WHERE event_name = '{{feature_event}}'
      AND event_timestamp >= DATEADD(DAY, -{{lookback_days}}, GETUTCDATE())
)
SELECT
    (SELECT COUNT(*) FROM feature_users)                         AS adopters,
    (SELECT COUNT(*) FROM {{total_users_table}})                 AS eligible_users,
    CAST((SELECT COUNT(*) FROM feature_users) AS FLOAT)
        / NULLIF((SELECT COUNT(*) FROM {{total_users_table}}), 0) AS adoption_rate;
