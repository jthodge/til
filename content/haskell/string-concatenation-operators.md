# String Concatenation Operators

E.g. the following two functions:

## `++`

```haskell
wrapHtml content = "<html><body>" ++ content ++ "</body></html>"
```

## `<>`

```haskell
wrapHtml content = "<html><body>" <> content <> "</body></html>"
```

## Operator Comparison

### Operator

`++` is the traditional list concatenation operator in Haskell, while `<>` is the more general "mappend" operator from the `Semigroup` typeclass.

### Type flexibility

`++` works only with lists (including strings, which are lists of characters), while `<>` can work with any type that implements the `Semigroup` typeclass, including `String`, `Text`, `ByteString` (and others).

### Performance

For strings, `<>` can be more efficient, especially when working with `Text` or `ByteString` types, as it allows for optimized concatenation.

### Readability

Some developers find `<>` more readable, especially when dealing with multiple concatenations.

In practice, for simple string concatenation like the examples above, both will work identically with `String` types. However, using `<>` more extensible and improves flexibility, because the underlying string representation (e.g., to `Text`) can be changed in the future.
