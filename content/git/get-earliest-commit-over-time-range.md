# Get Earliest Commit Over Time Range

```bash
git log  --since="24 hours ago" --until="now" --reverse --pretty=format:"%h" | head -1
```
