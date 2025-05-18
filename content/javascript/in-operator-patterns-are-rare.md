# `in` Operator Patterns are Rare

It's rare (in my experience) to see the `in` operator used in JS — or at least much less common than in other languages. Normally we'll see something along the lines of:
```js
typeof window !== "undefined"
```

vs.

```js
"window" in globalThis
```

I've learned that this is because they're not equivalent, and that using the latter pattern can lead to unanticipated results in vanilla JS, particularly when `undefined` is involved:

```js
a = {b: undefined}
"b" in a // returns True
typeof a.b !== "undefined" // returns False
```

But! It's possible to begin leveraging `in` more safely in TypeScript with [type guards `in` operator narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#the-in-operator-narrowing).
