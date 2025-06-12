# HTML Comment Syntax in JavaScript

JavaScript supports HTML-style comments at the beginning of lines.
This is a legacy feature that can lead to surprising behavior in modern code.

E.g.:

```javascript
x
= 1
x
--> 0
```

Returns `1`, not `0` or a syntax error.

## The Explanation

At the beginning of a line, `-->` acts as a single-line comment in JavaScript. The code is actually parsed as:

```javascript
x = 1;
x;  // --> 0 (this is a comment!)
```

The last line evaluates to the value of `x`, which is `1`.

## Historical Context

This feature exists for historical reasons dating back to early web browsers.
Prior to NetScape Navigator 2, it was necessary to hide JavaScript from browsers that didn't support it:

```html
<script>
<!--
// JavaScript code here
alert("Hello from 1995!");
//-->
</script>
```

Browsers without JavaScript support would treat the entire script block as an HTML comment, while JavaScript-enabled browsers would execute the code.

## Modern Examples

### The Comment Forms

```javascript
// These are all valid comments at line start
--> This is a comment
--> console.log("This won't run")

// But this throws a syntax error (not at line start)
let x = 5; --> This fails
```

### Practical Gotchas

```javascript
// Accidental comment creation
function calculate() {
    let result = 10
    --> 5  // Meant to return -5, but it's a comment!
    return result  // Returns 10
}

// Debugging confusion
let counter = 0
counter++
--> counter should be 1 here
console.log(counter)  // Prints 1, comment doesn't affect it
```

### The Full Set of HTML Comments

JavaScript actually supports multiple HTML comment forms:

```javascript
<!-- This is also a valid comment at line start
let a = 1
<!-- a = 2  // This line is commented out
console.log(a)  // Prints 1

// Combining both forms (rarely seen)
<!-- Start of comment
let b = 3
--> End of comment marker
console.log(b)  // Prints 3
```

## Browser vs Non-Browser Environments

This behavior is specifically required for web browsers but optional for other JavaScript environments:

```javascript
// In browsers (required to work)
--> This always works as a comment

// In Node.js (works, but not required by spec)
--> Support depends on the engine

// In embedded JavaScript engines
--> May not be supported at all
```

## Best Practices

1. **Never use HTML comments in JavaScript** - They're confusing and serve no modern purpose
2. **Use standard comments** - Stick to `//` and `/* */`
3. **Be aware when debugging** - If you see `-->` at line start, it's a comment
4. **Linting helps** - Most linters will warn about HTML comment usage

```javascript
// Good: Clear, standard JavaScript comments
// let x = 5

/* Also good: Multi-line comments
   for longer explanations */

// Bad: Confusing legacy syntax
--> let x = 5
<!-- let y = 10 -->
```

This kruft shows how JavaScript's commitment to backwards compatibility can create unexpected parsing behavior that persists decades after the original use case is obsolete.
