# Metaclasses

## tl;dr

- Metaclasses are the classes of classes.
- Classes are objects; metaclasses manufacture them.
- The `type(name, bases, attrs)` call is the fundamental constructor.
- Custom metaclasses override `__new__`/`__init__` to rewrite the namespace, enforce policies, or register classes.
- Prefer simpler mechanisms unless class-level intervention is unavoidably required.

## Default Path

When Python executes a class block, it calls a metaclass to construct the
resulting class object.

If we don't do anything special or out of thfe ordinary, then that metaclass
is the built-in type.

```python
# Standard class statement
class Simple:                # under the hood: →  type.__new__(...)
    pass

# Produce the same effect with an explicit call
Simple2 = type("Simple2", (), {})
```

Both `Simple` and `Simple2` are produced by `type`. This demonstrates that class
definitions are syntactic sugar for `type(...)`.

## The Minimum Viable Custom Metaclass

```python
class Tag(type):
    """Attach an auto-incrementing `id` to each new class."""
    _next_id = 0

    def __new__(mcls, name, bases, ns):
        ns["id"] = mcls._next_id      # install attribute when class is built
        mcls._next_id += 1
        return super().__new__(mcls, name, bases, ns)

class Alpha(metaclass=Tag):
    pass

class Beta(metaclass=Tag):
    pass

print(Alpha.id, Beta.id)      # returns 0 1
```

Execution order:

When `Alpha`'s body finishes executing, Python:

1. calls `Tag.__new__`,
2. injects `id`,
3. returns the freshly-minted class object, and then
4. the interpreter continues.

Note: there's no instance creation involved.

## Decorators vs. Metaclasses

We can use decorators to accomplish the same "registry" idea without needing to
touch metaclasses:

```python
registry = []

def register(cls):
    registry.append(cls)
    return cls

@register
class Gamma:                  # simpler for many use-cases
    pass
```

So, the question is:
pWhen should we reach for metclasses?
And when should we use decorators?

"Metaclasses are deeper magic than 99% of users should ever worry about. If you wonder whether you need them,
you don't (the people who actually need them know with certainty that they need them, and don't need an
explanation about why)."
- Tim Peters

Heurisitic:
Only use metaclasses when you need to intercept or alter class creation itself.
E.g. a need to modify the namespace before a class existss.
In most cases, with very rare exception,  decorators, `__init_subclass__`, or
mix-ins are the best tool(s) for the job..
