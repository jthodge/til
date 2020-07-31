# Reset Bundle Gems

Restore a bundle's installed gems to their default state using `bundle pristine`.
After editing a bundle's gems, using `puts`, and other debuggers, `bundle pristine` will use the local `.gem` cache or the gem's repo, just like installing from scratch.
