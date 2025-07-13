# Postgres clocks for time consistency

Known: in horizontally scaled applications, server clocks can drift  despite NTP syncing.
New: Using the db (specifically Postgres's `now()`) as the single source of time
authority ensures consistent timestamps across all nodes while maintaining
testability.

## The problem with distributed clocks

Even with NTP, minor clock drift occurs across horizontally scaled deployments:

```go
// This creates inconsistent timestamps across servers
timestamp := time.Now().UTC()
```

Different servers might record slightly different times for simultaneous
events, causing ordering issues or data inconsistencies.

## Using database clock as authority

Postgres's `now()` function provides a single source of time truth:

```sql
INSERT INTO events (name, created_at)
VALUES ('user_signup', now());
```

Benefits:
- Perfect consistency across all application nodes
- Single database serves all servers
- No clock drift between records

## The testing problem

Db time is difficult to stub for tests, making this approach problematic:

```go
// Hard to control in tests
db.Exec("INSERT INTO events (created_at) VALUES (now())")
```

## Hybrid approach with coalesce

Use `coalesce()` to prefer injected timestamps when available, falling back to `now()`:

```sql
-- name: CreateEvent :execrows
INSERT INTO events (name, created_at)
VALUES (
    @name,
    coalesce(
        sqlc.narg('now')::timestamptz,
        now()
    )
);
```

### sqlc configuration

Configure sqlc to handle nullable timestamps:

```yaml
# sqlc.yaml
version: "2"
sql:
  - engine: "postgresql"
    queries: "queries/"
    schema: "schema.sql"
    gen:
      go:
        overrides:
          - db_type: "timestamptz"
            go_type:
              type: "time.Time"
              pointer: true
            nullable: true
```

Generated code:

```go
type CreateEventParams struct {
    Name string
    Now  *time.Time  // Nullable timestamp
}

func (q *Queries) CreateEvent(ctx context.Context, arg CreateEventParams) error {
    _, err := q.db.Exec(ctx, createEvent, arg.Name, arg.Now)
    return err
}
```

## Time generator interface

Create a `TimeGenerator` interface for consistent time handling:

```go
type TimeGenerator interface {
    // Returns current time (stubbed or real)
    NowUTC() time.Time

    // Returns stubbed time pointer or nil
    NowUTCOrNil() *time.Time
}
```

### Production implementation

```go
type UnstubbableTimeGenerator struct{}

func (g *UnstubbableTimeGenerator) NowUTC() time.Time {
    return time.Now().UTC()
}

func (g *UnstubbableTimeGenerator) NowUTCOrNil() *time.Time {
    return nil  // Always use database time
}
```

### Test implementation

```go
type TimeStub struct {
    nowUTC *time.Time
}

func (t *TimeStub) NowUTC() time.Time {
    if t.nowUTC == nil {
        return time.Now().UTC()
    }
    return *t.nowUTC
}

func (t *TimeStub) NowUTCOrNil() *time.Time {
    return t.nowUTC  // Returns stubbed time
}

func (t *TimeStub) StubNowUTC(nowUTC time.Time) {
    t.nowUTC = &nowUTC
}
```

## Integration pattern

Inject the time generator into your service layer:

```go
type Service struct {
    db   *sql.DB
    time TimeGenerator
}

func (s *Service) CreateEvent(ctx context.Context, name string) error {
    return s.queries.CreateEvent(ctx, CreateEventParams{
        Name: name,
        Now:  s.time.NowUTCOrNil(), // nil in prod, stubbed in tests
    })
}
```

### Production setup

```go
service := &Service{
    db:   db,
    time: &UnstubbableTimeGenerator{},
}
```

### Test setup

```go
func TestCreateEvent(t *testing.T) {
    timeStub := &TimeStub{}
    service := &Service{
        db:   testDB,
        time: timeStub,
    }

    // Stub time for predictable tests
    fixedTime := time.Date(2024, 1, 1, 12, 0, 0, 0, time.UTC)
    timeStub.StubNowUTC(fixedTime)

    // Now all database operations use the stubbed time
    err := service.CreateEvent(ctx, "test_event")
    require.NoError(t, err)
}
```

## Real-world example

Queue pause operation with time consistency:

```sql
-- name: QueuePause :execrows
UPDATE queue
SET paused_at = CASE
    WHEN paused_at IS NULL THEN coalesce(
        sqlc.narg('now')::timestamptz,
        now()
    )
    ELSE paused_at
END
WHERE name = @name;
```

Usage:

```go
func (s *Service) PauseQueue(ctx context.Context, name string) error {
    rows, err := s.queries.QueuePause(ctx, QueuePauseParams{
        Name: name,
        Now:  s.time.NowUTCOrNil(),
    })

    if err != nil {
        return err
    }
    if rows == 0 {
        return ErrQueueNotFound
    }
    return nil
}
```

## Important considerations

### Transaction timing

Postgres `now()` returns the transaction start time, not the current moment:

```sql
BEGIN;
SELECT now(); -- Time A
-- ... long operation ...
SELECT now(); -- Still Time A (same transaction)
COMMIT;
```

This can be either helpful (i.e. offering consistent time within transaction)
or problematic (i.e. stale timestamps for long transactions).

### When to use this pattern

**Good for:**
- Critical timestamp consistency requirements
- Audit logs requiring precise ordering
- Multi-node applications with timing-sensitive operations

**Avoid when:**
- Server clocks are sufficient (most cases)
- Simplicity is preferred over microsecond precision
- Transaction duration makes timestamps unrepresentative

### Alternative: Clock-skew with known NTP

For most applications, modern NTP keeps server clocks within acceptable tolerances:

```go
// Simple approach - usually fine
timestamp := time.Now().UTC()
```

