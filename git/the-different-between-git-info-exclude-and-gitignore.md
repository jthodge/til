# The Differences Between `.git/info/exclude` and `.gitignore`

On `init`, Git will create `.git/info/exclude`. This file communicates to Git's user-facing commands (e.g. `add`, `rm`, `status`, etc.) which files should be excluded, and not checked in as changes.

Normally, we'll manually create `/.gitignore` to specify files to ignore and exclude from changes. Other than `.git/info/exclude` being created automatically and `.gitignore` being created manually, there is a key difference between `.git/info/exclude` and `.gitignore`:

- `.gitignore` is included as a part of your source tree. `.gitignore`'s contents is stored in commits, and is distributed to those you collaborate with inside the repo.
- The `exclude` file _is not_ a part of the commit database, and it remains local to your machine.

So, we use `.gitignore` for shared patterns and files we want to exclude from our changes, and `exclude` for patterns and files that only apply to our local computers.
