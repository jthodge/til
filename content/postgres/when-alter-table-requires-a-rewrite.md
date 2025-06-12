# When `ALTER TABLE` Requires a Rewrite

Not all `ALTER TABLE` operations in PostgreSQL behave the same.
Some require a full table rewrite, causing significant downtime on large tables.
Others are nearly instantaneous metadata changes.

## Operations That Require Table Rewrites

### Adding Columns with Non-Static Defaults

```sql
-- This requires a full table rewrite
ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT now();

-- This is instant (static default)
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT true;

-- This is also instant (no default)
ALTER TABLE users ADD COLUMN notes TEXT;
```

### Changing Data Types

```sql
ALTER TABLE products ALTER COLUMN price TYPE NUMERIC(12,2);
ALTER TABLE orders ALTER COLUMN quantity TYPE BIGINT;  -- Even from INT!
ALTER TABLE events ALTER COLUMN data TYPE JSONB USING data::JSONB;
```

### Other Rewrite-Triggering Operations

```sql
-- Change table's logging status
ALTER TABLE large_table SET UNLOGGED;  -- Requires rewrite
ALTER TABLE large_table SET LOGGED;    -- Also requires rewrite

-- These maintenance operations also rewrite
VACUUM FULL large_table;
CLUSTER large_table USING some_index;
REFRESH MATERIALIZED VIEW CONCURRENTLY my_view;
```

## Testing for Table Rewrites

It's good practice, before running `ALTER TABLE` on production, to test if it will cause a rewrite:

```sql
-- Create a test table with same structure
CREATE TABLE test_rewrite (LIKE production_table INCLUDING ALL);

-- Insert minimal test data
INSERT INTO test_rewrite SELECT * FROM production_table LIMIT 1000;

-- Check the file node before
SELECT pg_relation_filenode('test_rewrite'::regclass) AS before_filenode;

-- Run your ALTER TABLE
ALTER TABLE test_rewrite ADD COLUMN new_field VARCHAR(100) DEFAULT 'pending';

-- Check the file node after
SELECT pg_relation_filenode('test_rewrite'::regclass) AS after_filenode;

-- If the file nodes differ, a rewrite occurred
-- Clean up
DROP TABLE test_rewrite;
```

## Safer Alternatives for Large Tables

### Progressive Column Addition

Instead of adding a column with a default that requires a rewrite:

```sql
-- Step 1: Add column without default (instant)
ALTER TABLE users ADD COLUMN status VARCHAR(20);

-- Step 2: Update in batches
DO $$
DECLARE
    batch_size INT := 10000;
    updated INT;
BEGIN
    LOOP
        UPDATE users
        SET status = 'active'
        WHERE status IS NULL
        LIMIT batch_size;

        GET DIAGNOSTICS updated = ROW_COUNT;
        EXIT WHEN updated = 0;

        -- Optional: pause between batches
        PERFORM pg_sleep(0.1);
    END LOOP;
END $$;

-- Step 3: Add NOT NULL constraint after backfill
ALTER TABLE users ALTER COLUMN status SET NOT NULL;
ALTER TABLE users ALTER COLUMN status SET DEFAULT 'active';
```

### Using Logical Replication for Zero-Downtime Changes

For critical tables, use logical replication:

```sql
-- 1. Create new table with desired schema
CREATE TABLE users_new (LIKE users INCLUDING ALL);
ALTER TABLE users_new
    ADD COLUMN created_at TIMESTAMP DEFAULT now(),
    ALTER COLUMN id TYPE BIGINT;

-- 2. Set up logical replication
-- (Requires configuration of publisher/subscriber)

-- 3. Switch applications to new table
BEGIN;
ALTER TABLE users RENAME TO users_old;
ALTER TABLE users_new RENAME TO users;
COMMIT;

-- 4. Drop old table after verification
DROP TABLE users_old;
```

## Lock Monitoring During `ALTER TABLE`

Monitor blocking queries during schema changes:

```sql
-- Check for blocking locks
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocked_activity.query AS blocked_query,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocking_activity.query AS blocking_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.relation = blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

## Best Practices

1. **Always test first**: Use the file node comparison technique on a test table
2. **Consider timing**: Run ALTER TABLE during low-traffic periods
3. **Monitor locks**: Keep an eye on pg_stat_activity during the operation
4. **Have a rollback plan**: Some ALTER TABLE operations can't be easily undone
5. **Use CREATE TABLE ... LIKE**: For complex changes, creating a new table might be faster

So, remember: even "simple" `ALTER TABLE` operations require an `AccessExclusiveLock`, which can cause brief downtime while waiting for existing queries to complete.
