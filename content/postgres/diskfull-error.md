# Postgres `DiskFull` Error

I.e. `could not resize shared memory segment`

## BLUF

* The error stems from shared‑memory exhaustion, **not** disk usage.
* Multiply `work_mem × workers × hash/sort nodes` to estimate demand.
* Hash joins are the usual offender; fix with composite indexes or lower `work_mem`.
* Bursty logs trace back to one pathological query—optimize it, cap resources, or add RAM.
* Single occurrences are noise; systemic repetition is solvable with the steps above.

When Postgres writes

```
ERROR: could not resize shared memory segment "/PostgreSQL.…" to N bytes: No space left on device
```

it is signalling an *internal* out‑of‑memory condition. The string “DiskFull” is appended by libpq clients; the physical volume is almost always fine. The failure occurs in a `shmget(2)` call while extending a hash‑or‑sort buffer inside `/dev/shm` (on Linux) or System V shared memory.

---

## Mechanics: why memory, *not* disk?

| Factor                       | Multiplier | Example                    |
| ---------------------------- | ---------: | -------------------------- |
| `work_mem` per plan node     |      38 MB |                            |
| × parallel workers           |          8 | `max_parallel_workers = 8` |
| × RAM‑hungry nodes           |          5 | hash joins + sorts         |
| **Total shared‑buf request** | **7.6 GB** | 38 MB × 8 × 5              |

If the allocator sees < 7.6 GB available in the shared segment, it aborts the backend and raises this error. Large temporary operations *usually* spill to disk, but the planner prefers in‑memory hash joins/aggregates whenever the node fits within `work_mem`; once the multiplication above overshoots, spilling is impossible.

---

## Initial sanity checks

```bash
# disk really OK?
df -h /var/lib/postgresql

# frequency over the last day
grep -iR "could not resize shared memory" /var/log/postgresql \
  | sed 's/.log.*//' | uniq -c | sort -nr   # bursty? continuous?
```

Single‑digit incidents per day are benign. Persistent bursts require investigation.

---

## Trace a specimen query

1. Extract the PID from a log line (`postgres[5883275]: …`).
2. Pull the full statement sequence:

   ```bash
   grep 5883275 /var/log/postgresql/*.log | less  # note: [42-1], [42-2] fragments
   ```
3. In `psql`, inspect the execution plan:

   ```sql
   EXPLAIN (ANALYZE, BUFFERS) <query>;
   ```

Red flags: `Hash Join`, `HashAggregate`, many `Workers Launched`, or unusually high `Work_mem` in the settings column.

---

## Remediation

| Symptom                    | Targeted fix                                      | Command                                                           |
| -------------------------- | ------------------------------------------------- | ----------------------------------------------------------------- |
| Hash joins on large tables | Encourage merge/nested‑loop joins via **indexes** | `CREATE INDEX CONCURRENTLY ON big(a, b);`                         |
| Generous `work_mem`        | Lower to a rational per‑node value                | `ALTER SYSTEM SET work_mem = '16MB';`  `SELECT pg_reload_conf();` |
| Explosive parallelism      | Cap workers                                       | `ALTER SYSTEM SET max_parallel_workers = 4;`                      |
| Broad `SELECT *` analytics | Trim projection or materialize interim results    | `CREATE MATERIALIZED VIEW …`                                      |
| Still OOM after tuning     | Add RAM / move to a larger instance               | —                                                                 |

Implementation order: **indexes → memory tuning → parallelism → query rewrite → hardware**. After each change rerun the log grep to confirm reduction.

---

## Detailed tuning notes

### Index strategy

If a query filters on column A and joins on column B, add a multicolumn index `(A, B)` on *both* tables; this reduces the hash‑table input size and lets the planner pick a merge join.

### Memory parameters

`work_mem` is global‑per‑node, not per‑session. Keep it conservative (8–32 MB) on OLTP systems and use `SET LOCAL work_mem = …` for known analytics jobs.

### Parallel workers

High `work_mem` *and* many workers multiply; tune them together. A practical upper bound is:

```
total_RAM_bytes × 0.4 / (work_mem_bytes × avg_parallel_nodes)
```

Empirical monitoring trumps formulas—adjust until incidents disappear without degrading throughput.

---

## "Don’t panic" playbook

```bash
# 1. Prove the volume has headroom
df -hT /var/lib/postgresql

# 2. Locate noisy backends
grep -iR "could not resize shared memory" /var/log/postgresql | head

pid=5883275
grep $pid /var/log/postgresql/* | less        # capture SQL

# 3. Inside psql
EXPLAIN (ANALYZE, BUFFERS) <query>;
-- if HASH JOIN present:
CREATE INDEX CONCURRENTLY ... ;
SET work_mem = '16MB';
SET max_parallel_workers = 4;
```
