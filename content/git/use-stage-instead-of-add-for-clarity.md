# Use `stage` Instead of `add` for Clarity

`git stage` is a synonym for `git add`, but `stage`  more effectively expresses intent.
It aligns with Git's terminology used elsewhere and makes workflows more intuitive.
We should all probably move towards replacing `add` with `stage`.

## The Commands Are Identical

```bash
# These do the same thing
git add file.txt
git stage file.txt

# Both stage files for the next commit
git add .
git stage .
```

## Language Consistency

Git's own output uses staging terminology...

```bash
git status
# Changes to be committed:
#   (use "git restore --staged <file>..." to unstage)
#
# Changes not staged for commit:
#   (use "git add <file>..." to update what will be committed)
```

But still recommends `add`...

## Practical Examples

```bash
# Preparing files for commit
git stage README.md
git stage src/utils.py
git commit -m "Update documentation and utilities"

# Sselective staging workflow
git stage --patch config.json  # Stage specific changes
git stage tests/            # Stage entire directory
git status                  # Review what's staged
git commit -m "Add test configuration"
```

## Workflow Clarity

The staging metaphor is more intuitive:

```bash
# Stage management commands
git stage file.txt          # Put file on stage
git restore --staged file.txt  # Remove from stage
git stash --staged          # Stash only staged changes

# vs. the confusing "add" metaphor
git add file.txt            # "Add" file (but it's modification?)
git add file.txt            # "Add" same file again?
```

## Advanced Staging Operations

```bash
# Interactive staging
git stage -i               # Interactive mode
git stage -p               # Patch mode (stage chunks)

# Stage by file type
git stage "*.py"          # Stage all Python files
git stage --update        # Stage tracked files only

# Conditional staging
find . -name "*.js" -newer last_release.txt | xargs git stage
```

## Team Communication

Using `stage` can improve  shared understanding:

```bash
# Clear commit workflow documentation
# 1. Make changes
# 2. Stage files: git stage <files>
# 3. Review: git status
# 4. Commit: git commit

# vs unclear "add" workflow
# 2. Add files: git add <files>  # Add to what?
```

