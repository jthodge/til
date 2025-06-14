# Use the timeout command to limit execution time

The `timeout` command in Linux/Unix systems provides a simple way to run commands with a time limit. It automatically terminates a process if it runs longer than the specified duration, helping prevent scripts from hanging indefinitely.

## Basic syntax

```bash
timeout <duration> <command>
```

The duration can be specified with units:
- `s` for seconds (default if no unit specified)
- `m` for minutes  
- `h` for hours
- `d` for days

## Examples

### Basic usage

```bash
# Kill a sleep command after 2 seconds
timeout 2s sleep 10

# Check the exit code (124 indicates timeout occurred)
echo $?  # Returns 124
```

### Monitoring service startup

```bash
# Wait for a web service to become available, but give up after 30 seconds
timeout 30s bash -c 'until curl -s http://localhost:8080; do sleep 1; done'
```

### Preventing infinite loops

```bash
# Run a potentially long-running data processing script with a 1 hour limit
timeout 1h python process_large_dataset.py
```

### Custom termination signal

By default, `timeout` sends SIGTERM. You can specify a different signal:

```bash
# Send SIGKILL instead of SIGTERM
timeout --signal=KILL 5s long_running_process

# Or use the signal number
timeout --signal=9 5s long_running_process
```

## Working with shell built-ins

The `timeout` command cannot directly wrap shell built-ins like `while`, `until`, or `for`. You need to use `bash -c`:

```bash
# This won't work
timeout 5s until false; do echo "Running..."; done

# This works - wrap in bash -c
timeout 5s bash -c 'until false; do echo "Running..."; sleep 1; done'
```

## Exit codes

- `0`: Command completed successfully before timeout
- `124`: Command was terminated by timeout
- `125`: timeout command itself failed
- `126`: Command found but cannot be executed
- `127`: Command not found
- Other: Exit code from the command itself

## Practical example: Database connection check

```bash
#!/bin/bash
# Check if database is ready, timeout after 60 seconds

if timeout 60s bash -c 'until pg_isready -h localhost -p 5432; do sleep 2; done'; then
    echo "Database is ready!"
else
    echo "Database connection timed out after 60 seconds"
    exit 1
fi
```

The `timeout` command is particularly useful in CI/CD pipelines, monitoring scripts, and any situation where you need to ensure a command doesn't run indefinitely.