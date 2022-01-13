# JavaScript `RegExp` Objects are Stateful

When a JavaScript `RegExp` is in global scope, calling a method on that same `RegExp` object begins the method's evaluation _from the index of its last match_.
Then, when no more matches are found, the evaluation index is automatically reset to `0`.

This can be both confusing (if one isn't aware of this behavior) and powerful (if one is aware). E.g. with this knowledge it's possible to begin evaluating a regex from any point in the string. Or, within a loop, it's possible to cease evaluation after a desired number of matches.

Proof of Concept
```js
const re = /a/g
const str = "ab"
re.test(str) // returns true
re.test(str) // this will fail! re.lastIndex === 1 so it starts searching at 'b'
re.test(str) // this will pass! since it failed, re.lastIndex is reset to 0
```

Managing Evaluation Within a Loop
```js
const re = /a/g
const str = "ab"
let match, results = []

while (match = re.exec(str))
  results.push(+match[1])
```

## Resources
- ["Why does Javascript's regex.exec() not always return the same value?"](https://stackoverflow.com/questions/11477415/why-does-javascripts-regex-exec-not-always-return-the-same-value)
