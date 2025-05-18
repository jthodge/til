# Use Multiple `git commit` Message Flags to Create Multiline Commits

Turns out, `git commit` [accepts multiple](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt--mltmsggt) `-m` options:

```
If multiple -m options are given, their values are concatenated as separate paragraphs.
```

So, making a commit with this command:

`git commit -m "commit title" -m "commit description"`

Will result in this commit:

```
Author: Taylor Hodge
Date:   Sun Jul 12 19:18:21 2020 +0200

    commit title

    commit description

 test.txt | 0
 1 file changed, 0 insertions(+), 0 deletions(-)
```
