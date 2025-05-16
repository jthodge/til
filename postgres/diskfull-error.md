# `DiskFull` Error

A noteworthy, common Postgres error. Particularly when working with Postgres via ORMs.

Generic form:

```bash
DiskFull ERRROR: could not resize shared memory segment
```

Python flavored:

```bash
psycopg2.OperationalError: ERROR:  could not resize shared memory segment "/PostgreSQL.759674958" to 55444231 bytes: No space left on device
```

## Possible Causes

`DiskFull` errors can occur due to:

1. **Actual disk space exhaustion**: The database server is genuinely out of disk space
2. **Temporary files filling up**: Heavy queries or sorts creating large temporary files
3. **Shared memory segment limitations**: Operating system limits on shared memory segments (often on macOS)
4. **WAL segment accumulation**: Write-Ahead Log files building up due to replication lag or misconfiguration
5. **Log file growth**: Excessive logging filling up disk space

## Common Fixes

1. **Check disk space**:

   ```bash
   df -h
   ```

2. **Clean up temporary files**:

   ```sql
   -- Check temp file usage
   SELECT datname, temp_files, temp_bytes FROM pg_stat_database;
   ```

3. **Increase shared memory limits** (macOS):

   ```bash
   sudo sysctl -w kern.sysv.shmmax=4294967296
   sudo sysctl -w kern.sysv.shmall=1048576
   ```

4. **Manage WAL segments**:

   ```sql
   -- Check WAL size
   SELECT pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0'));
   ```

5. **Vacuum database**:

   ```sql
   VACUUM FULL;
   ```

## Investigation Techniques

1. **Check PostgreSQL logs**:

   ```bash
   tail -f /var/log/postgresql/postgresql-*.log
   ```

2. **Monitor disk usage by database**:

   ```sql
   SELECT datname, pg_size_pretty(pg_database_size(datname))
   FROM pg_database
   ORDER BY pg_database_size(datname) DESC;
   ```

3. **Identify large tables**:
   ```sql
   SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
   FROM pg_tables
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
   LIMIT 10;
   ```

4. **Check running queries**:
   ```sql
   SELECT pid, now() - query_start AS duration, query
   FROM pg_stat_activity
   WHERE state = 'active'
   ORDER BY duration DESC;
   ```

5. **Monitor temporary file creation**:
   ```sql
   SELECT query, temp_blks_written
   FROM pg_stat_statements
   WHERE temp_blks_written > 0
   ORDER BY temp_blks_written DESC
   LIMIT 10;
   ```
