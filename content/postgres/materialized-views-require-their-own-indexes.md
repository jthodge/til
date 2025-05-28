# Materialized Views Require Their Own Indexes

Postgre materialized views store query results on disk as static tables, but they don't inherit indexes from their underlying tables. This can be surprising if one expects index performance for free in their materialized views. Materialized views are treated as independent tables by the query planner, so they require their own indexes for improved performance.

```sql
-- Create a materialized view for SaaS usage analytics
CREATE MATERIALIZED VIEW account_usage_metrics AS
SELECT
    a.account_id,
    a.plan_tier,
    COUNT(DISTINCT u.user_id) as active_users,
    SUM(e.api_calls) as total_api_calls,
    MAX(u.last_activity) as last_team_activity
FROM accounts a
JOIN users u ON a.account_id = u.account_id
JOIN usage_events e ON u.user_id = e.user_id
WHERE e.event_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY a.account_id, a.plan_tier;

-- This view won't use the accounts table's primary key index!
-- We need to create indexes explicitly
CREATE INDEX idx_usage_metrics_account ON account_usage_metrics(account_id);
CREATE INDEX idx_usage_metrics_plan ON account_usage_metrics(plan_tier);
```

## The Key Difference: Views vs Materialized Views

Regular views are just saved queries that execute against live data, so they can use the underlying tables' indexes. Materialized views are physically stored result sets that require their own index structures.

```sql
-- Regular view: uses underlying table indexes
CREATE VIEW active_users AS
SELECT user_id, email, last_login
FROM users
WHERE status = 'active';

-- Query on view uses users table's indexes
EXPLAIN SELECT * FROM active_users WHERE user_id = 123;
-- Uses index on users.user_id

-- Materialized view: needs its own indexes
CREATE MATERIALIZED VIEW active_users_cached AS
SELECT user_id, email, last_login
FROM users
WHERE status = 'active';

-- Without an index, this does a sequential scan
EXPLAIN SELECT * FROM active_users_cached WHERE user_id = 123;
-- Seq Scan on active_users_cached
```

## Refresh Strategies and Index Behavior

Postgres offers two refresh methods for materialized views, each with different impacts on indexes:

**Standard Refresh (Blocking)**
```sql
-- Completely rebuilds the view and all indexes
REFRESH MATERIALIZED VIEW account_usage_metrics;
-- Acquires exclusive lock - no reads allowed during refresh
-- Indexes are rebuilt from scratch
```

**Concurrent Refresh (Non-Blocking)**
```sql
-- First, create a UNIQUE index (required for concurrent refresh)
CREATE UNIQUE INDEX idx_usage_metrics_unique
ON account_usage_metrics(account_id);

-- Now refresh without blocking reads
REFRESH MATERIALIZED VIEW CONCURRENTLY account_usage_metrics;
-- Updates incrementally, maintains indexes
-- Slower but allows continuous reads
```

The concurrent refresh requires at least one unique index to identify rows for incremental updates. This constraint makes it unsuitable for aggregated data without unique identifiers.

## Practical Indexing Patterns

For typical materialized view use cases, consider these indexing strategies:

```sql
-- SaaS user engagement metrics view
CREATE MATERIALIZED VIEW user_engagement_daily AS
SELECT
    DATE_TRUNC('day', activity_date) as activity_day,
    account_id,
    COUNT(DISTINCT user_id) as daily_active_users,
    SUM(feature_interactions) as total_interactions,
    AVG(session_duration_minutes) as avg_session_length
FROM user_activities
GROUP BY DATE_TRUNC('day', activity_date), account_id;

-- Index for date range queries
CREATE INDEX idx_engagement_date ON user_engagement_daily(activity_day);

-- Composite index for account-specific queries
CREATE INDEX idx_engagement_account_date ON user_engagement_daily(account_id, activity_day);

-- For concurrent refresh (if activity_day + account_id is unique)
CREATE UNIQUE INDEX idx_engagement_unique
ON user_engagement_daily(activity_day, account_id);
```

## Performance Monitoring

Track your materialized view index usage to ensure they're providing value:

```sql
-- Check index usage statistics
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'account_usage_metrics'
ORDER BY idx_scan DESC;

-- Monitor refresh times
\timing on
REFRESH MATERIALIZED VIEW CONCURRENTLY account_usage_metrics;
-- Time: 2834.123 ms
```

Materialized views combine the query simplification of views with the performance of pre-computed tables, but they require careful index management. Always create indexes based on your actual query patterns, and choose between blocking and concurrent refresh based on your availability requirements.
