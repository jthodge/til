# Choose Folders to Ignore During Search

When searching in VS Code, fuzzy matching operates over all files within the current project. This will include a great deal of files from build, package, and testing directories.

You can remove these unwanted directories from the file explorer and serach by modifying the `search.exlude` setting. E.g.

```
{
    // ...
    "search.exclude": {
        "**/.git": true,
        "**/node_modules": true,
        "**/tmp": true,
        "**/coverage": true
    },
    // ...
}
```
