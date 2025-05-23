# Format Mini-Language in f-strings

The Format Mini-Language is powerful. And often overlooked.
It affords precise control over how values are displayed, far beyond variable
interpolation.

The Format Mini-Language follows the pattern: `{value:format_spec}`.
`format_spec` can include alignment, padding, precision, type codes, etc.

## Common Format Specifiers

### Alignment and Padding

Control text alignment within a fixed width field:

```python
# Basic alignment
name = "Python"
print(f"|{name:<12}|")  # Left align
print(f"|{name:>12}|")  # Right align
print(f"|{name:^12}|")  # Center align

# Custom padding characters
print(f"{name:=^20}")   # Center with '='
print(f"{name:*>15}")   # Right align with '*'
```

Output:
```
|Python      |
|      Python|
|   Python   |
=======Python=======
*********Python
```

### Number Formatting

Format numbers with precision, thousands separators, and different bases:

```python
value = 1234567.89
small = 0.00456

# Decimal places
print(f"Fixed 2 decimals: {value:.2f}")
print(f"Fixed 4 decimals: {small:.4f}")

# Thousands separator
print(f"With commas: {value:,.2f}")

# Scientific notation
print(f"Scientific: {value:.2e}")
print(f"General format: {small:.2g}")

# Different bases
num = 255
print(f"Hex: {num:x}, {num:#x}, {num:#X}")
print(f"Binary: {num:b}, {num:#b}")
print(f"Octal: {num:o}, {num:#o}")
```

Output:
```
Fixed 2 decimals: 1234567.89
Fixed 4 decimals: 0.0046
With commas: 1,234,567.89
Scientific: 1.23e+06
General format: 0.0046
Hex: ff, 0xff, 0XFF
Binary: 11111111, 0b11111111
Octal: 377, 0o377
```

### Percentage and Sign Formatting

```python
ratio = 0.8765
change = -0.0234
positive = 42.5

# Percentage
print(f"Completion: {ratio:.1%}")
print(f"Precise: {ratio:.3%}")

# Sign handling
print(f"Always sign: {positive:+.1f}")
print(f"Space for positive: {positive: .1f}")
print(f"Negative: {change:+.2%}")
```

Output:
```
Completion: 87.7%
Precise: 87.650%
Always sign: +42.5
Space for positive:  42.5
Negative: -2.34%
```

### Zero Padding and Width

```python
# Zero padding for numbers
day = 5
month = 12
print(f"Date: {month:02d}/{day:02d}")

# Fixed width with zeros
order_id = 42
print(f"Order: {order_id:08d}")

# Combining with other formats
pi = 3.14159
print(f"Pi: {pi:08.3f}")
```

Output:
```
Date: 12/05
Order: 00000042
Pi: 003.142
```

### Debug Expressions

Supported in Python 3.8+

The `=` specifier shows both the expression and its value:

```python
x = 10
y = 20
name = "Alice"

print(f"{x + y=}")
print(f"{name.upper()=}")
print(f"{len(name)=}")
```

Output:
```
x + y=30
name.upper()='ALICE'
len(name)=5
```

### Datetime Formatting

Format datetime objects directly in f-strings:

```python
from datetime import datetime

now = datetime.now()

print(f"Full date: {now:%Y-%m-%d %H:%M:%S}")
print(f"Just date: {now:%B %d, %Y}")
print(f"Just time: {now:%I:%M %p}")
print(f"Weekday: {now:%A}")
print(f"ISO format: {now:%Y%m%dT%H%M%S}")
```

Output:
```
Full date: 2025-01-23 14:30:45
Just date: January 23, 2025
Just time: 02:30 PM
Weekday: Thursday
ISO format: 20250123T143045
```

## Advanced Combinations

You can combine multiple format specifiers for complex formatting:

```python
# Header with dynamic width
width = 60
title = "Processing Results"
print(f"{title:=^{width}}")

# Table-like output
items = [
    ("Dataset A", 0.9234, 1000000),
    ("Dataset B", 0.8765, 2500000),
    ("Dataset C", 0.9876, 750000)
]

print(f"{'Name':<15} {'Accuracy':>10} {'Samples':>12}")
print("-" * 39)
for name, acc, samples in items:
    print(f"{name:<15} {acc:>10.2%} {samples:>12,}")
```

Output:
```
=====================Processing Results=====================
Name             Accuracy      Samples
---------------------------------------
Dataset A          92.34%    1,000,000
Dataset B          87.65%    2,500,000
Dataset C          98.76%      750,000
```

## Format Specification Mini-Language

General form: `[[fill]align][sign][#][0][width][grouping_option][.precision][type]`

- **fill**: Any character to use for padding
- **align**: `<` (left), `>` (right), `^` (center), `=` (padding after sign)
- **sign**: `+` (always show), `-` (only negative), ` ` (space for positive)
- **#**: Alternate form (adds prefix for bases)
- **0**: Zero-padding
- **width**: Minimum field width
- **grouping_option**: `,` or `_` for thousands separator
- **precision**: Number of digits after decimal
- **type**: `s` (string), `d` (decimal), `f` (fixed-point), `e` (exponential), `%` (percentage), etc.

All of this makes f-strings suitable for everything from simple interpolation to
complex report formatting, all while maintaining readability and performance.
