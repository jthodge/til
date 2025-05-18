# Set Default for Initial Branch Name

As of `git` [version 2.28.0](https://lore.kernel.org/git/xmqq5za8hpir.fsf@gitster.c.googlers.com/), there's a new `init` feature to "_allow setting the default for the initial branch name via the config._"

## Change Initial Branch Name for New Repos

When creating a new git repo with `git init`, git "creates a default branch" so that you can begin committing and staging changes. Historically, this default branch has been called "master."

Should you find this name distasteful and lacking in explicit clarity, it's been possible to change the name of the branch:

```terminal
git branch --move master my-new-trunk
```

Now, as of 2.28.0, `git` can handle this change!

To set the default branch name for all new repos your git user creates to `main`, you can now edit git's global configuration:

```terminal
git config --global init.defaultBranch main
```

Then, any new repo you initialize will use the default branch name `main`.

## Bonus: Updating Existing Repos

The global configuration setting above only affects new repos created after your `.gitconfig` has been updated. But—updating the default branch name for an existing repo is easy!

In your existing git repo, rename the branch:

```terminal
git branch --move master main
```

Push your renamed branch (with the assumption that the remote repo is named `origin`):

```terminal
git push origin main
```

And finally, delete the remote's original branch:

```terminal
git push origin --delete master
```

👆*NB. Remote repo hosts like GitHub and GitLab don't allow deleting the `master` branch from the local repo. You'll receive an error*:

```terminal
til on  main
➜ git push origin --delete master
To https://github.com/jthodge/til.git
 ! [remote rejected] master (refusing to delete the current branch: refs/heads/master)
error: failed to push some refs to 'https://github.com/jthodge/til.git'
```

_To delete the `master` branch for each of these services, it's required to use their web applications._
