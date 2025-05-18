# Use the `DEBUG` Trap to Step Through a Script

The `DEBUG` trap will run any preceding command before it executes each subsequent commands. E.g.

```bash
trap "echo Hello World" DEBUG
```

will run `echo Hello World` before moving on to any following commands.

This is really useful when you need to step through a bash script line-by-line. E.g.

`$ cat step-it-up-and-go.sh`

```bash
#!/bin/bash

trap '(read -p "[$BASH_SOURCE:$LINENO] $BASH_COMMAND?")' DEBUG

var=40
echo $((var+2))
```

`$ bash step-it-up-and-go.sh`

```bash
[step-it-up-and-go.sh:5] var=40?
[step-it-up-and-go.sh:6] echo $((var+2))?
42
```
