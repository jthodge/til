# Drop a Database Even When Clients are Connected

Until recently, Postgres would not allow `DROP DATABASE` operations if any sessions connected to the target database were active.

Postgres 13 introduces a new feature to force drop a database regardless of the status of any sessions connected to the target database. It's worth noting that this option to force drop terminates the sessions connected to the target database.

Utility Syntax:
```
dropdb [-f/--force] $DB_NAME
```

SQL Syntax
```sql
DROP DATABASE [IF EXISTS] $DB_NAME [ [ WITH ] (FORCE)]
```

## References

- [Postgres 13 Release Notes](https://www.postgresql.org/docs/13/release-13.html#E.1.3.3.%20Utility%20Commands)
- ["Introduce the 'force' option for the Drop Database command"](https://git.postgresql.org/gitweb/?p=postgresql.git;a=commitdiff;h=1379fd537f9fc7941c8acff8c879ce3636dbdb77)
- ["Add the support for '-f' option in dropdb utility"](https://git.postgresql.org/gitweb/?p=postgresql.git;a=commitdiff;h=80e05a088e4edd421c9c0374d54d787c8a4c0d86)
