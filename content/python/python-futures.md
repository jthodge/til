# Python's `Future`s

Python provides native Promise-like concurrency through `concurrent.futures.Future` objects, enabling asynchronous programming patterns similar to JavaScript. These objects act as containers for results that will be available in the future, with built-in support for callbacks, timeouts, cancellation, and exception handling.

## Creating and Using Basic Futures

A Future represents a computation that may not have completed yet. You can create one manually and set its result when ready:

```python
from concurrent.futures import Future
import threading
import time

# Create a Future container
future = Future()

def background_computation():
    # Simulate work
    time.sleep(1)
    result = sum(range(1000000))
    future.set_result(result)

# Start computation in background
thread = threading.Thread(target=background_computation)
thread.start()

# Check completion status
print(f"Done yet? {future.done()}")  # False

# Block until result is ready
print(f"Result: {future.result()}")  # Result: 499999500000
```

## Callback Support Like JavaScript's `.then()`

Futures support event-driven programming through callbacks that fire when the result becomes available:

```python
from concurrent.futures import Future
import threading

def process_result(future):
    try:
        value = future.result()
        print(f"Processing result: {value}")
        # Chain another operation
        derived_future = Future()
        derived_future.set_result(value * 2)
        return derived_future
    except Exception as e:
        print(f"Error occurred: {e}")

# Create and configure future
future = Future()
future.add_done_callback(process_result)

# Callbacks work even after completion
def async_compute():
    import time
    time.sleep(0.5)
    future.set_result(21)

threading.Thread(target=async_compute).start()
# After 0.5s prints: Processing result: 21
```

## Control Operations: Timeouts, Cancellation, and Exceptions

Futures provide robust control mechanisms for managing asynchronous operations:

```python
from concurrent.futures import Future, CancelledError
import threading
import time

# Timeout example
def slow_operation():
    future = Future()

    def work():
        time.sleep(3)
        if not future.cancelled():
            future.set_result("Finally done!")

    threading.Thread(target=work).start()
    return future

future = slow_operation()
try:
    # Wait maximum 1 second
    result = future.result(timeout=1.0)
except TimeoutError:
    print("Operation too slow, cancelling...")
    future.cancel()  # May fail if already running

# Exception handling
def failing_operation():
    future = Future()
    future.set_exception(RuntimeError("Database connection failed"))
    return future

error_future = failing_operation()
print(f"Has exception? {error_future.exception() is not None}")  # True

try:
    error_future.result()
except RuntimeError as e:
    print(f"Caught: {e}")  # Caught: Database connection failed
```

## Integration with `asyncio` and `async`/`await`

The `asyncio` module provides its own Future implementation that works seamlessly with coroutines:

```python
import asyncio

async def async_producer(future):
    await asyncio.sleep(1)
    future.set_result("Async result ready!")

async def async_consumer():
    # Create asyncio Future
    future = asyncio.Future()

    # Schedule producer
    asyncio.create_task(async_producer(future))

    # Await future like any coroutine
    result = await future
    return result.upper()

# Run async code
result = asyncio.run(async_consumer())
print(result)  # ASYNC RESULT READY!

# Using futures for synchronization
async def coordinate_workers():
    start_signal = asyncio.Future()
    results = []

    async def worker(worker_id):
        # Wait for start signal
        await start_signal
        result = f"Worker {worker_id} processed {start_signal.result()}"
        results.append(result)

    # Create workers
    tasks = [asyncio.create_task(worker(i)) for i in range(3)]

    # Start all workers simultaneously
    await asyncio.sleep(0.1)  # Let workers initialize
    start_signal.set_result("shared data")

    # Wait for completion
    await asyncio.gather(*tasks)
    return results

results = asyncio.run(coordinate_workers())
print(results)  # ['Worker 0 processed shared data', ...]
```

## Automatic Future Management with Executors

`ThreadPoolExecutor` and `ProcessPoolExecutor` handle Future creation automatically:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

def analyze_data(dataset_id):
    # Simulate variable processing time
    process_time = random.uniform(0.5, 2.0)
    time.sleep(process_time)

    # Simulate occasional failures
    if dataset_id == 7:
        raise ValueError(f"Dataset {dataset_id} corrupted")

    return {
        'id': dataset_id,
        'records': random.randint(1000, 5000),
        'process_time': round(process_time, 2)
    }

# Process multiple datasets concurrently
with ThreadPoolExecutor(max_workers=4) as executor:
    # Submit all tasks, get futures immediately
    future_to_id = {
        executor.submit(analyze_data, i): i
        for i in range(10)
    }

    # Process results as they complete
    completed = 0
    for future in as_completed(future_to_id):
        dataset_id = future_to_id[future]
        try:
            result = future.result()
            completed += 1
            print(f"✓ Dataset {result['id']}: "
                  f"{result['records']} records in {result['process_time']}s")
        except Exception as e:
            print(f"✗ Dataset {dataset_id} failed: {e}")

# Simpler map interface for ordered results
def fetch_user_data(user_id):
    # Simulate API call
    time.sleep(0.3)
    return {'user_id': user_id, 'name': f'User-{user_id}'}

with ThreadPoolExecutor(max_workers=5) as executor:
    user_ids = [101, 102, 103, 104, 105]
    # Results returned in order, regardless of completion time
    for user_data in executor.map(fetch_user_data, user_ids):
        print(f"Fetched: {user_data}")
```

## Practical Future Patterns

Futures excel at coordinating complex asynchronous workflows:

```python
from concurrent.futures import Future, ThreadPoolExecutor
import time

class TaskPipeline:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)

    def stage1_fetch(self, url):
        """Simulate fetching data"""
        time.sleep(0.5)
        return f"Data from {url}"

    def stage2_process(self, data):
        """Simulate processing"""
        time.sleep(0.3)
        return f"Processed: {data}"

    def stage3_save(self, processed_data):
        """Simulate saving"""
        time.sleep(0.2)
        return f"Saved: {processed_data}"

    def run_pipeline(self, url):
        # Chain operations using futures
        fetch_future = self.executor.submit(self.stage1_fetch, url)

        # Create dependent future
        process_future = Future()

        def chain_processing(f):
            try:
                data = f.result()
                # Submit next stage
                result = self.executor.submit(self.stage2_process, data)
                # Transfer result to dependent future
                result.add_done_callback(
                    lambda f2: process_future.set_result(f2.result())
                )
            except Exception as e:
                process_future.set_exception(e)

        fetch_future.add_done_callback(chain_processing)
        return process_future

    def shutdown(self):
        self.executor.shutdown()

# Use the pipeline
pipeline = TaskPipeline()
final_future = pipeline.run_pipeline("https://api.example.com")
print(final_future.result())  # Processed: Data from https://api.example.com
pipeline.shutdown()
```

Python's Future objects provide a powerful abstraction for concurrent programming, bridging the gap between thread-based and async/await paradigms while offering fine-grained control over asynchronous operations.
