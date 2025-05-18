# Basic Node Test Runner

Node hasn't and doesn't ship with its own basic test runner.

Go and Rust have each set great conventions by shipping with [`go test` / `go test -bench`](https://pkg.go.dev/testing) and [`cargo test`](https://doc.rust-lang.org/cargo/commands/cargo-test.html), respectively. But, it should be possible to make that ease available when working with Node!

So, it seems possible to get quite a bit of value from a basic test runner like this module:
```js
import assert from 'assert';

const tests = []

export function test(msg, fn) {
  tests.push([msg, fn])
}

process.nextTick(async function run() {
  for (const [msg, fn] of tests) {
    try {
      await fn(assert);
      console.log(`pass - ${msg}`)
    } catch (error) {
      console.error(`fail - ${msg}`)
      process.exitCode = 1;
    }
  }
})
```
(It could also be ran inline, I suppose.)
