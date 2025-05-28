# Parallel Queries Can Silently Downgrade to Serial Execution

Postgres's parallel query execution can dramatically speed up operations on large datasets, but when parallel workers aren't available, queries silently downgrade to serial execution.

```sql
-- Create a test dataset simulating high-volume application events
CREATE TABLE application_events AS
SELECT
    generate_series(1, 50000000) AS event_id,
    NOW() - (random() * INTERVAL '90 days') AS created_at,
    (ARRAY['user_login', 'api_call', 'page_view', 'purchase', 'error'])[floor(random() * 5 + 1)] AS event_type,
    floor(random() * 100000)::int AS user_id,
    floor(random() * 1000)::int AS tenant_id,
    (random() * 1000)::numeric(10,2) AS response_time_ms;

-- With parallel workers available
SET max_parallel_workers_per_gather = 4;
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    tenant_id,
    event_type,
    COUNT(*) as event_count,
    AVG(response_time_ms) as avg_response_time
FROM application_events
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY tenant_id, event_type
ORDER BY event_count DESC;

-- Execution Time: 3.2 seconds with 4 workers
```

When parallel workers are exhausted, the same query might execute serially:

```sql
-- Force serial execution to simulate downgrade
SET max_parallel_workers_per_gather = 0;
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    tenant_id,
    event_type,
    COUNT(*) as event_count,
    AVG(response_time_ms) as avg_response_time
FROM application_events
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY tenant_id, event_type
ORDER BY event_count DESC;

-- Execution Time: 14.7 seconds without parallelism
```

## Common Causes of Parallel Query Downgrades

**1. Worker Pool Exhaustion**

```sql
-- Check current parallel worker usage
SELECT
    (SELECT COUNT(*) FROM pg_stat_activity WHERE backend_type = 'parallel worker') AS active_workers,
    current_setting('max_parallel_workers')::int AS max_workers,
    current_setting('max_parallel_workers_per_gather')::int AS per_query_limit;
```

**2. Competing Workloads**

```sql
-- Monitor which queries are consuming parallel workers
SELECT
    pid,
    leader_pid,
    query_start,
    state,
    LEFT(query, 50) AS query_preview
FROM pg_stat_activity
WHERE backend_type = 'parallel worker'
ORDER BY query_start;
```

**3. Configuration Limits**

```sql
-- Key parallel execution settings
SHOW max_parallel_workers;             -- Total worker pool
SHOW max_parallel_workers_per_gather;  -- Per-query limit
SHOW max_worker_processes;             -- System-wide process limit
```

## Detecting Silent Downgrades

Look for missing parallel operators in execution plans:

```sql
-- Parallel execution indicators
CREATE OR REPLACE FUNCTION check_parallel_plan(query_text TEXT)
RETURNS TABLE(uses_parallel BOOLEAN, worker_count INT) AS $$
DECLARE
    plan_text TEXT;
BEGIN
    EXECUTE 'EXPLAIN ' || query_text INTO plan_text;

    RETURN QUERY
    SELECT
        plan_text LIKE '%Parallel%',
        COALESCE(
            (regexp_match(plan_text, 'Workers Planned: (\d+)'))[1]::INT,
            0
        );
END;
$$ LANGUAGE plpgsql;

-- Check if your query will run in parallel
SELECT * FROM check_parallel_plan('SELECT COUNT(*) FROM application_events WHERE event_type = ''api_call''');
```

## Implementing Query Queueing (Oracle-Style Solution)

Create a retry mechanism that waits for available workers before executing critical queries:

```sql
CREATE OR REPLACE FUNCTION execute_with_parallel_workers(
    query_text TEXT,
    required_workers INT DEFAULT 2,
    max_wait_seconds INT DEFAULT 30
) RETURNS VOID AS $$
DECLARE
    start_time TIMESTAMP := clock_timestamp();
    available_workers INT;
    max_workers INT;
BEGIN
    -- Get max worker configuration
    SELECT current_setting('max_parallel_workers')::INT INTO max_workers;

    WHILE clock_timestamp() < start_time + (max_wait_seconds || ' seconds')::INTERVAL LOOP
        -- Count available workers
        SELECT max_workers - COUNT(*)
        INTO available_workers
        FROM pg_stat_activity
        WHERE backend_type = 'parallel worker';

        -- Execute if enough workers available
        IF available_workers >= required_workers THEN
            EXECUTE query_text;
            RETURN;
        END IF;

        -- Wait before retry
        PERFORM pg_sleep(0.5);
    END LOOP;

    -- Timeout: execute anyway with warning
    RAISE WARNING 'Parallel workers unavailable after % seconds, executing serially', max_wait_seconds;
    EXECUTE query_text;
END;
$$ LANGUAGE plpgsql;

-- Usage: Ensure parallel execution for critical analytics
SELECT execute_with_parallel_workers(
    'INSERT INTO tenant_usage_summary
     SELECT tenant_id, event_type, DATE(created_at), COUNT(*), AVG(response_time_ms)
     FROM application_events
     WHERE created_at >= CURRENT_DATE - 1
     GROUP BY tenant_id, event_type, DATE(created_at)',
    required_workers := 4,
    max_wait_seconds := 60
);
```

## Monitoring and Prevention Strategies

Track parallel query performance over time:

```sql
-- Create monitoring table
CREATE TABLE parallel_query_stats (
    check_time TIMESTAMP DEFAULT NOW(),
    total_workers INT,
    active_workers INT,
    queued_queries INT,
    avg_wait_time_ms NUMERIC
);

-- Regular monitoring job
CREATE OR REPLACE FUNCTION monitor_parallel_usage() RETURNS VOID AS $$
INSERT INTO parallel_query_stats (total_workers, active_workers)
SELECT
    current_setting('max_parallel_workers')::INT,
    COUNT(*) FILTER (WHERE backend_type = 'parallel worker')
FROM pg_stat_activity;
$$ LANGUAGE sql;
```

Configure alerts when worker utilization is high:

```sql
-- Alert when worker usage exceeds 80%
SELECT
    CASE
        WHEN active_workers::NUMERIC / total_workers > 0.8
        THEN 'WARNING: High parallel worker utilization'
        ELSE 'OK'
    END AS status,
    active_workers || '/' || total_workers AS usage
FROM parallel_query_stats
ORDER BY check_time DESC
LIMIT 1;
```

