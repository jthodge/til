# Run `rbenv rehash` to Use Newly Installed Versions of Ruby or Gems

After installing a new gem or a new version of Ruby, sometimes you'll encounter an error where this new gem or Ruby version isn't found.

When that happens, run `rbenv rehash`. You'll then be able to run your new gem or Ruby version.

`rbenv rehash` installs shims for all executables known to rbenv (i.e. anything found in `~/.rbenv/versions/*/bin/*`).
