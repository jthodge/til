# Cross-Table Row Deletions

*Context*
Need to `DELETE` all rows from a table satisfying a certain condition based on a value in another table.

*Assumptions*
Table: `Person`
`Person` Columns: `person_id`, `city_id`, `email`

Table: `City`
`City` Columns: `city_id`, `name`, `population`

```sql
CREATE TABLE City (
    city_id INT PRIMARY KEY,
    name TEXT,
    population INT
);

CREATE TABLE Person (
    person_id INT PRIMARY KEY,
    email TEXT,
    city_id INT,
    FOREIGN KEY (city_id) REFERENCES City(city_id)
);

INSERT INTO
    City (city_id, name, population)
VALUES 
    (1, 'New York', 8419000), 
    (2, 'Los Angeles', 3971000), 
    (3, 'Chicago', 2716000), 
    (4, 'Houston', 2325500), 
    (5, 'Phoenix', 1680000);

INSERT INTO
    Person (person_id, email, city_id)
VALUES
    (1, 'john@doe.com', 1),
    (2, 'jane@doe.com', 2),
    (3, 'jim@doe.com', 3),
    (4, 'jill@doe.com', 4),
    (5, 'joe@doe.com', 5);
```

*Goal*
Delete all people from cities with a population of less than 1,000,000 people.

*Solution*
Standard-compliant solution:

```sql
DELETE FROM Person
WHERE
    city_id IN (
        SELECT
            city_id
        FROM
            City
        WHERE
            population < 1000000
    );
```

`USING` (Extension)[^1] solution:

```sql
DELETE FROM Person USING City
WHERE
    Person.city_id = City.city_id
    AND City.population < 1000000;
```

[^1]: [This command does not conform to the SQL standard](https://www.postgresql.org/docs/current/sql-delete.html). `USING` and `RETURNING` clauses
are postgres exentions.
