# `uvtrick`: Run Python Code from `venv` in Current Environment

🔗: [uvtrick](https://github.com/koaning/uvtrick)

The following Python code executes the `uses_rich` function in a fresh Python
virtual environment that's...

- managed by `uv`
- using Python 3.12
- ensuring `rich` package is installed and available...even if it's not
  available in the current Python environment

```python
from uvtrick import Env

def uses_rich():
    from rich import print
    print("hi :vampire:")

Env("rich", python="3.12").run(uses_rich)
```

The trick works by taking advantage of `uv`'s speed to perform the following operations, all within the `Env.run()` method:

1. Create a new temp directory
2. Pickle the `args` and `kwargs`, and save them to `pickled_inputs.pickle`
3. Use `inspect.getsource()` to get the source code of the function passed to `run()`
4. Write that source to a `pytemp.py` file, along with the genearted `if __name__ == "__main__":` block responsible for calling the function with pickled inputs, and save its output
to a new, separate pickle file named `tmp.pickle`

Finally, after creating the new temporary Python file, it executes the program using a command
similar to:

```bash
uv run --with rich --python 3.12 --quiet pytemp.py
```

Which reads the output from `tmp.pickle` and returns it to the caller.
Sensational.
