# Idenfity `NULL` JSON Values

```sql
SELECT id, metadata FROM $TABLE_NAME
WHERE jsonb_typeof(metadata) != 'object'
OR jsonb_path_exists(metadata, '$.keyvalue() ? (@.value == null)')
```

Given a table, `$TABLE_NAME`, that possesses a JSONB column, `metadata`, the above query will return all rows in `$TABLE_NAME` where `metadata` is not `NULL`, but some value _within_ `metadata` is `NULL`.
