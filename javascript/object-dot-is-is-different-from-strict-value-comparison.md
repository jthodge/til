# `Object.is` is Different From `===` and `!==`

The `SameValue` algorithm provided by `Object.is` differs from the `IsStrictlyEqual` algorithm provided by strict value-comparison operators by:
- treating all `NaN` values as equivalent, and
- by differentiating `+0` from `0-`

```js
Object.is(+0, -0)
// False
```

vs.

```js
+0 === -0
// True
```

Strange, no?

But it does seem like this difference could be useful for some interesting custom negative indexing:
```js
Object.is(0, -0) !== (0 === -0)
// True
```

## Resources
- [Ecma Standard `SameValue` Spec](https://tc39.es/ecma262/#sec-samevalue)
- [MDN Equality comparisons and sameness](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Equality_comparisons_and_sameness)
