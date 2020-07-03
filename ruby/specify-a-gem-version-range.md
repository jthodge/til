# Specify a Gem Version Range

In your `Gemfile`, there are two methods of specifying a gem's version range.

1. Optimistic Version Constraint (`>=`)

This constraint will install the latest gem version, as long as it is greater than or equal to the version you specify. It's essentially saying "_all versions above this work with your software_."

E.g. `gem 'library', '>= 2.2.0'` will install the latest version of `library`—even if it's 7.1.2.

2. Pessimistic Version Constraint (`~>`)

This constraint will install the latest gem version up to the most recent dot-release. It's essentially saying "_only versions up to the most recent minor release with your software_."

The "twiddle-wakka" operator is a shortcut for combining the `>=` and `<` operators.

E.g. `gem 'rails', '~> 3.0.3'` will install the latest version of `rails` between `>= 3.0.3` and `< 3.1`.

E.g. `gem 'thin', '~> 1.1'` will install the latest version of `thin` between `>= 1.1` and `< 2.0`.
