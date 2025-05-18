# Django Drops the SQL `DEFAULT` Constraint When Creating New Columns

Django _does not_ use database-level `DEFAULT`s.

Instead, Django handles the `default` model field option at the application level — _not_ the database level.

> "[Django never sets database defaults and always applies them in the Django ORM code.](https://docs.djangoproject.com/en/2.2/ref/migration-operations/#:~:text=the%20database%20directly%20%2D-,Django%20never%20sets%20database%20defaults%20and%20always%20applies%20them%20in%20the%20Django%20ORM%20code.,-Warning)"

When adding a new non-nullable column to an existing table, relational databases require a default value for this new column in order to perform the `ALTER TABLE ... ADD COLUMN` operation.

In Django, `makemigrations` will attempt to infer the correct default value from the application-level `default` option on the field, when available. If a `default` option isn't available on the field, then Django halts `makemigrations` and prompts for a `default` value in the command line before proceeding. In each of these cases, the `DEFAULT` constraint is applied (again, _using the application-level value — not the database-level value_), and then it's removed.
