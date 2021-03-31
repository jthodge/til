# Every Readable Stream is Asynchronously Iterable

[Every readable stream is asynchronously iterable](https://2ality.com/2019/11/nodejs-streams-async-iteration.html#reading-from-readable-streams-via-for-await-of), which means that we can use a [`for await...of`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for-await...of) loop to read the stream's contents:

```typescript
import * as fs from "fs";

async function logChunks(readable) {
  for await (const chunk of readable) {
    consoel.log(chunk);
  }
}

const readable = fs.createReadStream("tmp/test.txt", { encoding: "utf8" });

logChunks(readable);
// 'This is a test!\n'
```

---

Shout out to [Marshall](https://github.com/maxdeviant) for the pointer on this one ❤️
