# Fixing Duplicate Primary Key Rows

Even with primary key constraints, Postgres tables can sometimes contain duplicate primary key values.
Duplicate priamry keys are rare, but seem to be most commoonly caused by index corruption, which is often caused by glibc sorting changes. Those sorting changes are often introduced by Postgres updates, OS updates, or (even rarer), upstream hardware failures.

## Detecting Duplicates

First, check for duplicate primary keys:

```sql
-- Look for repeated primary key values
SELECT id, COUNT(*)
FROM mytable
GROUP BY id
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC;

-- View the actual duplicate rows
SELECT ctid, *
FROM mytable
WHERE id IN (
    SELECT id
    FROM mytable
    GROUP BY id
    HAVING COUNT(*) > 1
)
ORDER BY id, ctid;
```

## Preparation Steps

Before introducing any breaking changes to fixing duplicates, generate a backup:

```sql
-- 1. Create a full backup (run from shell)
pg_dump -d mydb > mydb_backup_$(date +%Y%m%d).sql

-- 2. Disable index scans to see all rows
SET enable_indexscan = off;
SET enable_indexonlyscan = off;

-- 3. Create a backup table
CREATE TABLE mytable_backup AS
SELECT * FROM mytable;

-- 4. Create table for deleted rows (forensics)
CREATE TABLE mytable_deleted_dups AS
SELECT * FROM mytable WHERE false;
```

## Removing Duplicates

### Method 1: Keep Row with Minimum CTID

```sql
BEGIN;

-- Set session to replica role to bypass triggers
SET session_replication_role = 'replica';

-- Remove duplicates, keeping the row with smallest ctid
WITH good_rows AS (
    SELECT MIN(ctid) as min_ctid
    FROM mytable
    GROUP BY id
),
deleted AS (
    DELETE FROM mytable
    WHERE NOT EXISTS (
        SELECT 1
        FROM good_rows
        WHERE good_rows.min_ctid = mytable.ctid
    )
    RETURNING *
)
-- Store deleted rows for analysis
INSERT INTO mytable_deleted_dups
SELECT * FROM deleted;

-- Check results before committing
SELECT 'Deleted duplicates:', COUNT(*) FROM mytable_deleted_dups;
SELECT 'Remaining rows:', COUNT(*) FROM mytable;

-- If everything looks good
COMMIT;
-- Otherwise: ROLLBACK;
```

### Method 2: Keep Specific Row Based on Business Logic

```sql
BEGIN;

SET session_replication_role = 'replica';

-- Example: Keep the most recently updated row
WITH ranked_rows AS (
    SELECT ctid,
           ROW_NUMBER() OVER (
               PARTITION BY id
               ORDER BY updated_at DESC, ctid
           ) as rn
    FROM mytable
),
deleted AS (
    DELETE FROM mytable
    USING ranked_rows
    WHERE mytable.ctid = ranked_rows.ctid
    AND ranked_rows.rn > 1
    RETURNING mytable.*
)
INSERT INTO mytable_deleted_dups
SELECT * FROM deleted;

COMMIT;
```

## Rebuilding Indexes

After removing duplicates, rebuild all indexes:

```sql
-- Rebuild primary key and all indexes
REINDEX TABLE mytable;

-- Alternative: Rebuild specific index
REINDEX INDEX mytable_pkey;

-- For large tables, consider CONCURRENTLY (requires more space)
CREATE UNIQUE INDEX CONCURRENTLY mytable_pkey_new ON mytable(id);
BEGIN;
ALTER TABLE mytable DROP CONSTRAINT mytable_pkey;
ALTER TABLE mytable ADD CONSTRAINT mytable_pkey PRIMARY KEY USING INDEX mytable_pkey_new;
COMMIT;
```

## Verification and Cleanup

```sql
-- Re-enable normal query planning
RESET enable_indexscan;
RESET enable_indexonlyscan;
RESET session_replication_role;

-- Verify no duplicates remain
SELECT id, COUNT(*)
FROM mytable
GROUP BY id
HAVING COUNT(*) > 1;

-- Analyze the deleted duplicates
SELECT id, COUNT(*) as dup_count
FROM mytable_deleted_dups
GROUP BY id
ORDER BY dup_count DESC;

-- After verification, clean up
DROP TABLE mytable_backup;
-- Keep mytable_deleted_dups for audit trail
```

## Prevention

To prevent future occurrences:

```sql
-- Add a check constraint as backup validation
ALTER TABLE mytable ADD CONSTRAINT check_unique_id
CHECK (id IN (SELECT id FROM mytable GROUP BY id HAVING COUNT(*) = 1));

-- Monitor for index corruption regularly
CREATE OR REPLACE FUNCTION check_duplicates(table_name text, key_column text)
RETURNS TABLE(key_value text, duplicate_count bigint) AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT %I::text, COUNT(*)
         FROM %I
         GROUP BY %I
         HAVING COUNT(*) > 1',
        key_column, table_name, key_column
    );
END;
$$ LANGUAGE plpgsql;

-- Schedule regular checks
SELECT * FROM check_duplicates('mytable', 'id');
```

## Key Takeaways

1. **Always backup first** - This issue involves data deletion
2. **Use transactions** - Allow rollback if something goes wrong
3. **Disable index scans** - Ensures you see all rows during cleanup
4. **Keep forensic data** - Store deleted rows for analysis
5. **Rebuild indexes** - Essential after removing duplicates
6. **Monitor regularly** - Catch issues before they accumulate

