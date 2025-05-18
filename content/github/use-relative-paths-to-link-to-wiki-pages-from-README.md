# Use Relative Paths to Link to Wiki Pages from README.md

You can create a link from a repo's README.md to a repo's Wiki using relative paths.

Because a repo's README.md is located here:

`https://github.com/$USERNAME/$REPO_NAME/blob/master/README.md`

And a repo's Wiki is located here:

`https://github.com/$USERNAME/$REPO_NAME/wiki`

You can crawl up two levels from README.md to the Wiki:

`[Article Title](../../wiki/article-title)`

_Note_: When cloning a repo that uses relative paths for links to repo Wikis like this, those relative links will break. However, cloning the Wiki as a separate repo to fix this. You can clone a repo's Wiki by appending `.wiki.git` to the repo name:

`git clone https://github.com/$USERNAME/$REPO_NAME.wiki.git`
