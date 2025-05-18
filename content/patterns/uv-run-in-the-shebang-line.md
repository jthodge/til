# `uv run` in the Shebang Line

Beginning a script with `#!/usr/bin/env -S uv run` and then `chmod 755` the script.

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "flask==3.*",
# ]
# ///
import flask
# ...
```

This allows you to run the script on any machine with the `uv` binary installed
via `./script.py`.

And, it will automatically:

1. Create its own isolated, sandboxed environment
2. Install all required dependencies in the environment
3. Run itself in that environment (even using the correctly installed version
   of Python)

via [alsuren](https://github.com/alsuren) ➡️ [diff](https://github.com/alsuren/sixdofone/pull/8/files#diff-568470d013cd12e4f388206520da39ab9a4e4c3c6b95846cbc281abc1ba3c959R1)