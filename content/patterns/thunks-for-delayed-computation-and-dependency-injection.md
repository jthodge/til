# Thunks for Delayed Computation and Dependency Injection

A thunk is a function that takes no arguments and returns a value.
Thunks can be used to delay computation and manage dependencies between modules.

## What Are Thunks?

Thunks are lexical closures that capture their creation environment, which affords separating  "what to compute" from "when to compute it". E.g.:

```python
def create_counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    # Return a thunk that captures the current count
    def get_count_thunk():
        return lambda: count

    return increment, get_count_thunk

increment, get_thunk = create_counter()
count_thunk = get_thunk()

print(count_thunk())  # 0
increment()
print(count_thunk())  # 1 - thunk always returns current value
```

## Delayed Computation

Thunks defer expensive operations until actually needed:

```python
import time
from typing import Callable

def expensive_computation() -> str:
    """Simulate an expensive operation."""
    time.sleep(2)
    return "computed_value"

# Create a thunk instead of computing immediately
result_thunk: Callable[[], str] = lambda: expensive_computation()

# Computation only happens when invoked
print("Thunk created...")
# ... do other work ...
print(f"Result: {result_thunk()}")  # Now it computes
```

## Dependency Injection Pattern

Thunks provide a pleasant pattern for injecting dependencies:

```python
# Configuration module
class Config:
    def __init__(self):
        self.api_key = None
        self.base_url = None

    def update(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    def get_api_key_thunk(self):
        """Return a thunk for the current API key."""
        return lambda: self.api_key

    def get_base_url_thunk(self):
        """Return a thunk for the current base URL."""
        return lambda: self.base_url

# Service module that uses thunks
class ApiService:
    def __init__(self, api_key_thunk, base_url_thunk):
        # Store thunks, not values
        self._api_key_thunk = api_key_thunk
        self._base_url_thunk = base_url_thunk

    def make_request(self, endpoint: str):
        # Get current values when needed
        api_key = self._api_key_thunk()
        base_url = self._base_url_thunk()

        return f"GET {base_url}/{endpoint} with key: {api_key}"

# Usage
config = Config()
api_key_thunk = config.get_api_key_thunk()
base_url_thunk = config.get_base_url_thunk()

service = ApiService(api_key_thunk, base_url_thunk)

# Values can change after service creation
config.update("new-key-123", "https://api.example.com")
print(service.make_request("users"))  # Uses updated values
```

## Shared State Management

Thunks can be used to manage shared application state:

```python
import threading
import time
from datetime import datetime

class MetricsCollector:
    """Collects and updates metrics in a background thread."""

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.last_update = datetime.now()
        self._lock = threading.Lock()

    def increment_requests(self):
        with self._lock:
            self.request_count += 1
            self.last_update = datetime.now()

    def increment_errors(self):
        with self._lock:
            self.error_count += 1
            self.last_update = datetime.now()

    def get_metrics_thunk(self):
        """Return a thunk that safely captures current metrics."""
        def metrics_snapshot():
            with self._lock:
                return {
                    'requests': self.request_count,
                    'errors': self.error_count,
                    'error_rate': self.error_count / max(self.request_count, 1),
                    'last_update': self.last_update
                }
        return metrics_snapshot

# Dashboard component receives thunk
class Dashboard:
    def __init__(self, metrics_thunk):
        self.get_metrics = metrics_thunk

    def render(self):
        # Always gets fresh data when rendered
        metrics = self.get_metrics()
        return f"""
        Dashboard (updated: {metrics['last_update']})
        Requests: {metrics['requests']}
        Errors: {metrics['errors']}
        Error Rate: {metrics['error_rate']:.2%}
        """

# Usage
collector = MetricsCollector()
dashboard = Dashboard(collector.get_metrics_thunk())

# Simulate activity
collector.increment_requests()
collector.increment_requests()
collector.increment_errors()

print(dashboard.render())  # Shows current metrics
```

## Benefits Over Global Variables

1. **Explicit Dependencies**: Modules must explicitly receive thunks
2. **Read-Only Access**: Thunks can provide values without allowing modification
3. **Late Binding**: Values are resolved when needed, not when passed
4. **Testability**: Easy to mock thunks for testing

Thunks provide an elegant and sophisticated pattern for managing shared state, delaying computation, and creating cleaner module boundaries without resorting to global variables.
