# `psql` Notes

## Formatting Output

Extended output display mode: `\x`
Reads query results as batches of records that contain column data.
Contrasts the default output, which displays each record as a (usually quite wide) list of columns.

## Table Column Borders

Should you opt not to use `\x`, you can use line styling to add outlining borders and separators to table output using Unicode characters:

```bash
\pset linestyle unicode
```

## Display query runtimes

To retreieve a tailing result (in ms) for a query:

```bash
\timing
```

## `NULL` Value Presets

Set `NULL` value output to differentiate from an empty string:

```bash
\pset null '(null)'
```

## Dump History

Dump a command history for a session:

```bash
# Generate a history file for each db in the config directory
# NOTE: triple check this path before running
#
# \set HISTFILE ~/.config/psql/psql_history-:DBNAME
```

## Echo `psql` Commands as `SQL` to stdout

All `psql` `\` commands run against Postgres system tables.
You can use the `ECHO` command to display SQL queries as they're run for a given command.
Excellent for visibility into internal tables, catalogs, etc.

```bash
\set ECHO_HIDDEN on
# or, short name:
# -E
```

And then, e.g. a table lookup:

```bash
\dt+
```

## Echo Postgres `psql` Queries to stdout

We can also echo all queries that `psql` runs to stdout:

```bash
\set ECHO queries
# or, short name:
# -e
```

## Run Shell Scripts from Within `psql`

```bash
\! pwd
```

Alternatively, invoking `\!` without a command will open an interactive shell.
After leaving this shell, you're returned to the previous `psql` session.

## `crosstabview`

Executed a pivoted representation of a resultset.

- [Current postgresql docs](https://www.postgresql.org/docs/current/app-psql.html#APP-PSQL-META-COMMANDS-CROSSTABVIEW)
- [postgresl Wiki entry](https://wiki.postgresql.org/wiki/Crosstabview)