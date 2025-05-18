# Always Enclose Variable Names in Double Quotes

When referencing a variable in bash, always err on enclosing the variable name in double quotes.

Enclosing the variable name in double quotes prevents bash from reinterpreting all special characters within the quoted variable name string.
Notable exceptions that _will_ be reinterpreted are:
- `$`
- `\`` (backtick)
- `\` (escape character)

_N.B. it's important to keep `$` as a special character within double quotes, because doing so permits referencing a quoted variable i.e. replacing the variable with its value._

Enclosing a variable name within double quotes also prevents word splitting. Because, a reference or argument enclosed in double quotes presents itself as a single word, even if it contains whitespace separators.
