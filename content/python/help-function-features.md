# Python's `help()` Function Features

Python's built-in `help()`  provides offline documentation for functions, modules, objects, keywords, and symbols—perfect for quick exploration without leaving the REPL.

## Basic Usage

### Getting Help on Objects

```python
# Functions
help(print)
help(len)
help(sorted)

# Modules
import math
help(math)
help(math.sqrt)

# Classes and methods
help(list)
help(list.append)

# Your own objects
class Customer:
    """A customer with a name and balance."""
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance

    def deposit(self, amount):
        """Add funds to the customer's balance."""
        self.balance += amount

help(Customer)
help(Customer.deposit)
```

## String-Based Lookups

You can pass strings to access help in different ways:

```python
# Module.function notation
help("math.prod")
help("itertools.chain")

# Get help on symbols (operators)
help("**")   # Exponentiation
help("//")   # Floor division
help("@")    # Matrix multiplication / decorator
help("...")  # Ellipsis

# Keywords
help("if")
help("yield")
help("lambda")
help("nonlocal")

# Special topics
help("TRUTHVALUE")
help("BASICMETHODS")
help("SEQUENCEMETHODS")
```

## Interactive Help Mode

Launch an interactive help session:

```python
# Enter interactive help
help()

# Then type:
# modules     - list all available modules
# keywords    - list Python keywords
# symbols     - list operators and punctuation
# topics      - list special topics
# quit        - exit help

# Or explore specific items:
# >>> modules math
# >>> keywords for
```

## Practical Examples

### Exploring Unknown Modules

```python
import json

# What's in this module?
help(json)

# How does dumps work?
help(json.dumps)

# What about that cls parameter?
help(json.JSONEncoder)
```

### Understanding Error Messages

```python
# Got a TypeError about 'NoneType'?
help(None)
help(type(None))

# Confused about a built-in exception?
help(ValueError)
help(KeyError)
```

### Quick Language Reference

```python
# How do f-strings work?
help("FORMATTING")

# What's the deal with slicing?
help(slice)

# Remind me about list comprehensions
help("LISTCOMPREHENSIONS")
```

## Advanced Tips

### Custom Help for Your Code

```python
def calculate_discount(price, discount_percent):
    """
    Calculate the final price after applying a discount.

    Args:
        price (float): Original price
        discount_percent (float): Discount as a percentage (0-100)

    Returns:
        float: Final price after discount

    Example:
        >>> calculate_discount(100, 20)
        80.0
    """
    return price * (1 - discount_percent / 100)

# Now help() shows your documentation
help(calculate_discount)
```

### Combining with Other Introspection Tools

```python
import inspect

# Get source code
print(inspect.getsource(calculate_discount))

# Get signature
print(inspect.signature(json.dumps))

# List all attributes
print(dir(math))

# Then get help on specific ones
help(math.tau)  # Found via dir()
```

### Finding Hidden Gems

```python
# Discover all available topics
help("topics")

# Some interesting ones:
help("DEBUGGING")
help("NAMESPACES")
help("PACKAGES")
help("CONTEXTMANAGERS")
```

## Best Practices

1. **Use help() during development** - Quick way to check function signatures
2. **Document your code** - Your docstrings will appear in help()
3. **Explore new modules** - Use help() before reading online docs
4. **Learn Python features** - Keywords and topics provide language insights
5. **Check parameter details** - Especially useful for understanding optional arguments

```python
# Example: What are all the parameters for open()?
help(open)

# Quick check: How does enumerate work again?
help(enumerate)

# Debugging: What methods does this object have?
data = {'a': 1}
help(type(data))
```

