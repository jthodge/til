# Use Real Database Fixtures Instead of Mocks

Testing with real db connections and fixtures offers higher fidelity than mocking, and modern databases are fast enough that performance concerns are largely outdated.

## Why Avoid Database Mocks

Mocks can't replicate actual database behavior:
- They bypass database constraints and validations
- They may allow invalid data that would fail in production
- They don't catch SQL syntax errors or query logic issues

## Real Fixtures Are Fast

Modern databases handle test data efficiently. With proper setup, you can achieve:
- ~780 database fixtures per second
- ~100 microseconds per complex record insertion
- Parallel test execution without conflicts

## Best Practices for Database Testing

### Create Fixture Utility Functions

Build standardized test data generators with sensible defaults:

```python
import time
from datetime import datetime
from typing import Optional, Dict, Any

def create_test_user(db_connection, **overrides) -> Dict[str, Any]:
    """Create a test user with sensible defaults."""
    defaults = {
        "name": "Test User",
        "email": f"test-{int(time.time() * 1000000)}@example.com",
        "active": True,
        "created_at": datetime.now()
    }

    # Apply any overrides
    user_data = {**defaults, **overrides}

    # Insert and return the created user
    cursor = db_connection.cursor()
    cursor.execute("""
        INSERT INTO users (name, email, active, created_at)
        VALUES (%(name)s, %(email)s, %(active)s, %(created_at)s)
        RETURNING id, name, email, active, created_at
    """, user_data)

    result = cursor.fetchone()
    return {
        "id": result[0],
        "name": result[1],
        "email": result[2],
        "active": result[3],
        "created_at": result[4]
    }
```

### Use Transactions

Wrap each test in a transaction for isolation and cleanup:

```python
import pytest
from contextlib import contextmanager

@contextmanager
def test_transaction(connection):
    transaction = connection.begin()
    try:
        yield connection
    finally:
        transaction.rollback()

def test_user_creation(db_connection):
    with test_transaction(db_connection) as conn:
        user = create_test_user(conn, email="unique@test.com")
        assert user.id is not None
        assert user.email == "unique@test.com"
        # Transaction rollback ensures cleanup
```

### Enable Parallel Testing

Modern test frameworks support parallel execution with proper database isolation:

```python
import pytest
import psycopg2
from psycopg2.pool import ThreadedConnectionPool

# Create a connection pool for parallel tests
test_pool = ThreadedConnectionPool(
    minconn=1,
    maxconn=20,
    database="test_db",
    user="test_user"
)

@pytest.mark.parametrize("execution_number", range(10))
def test_user_operations_parallel(execution_number):
    """Tests can run in parallel with proper isolation."""
    conn = test_pool.getconn()
    try:
        with conn:
            with conn.cursor() as cursor:
                # Each test gets its own transaction
                user = create_test_user(conn)

                # Test operations with real database constraints
                cursor.execute("""
                    UPDATE users
                    SET email = %s
                    WHERE id = %s
                """, ("invalid-email", user["id"]))

                # This would fail due to email validation constraint
                with pytest.raises(psycopg2.IntegrityError):
                    conn.commit()
    finally:
        test_pool.putconn(conn)
```

### Use Database Constraints

Let the database validate your test data:

```sql
-- Schema with comprehensive constraints
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    plan VARCHAR(50) NOT NULL CHECK (plan IN ('starter', 'growth', 'enterprise')),
    seats_limit INTEGER NOT NULL CHECK (seats_limit > 0),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('owner', 'admin', 'member')),
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    -- Ensure org owners can't be deactivated
    CONSTRAINT active_owner CHECK (NOT (role = 'owner' AND active = false))
);

CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    status VARCHAR(50) NOT NULL CHECK (status IN ('trialing', 'active', 'past_due', 'canceled')),
    current_period_end TIMESTAMP NOT NULL,
    mrr_cents INTEGER NOT NULL CHECK (mrr_cents >= 0),
    -- Ensure only one active subscription per org
    CONSTRAINT one_active_subscription UNIQUE (organization_id, status)
        WHERE status IN ('trialing', 'active', 'past_due')
);
```

## Performance Tips

1. **Use connection pooling** - Reuse database connections across tests
2. **Minimize setup/teardown** - Use transactions instead of recreating schemas
3. **Generate data programmatically** - Avoid loading large SQL fixtures
4. **Run tests in parallel** - Modern databases handle concurrent connections well

The small performance cost of using real db's is worth the large increase in test reliability and robustness.
