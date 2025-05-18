# Write a Query Result to a File

Normally, when writing a `psql` query, the statement is terminated with a semicolon and the result of the query is written to the output of the `psql` session.

However, there's an alternative. Terminating a `psql` statement with `\g` instead of a semicolon will also send the query to the Postgres server for execution.

```sql
SELECT 1 \g
```

And including a filename after `\g` will write the query result to the specified file instead of to the `psql` session output.

```sql
SELECT 1, 2, 3 \g psql-query-result.txt
```

Then, you can use `cat` to view the result

```terminal
\! cat psql-query-result.txt
 ?column? | ?column? | ?column?
----------+----------+----------
        1 |        2 |        3
(1 row)
```
