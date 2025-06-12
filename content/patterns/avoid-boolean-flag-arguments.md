# Avoid Boolean Flag Arguments

Boolean parameters that control function behavior make code:
- less readable
- harder to maintain

Instead of flag arguments, use explicit methods or enums to make code:
- self-documenting
- more extensible

## The Problem with Boolean Flags

Boolean flags create ambiguous function calls that require readers to understand the paramete's implicit meaning:

```python
# What does False mean here?
send_email(user, "Welcome!", False)
process_payment(order, True)
generate_report(data, False, True)

# These calls are unclear without documentation
book_ticket(passenger, False)  # premium? refundable? priority?
authenticate_user(credentials, True)  # remember? admin? force?
```

## Better Alternatives

### 1. Separate Methods with Clear Names

Replace boolean flags with explicit method names:

```python
# Instead of: send_email(user, message, is_html)

def send_text_email(user, message):
    """Send a plain text email."""
    return _send_email(user, message, format="text")

def send_html_email(user, message):
    """Send an HTML formatted email."""
    return _send_email(user, message, format="html")

# Instead of: book_ticket(passenger, is_premium)
def book_regular_ticket(passenger):
    return _book_ticket(passenger, tier="regular")

def book_premium_ticket(passenger):
    return _book_ticket(passenger, tier="premium")
```

### 2. Use Enums for Multiple Options

When functions might expand beyond binary choices, use enums:

```python
from enum import Enum

class OutputFormat(Enum):
    TEXT = "text"
    JSON = "json"
    XML = "xml"
    HTML = "html"

class BookingTier(Enum):
    ECONOMY = "economy"
    PREMIUM = "premium"
    BUSINESS = "business"

# Clear, extensible function calls
def generate_report(data, format: OutputFormat):
    if format == OutputFormat.JSON:
        return json.dumps(data)
    elif format == OutputFormat.XML:
        return convert_to_xml(data)
    # ... handle other formats

# Usage is self-documenting
report = generate_report(sales_data, OutputFormat.JSON)
ticket = book_ticket(passenger, BookingTier.PREMIUM)
```

### 3. Configuration Objects for Complex Cases

For functions with multiple configuration options:

```python
from dataclasses import dataclass

@dataclass
class EmailConfig:
    format: str = "text"
    priority: str = "normal"
    track_opens: bool = False
    retry_count: int = 3

@dataclass
class ReportConfig:
    include_charts: bool = True
    compress_output: bool = False
    format: OutputFormat = OutputFormat.JSON
    max_rows: int = 10000

def send_email(recipient, message, config: EmailConfig = None):
    config = config or EmailConfig()
    # Implementation uses clear configuration

def generate_report(data, config: ReportConfig = None):
    config = config or ReportConfig()
    # Clear, extensible configuration

# Usage shows intent clearly

email_config = EmailConfig(format="html", priority="high")
send_email(user, welcome_message, email_config)

report_config = ReportConfig(format=OutputFormat.PDF, compress_output=True)
generate_report(quarterly_data, report_config)
```

## When Boolean Parameters Are Acceptable

Some cases where boolean parameters remain appropriate:

### 1. UI Control Values

When directly passing user interface state:

```python
def set_feature_enabled(feature_name: str, enabled: bool):
    """Toggle feature based on UI checkbox state."""
    features[feature_name] = enabled

# Checkbox value maps directly to boolean
set_feature_enabled("dark_mode", dark_mode_checkbox.checked)
```

### 2. Clear Binary States

When the boolean represents a true binary condition:

```python
def validate_user_input(data: str, strict: bool = False):
    """Validate input with optional strict mode."""
    # 'strict' clearly means "apply stricter validation rules"
    pass

def retry_operation(operation, ignore_errors: bool = False):
    """Retry operation with optional error handling."""
    # 'ignore_errors' has clear boolean meaning
    pass
```

### 3. Explicit Boolean Methods

When the method name includes the boolean concept:

```python
class Database:
    def set_auto_commit(self, enabled: bool):
        """Enable or disable auto-commit mode."""
        self.auto_commit = enabled
    
    def enable_auto_commit(self):
        """Enable auto-commit mode."""
        self.set_auto_commit(True)
    
    def disable_auto_commit(self):
        """Disable auto-commit mode."""
        self.set_auto_commit(False)
```

## Refactoring Existing Code

Transform flag arguments systematically:

```python
# Before: Multiple boolean flags
def process_data(data, validate=True, transform=False, cache=True):
    if validate:
        data = validate_data(data)
    if transform:
        data = transform_data(data)
    if cache:
        cache_data(data)
    return data

# After: Configuration object approach
@dataclass
class ProcessingOptions:
    validate: bool = True
    transform: bool = False
    cache_result: bool = True

def process_data(data, options: ProcessingOptions = None):
    options = options or ProcessingOptions()
    
    if options.validate:
        data = validate_data(data)
    if options.transform:
        data = transform_data(data)
    if options.cache_result:
        cache_data(data)
    return data

# Or: Pipeline approach with explicit methods
class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def with_validation(self):
        self.data = validate_data(self.data)
        return self
    
    def with_transformation(self):
        self.data = transform_data(self.data)
        return self
    
    def with_caching(self):
        cache_data(self.data)
        return self
    
    def process(self):
        return self.data

# Clear, composable usage
result = (DataProcessor(raw_data)
          .with_validation()
          .with_transformation()
          .with_caching()
          .process())
```

## Key Principles

1. **Readability first** - Code should be self-documenting
2. **Future extensibility** - Enums and objects handle growth better than booleans
3. **Reduce cognitive load** - Explicit names eliminate guesswork
4. **Consider the caller** - API design should prioritize the user experience

Boolean flags often seem convenient initially but create maintenance debt as systems evolve. Investing in explicit, extensible interfaces pays dividends in code clarity and maintainability.
