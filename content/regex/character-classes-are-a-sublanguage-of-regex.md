# Character Classes Are a Sub-language of Regex

Regular expression character classes are their own micro-universe within the regex syntax.

The usual rules for regex we normally find outside of character classes don't apply.

Rules inside character classes are different from the rest of the regex, and treating them the same can lead to errors. For instance:

- The dot `.` loses its "match any character" meaning inside a character class.
- The caret `^` means "not" at the start of a character class, but matches a literal caret elsewhere.
- The hyphen `-` defines a range between two characters, but only if it's not at the start or end of the class.

Understanding these differences can help avoid common regex mistakes and write more accurate patterns.

## Basic Character Class

A character class is defined by square brackets `[ ]`. It matches any single character from the set of characters inside the brackets. E.g.

This pattern...

```regex
[aeiou]
```

...matches any single vowel.

## Negated Character Class

Adding a caret `^` at the start of a character class negates it, meaning it matches any character that is not in the set. E.g.

This pattern...

```regex
[^0-9]
```

...matches any single character that is not a digit.

## Ranges

Inside a character class, you can define ranges using a hyphen `-`. E.g.

This pattern...

```regex
[a-z]
```

...matches any single lowercase letter, from a to z.

## Special Characters

Many special characters that have meaning outside of character classes lose their special meaning inside them.
E.g.

This pattern...

```regex
[.]
```

...matches a literal period — _NOT_ the "match any character" that `.` means outside of character classes.

## Meta-characters within Character Classes

Some meta-characters retain special meaning even within character classes:

- `^`: negation (if it's the first character in the class)
- `-`: range (if it's not the first or last character in the class)
- `\`: literal

E.g. this pattern...

```regex
[^-]
```

...matches any single character that is not a hyphen.

## Predefined Character Classes

Some shorthand character classes exist, which are equivalent to longer character class expressions:

- `\d` is equivalent to `[0-9]`
- `\w` is equivalent to `[a-zA-Z0-9_]`
- `\s` is equivalent to `[ \t\r\n\f]`
