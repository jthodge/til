# JSON Encoding and Decoding I/O Conversions

When encoding/decoding JSON, Python's builtin `json` module adheres to the following conversion rules:

| JSON          | Python  |
|---------------|---------|
| object        | dict    |
| array         | list    |
| string        | str     |
| number (int)  | int     |
| number (real) | float   |
| true          | True    |
| false         | False   |
| null          | None    |
