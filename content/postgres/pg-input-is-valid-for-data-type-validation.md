# pg_input_is_valid for Data Type Validation

Postgres 16+ provides the `pg_input_is_valid` function to safely check if a value can be cast to a specific data type without raising an error. This is especially useful when importing semi-structured data! And `pg_input_is_valid` mames  data imports more robust by allowing you to gracefully handle bad data instead of just failing.

## Basic Usage

```sql
-- Check if a string can be cast to a type
SELECT pg_input_is_valid('123', 'integer');      -- true
SELECT pg_input_is_valid('abc', 'integer');      -- false
SELECT pg_input_is_valid('2024-01-01', 'date');  -- true
SELECT pg_input_is_valid('not-a-date', 'date');  -- false
```

## Validating During Data Import

### Safe Column Conversion

Instead of failing on bad data, convert only valid values:

```sql
-- Create staging table with all text columns
CREATE TABLE user_import_staging (
    user_id TEXT,
    email TEXT,
    age TEXT,
    signup_date TEXT,
    monthly_spend TEXT
);

-- Import with validation and type conversion
INSERT INTO users (user_id, email, age, signup_date, monthly_spend)
SELECT
    user_id::uuid,
    email,
    CASE
        WHEN pg_input_is_valid(age, 'integer') THEN age::integer
        ELSE NULL
    END,
    CASE
        WHEN pg_input_is_valid(signup_date, 'date') THEN signup_date::date
        ELSE NULL
    END,
    CASE
        WHEN pg_input_is_valid(monthly_spend, 'numeric') THEN monthly_spend::numeric
        ELSE 0.00
    END
FROM user_import_staging
WHERE pg_input_is_valid(user_id, 'uuid')  -- Skip rows with invalid UUIDs
  AND email IS NOT NULL;
```

### Identifying Invalid Data

Find problematic rows before processing:

```sql
-- Find all rows with invalid data
SELECT
    *,
    NOT pg_input_is_valid(user_id, 'uuid') AS invalid_uuid,
    NOT pg_input_is_valid(age, 'integer') AS invalid_age,
    NOT pg_input_is_valid(signup_date, 'date') AS invalid_date,
    NOT pg_input_is_valid(monthly_spend, 'numeric') AS invalid_spend
FROM user_import_staging
WHERE NOT pg_input_is_valid(user_id, 'uuid')
   OR NOT pg_input_is_valid(age, 'integer')
   OR NOT pg_input_is_valid(signup_date, 'date')
   OR NOT pg_input_is_valid(monthly_spend, 'numeric');

-- Count validation issues by column
SELECT
    COUNT(*) FILTER (WHERE NOT pg_input_is_valid(user_id, 'uuid')) AS invalid_uuids,
    COUNT(*) FILTER (WHERE NOT pg_input_is_valid(age, 'integer')) AS invalid_ages,
    COUNT(*) FILTER (WHERE NOT pg_input_is_valid(signup_date, 'date')) AS invalid_dates,
    COUNT(*) FILTER (WHERE NOT pg_input_is_valid(monthly_spend, 'numeric')) AS invalid_spends
FROM user_import_staging;
```

## Complex Data Type Validation

### JSON Validation

```sql
-- Validate JSON structure
SELECT
    config_data,
    pg_input_is_valid(config_data, 'json') AS is_valid_json,
    pg_input_is_valid(config_data, 'jsonb') AS is_valid_jsonb
FROM app_configs;

-- Import only valid JSON
INSERT INTO settings (user_id, preferences)
SELECT
    user_id,
    preferences::jsonb
FROM settings_import
WHERE pg_input_is_valid(preferences, 'jsonb');
```

### Array and Custom Types

```sql
-- Validate array inputs
SELECT pg_input_is_valid('{1,2,3}', 'integer[]');        -- true
SELECT pg_input_is_valid('{1,2,abc}', 'integer[]');      -- false
SELECT pg_input_is_valid('{"a","b","c"}', 'text[]');     -- true

-- Validate enum types
CREATE TYPE order_status AS ENUM ('pending', 'shipped', 'delivered');
SELECT pg_input_is_valid('pending', 'order_status');      -- true
SELECT pg_input_is_valid('cancelled', 'order_status');    -- false

-- Validate composite types
CREATE TYPE address AS (
    street TEXT,
    city TEXT,
    postal_code TEXT
);
SELECT pg_input_is_valid('("123 Main St","Boston","02101")', 'address');  -- true
```

## Building Validation Functions

Create reusable validation functions for complex imports:

```sql
CREATE OR REPLACE FUNCTION validate_import_row(
    p_row record,
    OUT is_valid boolean,
    OUT validation_errors text[]
) AS $$
DECLARE
    v_errors text[] := '{}';
BEGIN
    -- Check each field
    IF NOT pg_input_is_valid(p_row.order_id, 'uuid') THEN
        v_errors := v_errors || 'Invalid UUID in order_id';
    END IF;

    IF NOT pg_input_is_valid(p_row.order_date, 'timestamptz') THEN
        v_errors := v_errors || 'Invalid timestamp in order_date';
    END IF;

    IF NOT pg_input_is_valid(p_row.amount, 'numeric(10,2)') THEN
        v_errors := v_errors || 'Invalid numeric in amount';
    END IF;

    IF NOT pg_input_is_valid(p_row.items, 'jsonb') THEN
        v_errors := v_errors || 'Invalid JSON in items';
    END IF;

    is_valid := (array_length(v_errors, 1) IS NULL);
    validation_errors := v_errors;
END;
$$ LANGUAGE plpgsql;

-- Use the validation function
SELECT
    *,
    (validate_import_row(import.*)).*
FROM order_imports import
WHERE NOT (validate_import_row(import.*)).is_valid;
```

## Performance Considerations

```sql
-- Create partial indexes for frequently validated columns
CREATE INDEX idx_staging_valid_dates
ON staging_table (signup_date)
WHERE pg_input_is_valid(signup_date, 'date');

-- Materialize validation results for large datasets
CREATE MATERIALIZED VIEW import_validation AS
SELECT
    *,
    pg_input_is_valid(user_id, 'uuid') AS valid_uuid,
    pg_input_is_valid(email, 'email') AS valid_email,
    pg_input_is_valid(age, 'integer') AS valid_age,
    pg_input_is_valid(signup_date, 'date') AS valid_date
FROM user_import_staging;

-- Process in batches based on validation status
WITH valid_batch AS (
    SELECT * FROM import_validation
    WHERE valid_uuid AND valid_email AND valid_age AND valid_date
    LIMIT 10000
)
INSERT INTO users
SELECT user_id::uuid, email, age::integer, signup_date::date
FROM valid_batch;
```

## Best Practices

1. **Always validate before casting** - Prevent runtime errors in production
2. **Log invalid data** - Keep audit trail of what couldn't be imported
3. **Use staging tables** - Import as text first, then validate and convert
4. **Batch processing** - For large imports, process valid/invalid data separately
5. **Consider NULL handling** - Decide if invalid data becomes NULL or skips the row

