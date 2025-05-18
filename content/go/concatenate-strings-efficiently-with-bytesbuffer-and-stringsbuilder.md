# Concatenate Strings Efficiently with `bytes.Buffer` and `strings.Builder`

Concatenating strings with `+` or `+=` is fine for a small number of strings.

```go
str := "Taylor"
str = str + " Hodge"
```

```go
func join(strs ...string) string {
  var ret string
  for _, str := range strs {
    ret += str
  }
  return ret
}
```

But this becomes inefficient when concatenating a large number of strings, because strings in Go are immutable. So, when we want to update a string in any way, we need to create an entirely new string in memory.

It's more efficient to either:

1. Use `bytes.Buffer` and then convert the result to a string once everything has been concatenated, or
2. Use `strings.Builder`.

### 1. `bytes.Buffer`

```go
package main

import (
  "bytes"
  "fmt"
)

func main() {
  var b bytes.Buffer

  for i := 0; i < 1000; i++ {
    b.WriteString(returnString())
  }

  fmt.Println(b.String())
}

func returnString() string {
  return "a-sample-string-that-returns-"
}
```

### 2. `strings.Builder`

```go
func join(strs ...string) string {
  var sb strings.Builder
  for _, str =: range strs {
    sb.WriteString(str)
  }
  return sb.String()
}
```
