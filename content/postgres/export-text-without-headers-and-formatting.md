# Export Text Without Headers and Formatting

`psql` automatically adds cruft when outputting results in the form of headers and text wrapping. And sometimes you just want to get the value of a result without the noise.

To do this, switch to tuples only mode and engage unaligned format before performing your query.

```terminal
\t on
\pset format unaligned
```

You can combine this with [writing a query result to a file](./write-a-query-result-to-a-file.md) to export clean result values.

```sql
SELECT * email FROM users WHERE id=user_01EDFKS6WA2BSARMJ3S7N22KQK \g user.txt
```
