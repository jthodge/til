# UUID v7 Monotonic Per Backend

Postgres UUID v7 implementation ensures monotonic ordering within each backend
by using 12 bits of sub-millisecond precision instead of pure randomness.

This ordering combines the best of:
- (satisficing) collision resistance
- sequential IDs

This balance makes them ideal for ordered operations and testing, as well as
for use in high-write systems and simpler business logic..

## Why Does It Matter?

UUID v4 generates truly random identifiers with no ordering guarantees:

```sql
-- UUID v4: completely random, no ordering
SELECT gen_random_uuid() FROM generate_series(1,5);
-- 550e8400-e29b-41d4-a716-446655440000
-- 2c5ea4c0-4067-11e9-8bad-9b1deb4d3b7d
-- 110ec58a-a0f2-4ac2-8c5c-a87c8c8b4a4e
-- (order varies each run)

-- UUID v7: time-ordered with monotonic guarantee
SELECT gen_uuid_v7() FROM generate_series(1,5);
-- 018d3c8f-1234-7abc-8def-123456789abc
-- 018d3c8f-1234-7abd-8def-123456789abc
-- 018d3c8f-1234-7abe-8def-123456789abc
-- (always increasing within same backend)
```

## Monotonicity Implementation

UUID v7 achieves ordering through enhanced timestamp precision:

```
UUIDv7 Structure:
┌─────────── 48 bits ─────────────┬─ 4 ─┬─── 12 bits ───┬─ 2 ─┬── 62 bits ───┐
│        unix_ts_ms               │ ver │    rand_a     │ var │   rand_b     │
└─────────────────────────────────┴─────┴───────────────┴─────┴──────────────┘

Where rand_a = sub-millisecond timestamp (not random)
```

The 12 `rand_a` bits store fractional milliseconds, providing 4096 distinct
values within each millisecond.

## Benefits

### Simplified Testing

```python
# E.g. creating ordered test data
def test_user_pagination():
    # No need to sort - UUID v7 guarantees order
    users = [create_user(f"user{i}") for i in range(5)]

    # IDs are automatically in creation order
    response = api_get('/users?limit=3')
    assert response['users'][0]['id'] == users[0].id
    assert response['users'][1]['id'] == users[1].id

# E.g. event sourcing
def test_event_stream_ordering():
    # Events created in sequence have ordered IDs
    events = [
        create_event('user_created', user_id=123),
        create_event('profile_updated', user_id=123),
        create_event('email_verified', user_id=123)
    ]

    # Query by ID range automatically gives chronological order
    stream = db.query("SELECT * FROM events WHERE id >= ? ORDER BY id", events[0].id)
    assert [e.type for e in stream] == ['user_created', 'profile_updated', 'email_verified']
```

### Database Performance

```sql
-- B-tree inserts are more efficient with ordered UUIDs
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_uuid_v7(),
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inserts append to index (fast) instead of random positions (slow)
INSERT INTO messages (content) VALUES
    ('First message'),
    ('Second message'),
    ('Third message');
-- UUIDs will be in order: 018d... < 018d... < 018d...
```

### API Pagination

```python
# Cursor-based pagination with UUID v7
def get_messages(cursor=None, limit=20):
    if cursor:
        # UUID v7 ordering enables efficient cursor pagination
        query = "SELECT * FROM messages WHERE id > ? ORDER BY id LIMIT ?"
        return db.execute(query, (cursor, limit))
    else:
        query = "SELECT * FROM messages ORDER BY id LIMIT ?"
        return db.execute(query, (limit,))

# Frontend can use last ID as cursor
messages = get_messages()
next_batch = get_messages(cursor=messages[-1]['id'])
```

## Limitations and Considerations

### Single Backend Only

```python
# Monotonicity guaranteed within same connection
with db.connection() as conn:
    id1 = conn.execute("SELECT gen_uuid_v7()").fetchone()[0]
    id2 = conn.execute("SELECT gen_uuid_v7()").fetchone()[0]
    assert id1 < id2  # Always true

# NOT guaranteed across different connections
conn1 = db.connection()
conn2 = db.connection()
id1 = conn1.execute("SELECT gen_uuid_v7()").fetchone()[0]
id2 = conn2.execute("SELECT gen_uuid_v7()").fetchone()[0]
# id1 < id2 might be false
```

### Reduced Randomness

UUID v7 has 62 bits of randomness instead of v4's 122 bits,
But still, collision probability remains negligible for most  use cases.

## Migration Considerations

```sql
-- Gradual migration from UUID v4 to v7
ALTER TABLE users ALTER COLUMN id SET DEFAULT gen_uuid_v7();

-- Existing v4 UUIDs remain valid
-- New records get v7 UUIDs
-- Mixed ordering within table (v4 scattered, v7 clustered)

-- For pure v7 ordering, consider new table or data migration
```
