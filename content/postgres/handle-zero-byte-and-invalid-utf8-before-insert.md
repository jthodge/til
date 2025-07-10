# Handle Zero Byte and Invalid UTF-8 Before Insert

Postgres rejects text containing `0x00` (zero byte) or invalid UTF-8 sequences.
But most programming languages accept them.
This asymmetric support can lead to errors when data flows from application to database.

## The Problem

Postgres explicitly disallows zero bytes in text/varchar columns:

```sql
-- This will fail
INSERT INTO logs (message) VALUES ('Hello' || CHR(0) || 'World');
-- ERROR: invalid byte sequence for encoding "UTF8": 0x00

-- Invalid UTF-8 also fails
INSERT INTO logs (message) VALUES (E'\xc3\x28');
-- ERROR: invalid byte sequence for encoding "UTF8": 0xc3 0x28
```

## Validation at Input Boundaries

Prevent invalid data from entering your system:

```python
# E.g.  simple validation function
def validate_postgres_text(text: str) -> bool:
    """Check if text is safe for Postgres insertion."""
    if not text:
        return False

    # Check for zero bytes
    if '\x00' in text:
        return False

    # Check for valid UTF-8
    try:
        text.encode('utf-8').decode('utf-8')
    except UnicodeDecodeError:
        return False

    return True

# Flask request validation
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

def sanitize_postgres_input(f):
    """Decorator to sanitize all string inputs for Postgres."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.json:
            sanitized = {}
            for key, value in request.json.items():
                if isinstance(value, str):
                    # Remove zero bytes
                    value = value.replace('\x00', '')
                    # Ensure valid UTF-8
                    value = value.encode('utf-8', 'ignore').decode('utf-8')
                sanitized[key] = value
            request.json = sanitized
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/comments', methods=['POST'])
@sanitize_postgres_input
def create_comment():
    # Safe to insert - zero bytes and invalid UTF-8 removed
    comment_text = request.json.get('text', '')
    # ... insert to database
```

## Sanitizing for Logging and Debugging

It's possible to preserve problematic input for debugging:

```javascript
// Replacement approach
function sanitizeForPostgres(str) {
    if (!str) return str;

    // Replace zero bytes with visible marker
    str = str.replace(/\x00/g, '[NULL]');

    // Replace invalid UTF-8 sequences
    // JavaScript strings are UTF-16, so we check during encoding
    try {
        // Encode and decode to verify UTF-8 validity
        const encoded = new TextEncoder().encode(str);
        str = new TextDecoder('utf-8', { fatal: true }).decode(encoded);
    } catch (e) {
        // Fall back to replacing common invalid patterns
        str = str.replace(/[\uD800-\uDBFF](?![\uDC00-\uDFFF])/g, '[INVALID]');
        str = str.replace(/(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/g, '[INVALID]');
    }

    return str;
}

// Express middleware for request logging
const express = require('express');
const app = express();

// Middleware to log all requests with sanitized data
app.use((req, res, next) => {
    const logEntry = {
        method: req.method,
        path: sanitizeForPostgres(req.path),
        userAgent: sanitizeForPostgres(req.get('user-agent')),
        body: req.body ? sanitizeForPostgres(JSON.stringify(req.body)) : null,
        timestamp: new Date()
    };

    // Safe to insert to Postgres
    db.query(
        'INSERT INTO request_logs (method, path, user_agent, body, timestamp) VALUES ($1, $2, $3, $4, $5)',
        [logEntry.method, logEntry.path, logEntry.userAgent, logEntry.body, logEntry.timestamp]
    );

    next();
});
```

## Database-Level Protection

Add constraints as a last line of defense:

```sql
-- Create a domain type that validates text
CREATE DOMAIN safe_text AS TEXT
CHECK (
    VALUE !~ '\x00' AND  -- No zero bytes
    VALUE = convert_from(convert_to(VALUE, 'UTF8'), 'UTF8')  -- Valid UTF-8
);

-- Use in table definitions
CREATE TABLE user_content (
    id SERIAL PRIMARY KEY,
    title safe_text NOT NULL,
    body safe_text
);

-- Or add check constraints to existing tables
ALTER TABLE comments
ADD CONSTRAINT no_zero_bytes
CHECK (message !~ '\x00');
```

## Common Sources of Invalid Input

1. **Security scanners** - Pentest tools often send zero bytes
2. **Copy-paste from binary files** - Users accidentally including non-text data
3. **Encoding mismatches** - Data from systems using different character encodings
4. **Malicious actors** - Attempting SQL injection or buffer overflow attacks

## Best Practices

1. **Validate at the edge** - Check input as early as possible
2. **Sanitize for storage** - Replace invalid sequences when you must store them
3. **Use placeholders** - `[NULL]` or `[INVALID_UTF8]` make issues visible
4. **Log attempts** - Track where invalid input originates
5. **Return clear errors** - Help legitimate users fix their input

