# Move a Range of Commits Between Branches

Suppose Branch A contains a range of commits X...ZZ, and that X...ZZ need to be on Branch B as well, in their original order.

> Note: To migrate these commits to our desired branch, we first need to specify the commit _before_ the initial commit (i.e. X) since the range's initial value is non-inclusive.

```git
git checkout branch-b
git log # note the SHA of head, M)
git rebase --onto $SHA_OF_M $SHA_OF_COMMIT_BEFORE_X $SHA_OF_ZZ
git rebase HEAD branch-b
```
