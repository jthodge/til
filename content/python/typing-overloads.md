# Typing Overloads

The `typing` module's `@overload` decorator allows you to define multiple type
signatures for a single function.

Each new function overload communicates with the type checker to tell it exactly
what types to expect when specific parameters are passed into the function.

N.B. Python's `@overload` _does not_ actually define multiple different versions
of the function. `@overload` _does_ tell the type checker to expect different
possible signatures the same single function.

E.g. usage: binding a return type precisely to a literal argument, allowing
any static analysis to treat each individual call site as if it were a different
function:

```python
from __future__ import annotations
from typing import Literal, overload


@overload
def compute(a: int, b: int, mode: Literal["sum"]) -> int:
    ...

@overload
def compute(a: int, b: int, mode: Literal["ratio"]) -> float:
    ...

def compute(a: int, b: int, mode: Literal["sum", "ratio"]) -> int | float:
    if mode == "sum":
        return a + b
    elif mode == "ratio":
        return a / b
    else:                               # never reached; keeps mypy/pylance silent
        raise ValueError("unknown mode")


total = compute(7, 3, "sum")            # → int
total.bit_length()                      # ✅ valid for int

fraction = compute(7, 3, "ratio")       # → float
fraction.as_integer_ratio()             # ✅ valid for float

fraction.bit_length()                   # ❌ type checker error: float has no bit_length()
```

In this case, `@overload` tells the type checker:

- When `mode` is the literal string `"sum"`, then the return type is `int`.
- When `mode` is the literal string `"ratio"`, then the return type is `float`.

Only the final, non-`@overload`ed version of the `compute()` function contains
executable code. The two `@overload`ed stubs are erased at runtime, so there's
no performance cost to include them.

Since the argument is a string literal instead of an arbitrary `str`, static
analyzers treat each call as monomorphic function with a single, concrete
return type. Editors and other tooling can use this single, concrete return
type to surface completion recommendations and catch type errors (e.g. calling
`bit_length()` on a `float`), without needing to perform any manual type
introspection with e.g. `cast()` or `reveal_type()
