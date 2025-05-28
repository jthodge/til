# Create Dual-Purpose Attributes with Proxy Properties

Python's descriptor protocol enables creating attributes that act as both properties and methods through clever use of `__get__`, `__call__`, and `__repr__` magic methods.

```python
from typing import Callable, Generic, TypeVar, ParamSpec, Self

P = ParamSpec("P")
R = TypeVar("R")

class ProxyProperty(Generic[P, R]):
    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func

    def __get__(self, instance: object, _=None) -> Self:
        self.instance = instance
        return self

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.func(self.instance, *args, **kwargs)

    def __repr__(self) -> str:
        return self.func(self.instance)
```

This creates attributes with dual behavior:

```python
def proxy_property(func: Callable[P, R]) -> ProxyProperty[P, R]:
    return ProxyProperty(func)

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @proxy_property
    def endpoint(self, path: str = "/") -> str:
        return f"{self.base_url}{path}"

    @proxy_property
    def timeout(self, seconds: int = 30) -> int:
        return seconds

# Usage showing dual behavior
client = APIClient("https://api.example.com")
print(client.endpoint)           # https://api.example.com/
print(client.endpoint("/users")) # https://api.example.com/users
print(client.timeout)            # 30
print(client.timeout(60))        # 60
```

The descriptor protocol makes this possible. When accessing `client.endpoint`, Python checks if the attribute has a `__get__` method. Finding one, it calls `endpoint.__get__(client, APIClient)` which returns the descriptor instance itself. The `__repr__` method handles property-like access (returning the default value), while `__call__` enables method-like invocation with arguments.

The type annotations preserve full type safety using `ParamSpec` to capture the exact function signature and `Generic[P, R]` to maintain parameter and return types. This ensures type checkers understand both the callable signature and return type.

While clever, this pattern confuses IDE autocomplete and static analysis tools that expect attributes to be either properties or methods, not both. Reserve it for internal APIs where the dual behavior provides clear benefits and is well-documented.
