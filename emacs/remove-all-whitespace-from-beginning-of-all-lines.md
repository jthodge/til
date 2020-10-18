# Remove All Whitespace from Beginning of All Lines

1. `g g` to head to the top of your buffer.
2. `C-M-%` to use `query-replace-regexp`.
3. Input `^\s-+` as your regex value and press `RET`.
4. Press `RET` again to leave the replacement string empty.
5. You'll be prompted by `query-replace-regexp` in the minibuffer. Press `!` to perform all string replacements at once.

## Regex(planation):

- Caret `^`: beginning of line
- `\s-`: any character designated as "space" by the current mode's syntax table.
- `+`: >= 1 contiguous matches.
