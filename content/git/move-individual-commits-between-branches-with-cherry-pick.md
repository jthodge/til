# Move Individual Commits Between Branches with `cherry-pick`

Suppose Branch A contains individual commits X and Y, and that X and Y need to be on Branch B as well, in their original order. We can use `cherry-pick` to migrate those specific commits to our newly desired branch.

> Note: `cherry-pick` operations on a receiving branch need to be performed in the same chronological order as they appear on their originating branch.

```git
git checkout branch-b
git cherry-pick x
git cherry-pick y
```
