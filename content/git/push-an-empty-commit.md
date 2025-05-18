# Push an Empty Commit

At one point or another, you'll need to push a commit for the express purpose of testing whether or not something in CI is working properly.

The `--allow-empty` flag lets you push a "blank" commit and is perfect for this!

e.g. `git commit --allow-empty -m "Testing CI"`
