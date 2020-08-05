# Suppress File Names When Grepping Across Multiple Files

Use the `-h` flag to suppress file names when searching over multiple files with `grep`.

```terminal
➜ grep 'esModule' *.json
tsconfig.json:    "esModuleInterop": true,
```

```terminal
➜ grep -h 'esModule' *.json
    "esModuleInterop": true,
```
