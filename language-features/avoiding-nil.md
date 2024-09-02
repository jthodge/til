# Avoiding Nil

Many languages and frameworks (Ruby and Rails in particular) tend to be `nil` happy.
They fire off `nil`s every which way, which can be problematic when those `nil`s percolate throughout your system and end up generating errors far, far away from their origin.

E.g.

```ruby
class Person
  attr_reader :name

  def initialize(name)
    @name = name
  end
          
  def self.find(id)
    people = {1 => new('alice'), 2 => new('bob')}
    # people[id]
    # L18 returns `nil` in Ruby, and Rails throws an exception in Rails when `id` does not exist (when using the base `find` method)
    # We can fix this with:
    prople.fetch(id)
    # which will return:
    # foo.rb:10:in `fetch': key not found (IndexError)
    # from foo.rb:10:in `find'
    # from foo.rb:16:in `create'
    # from foo.rb:30
  end
end

class SubscriptionsController
  def create(person_id)
    person = Person.find(person_id)
    Subscription.create_for_person(person)
  end
end

class Subscription
  def self.create_for_person(person)
    create!(:person => person, :person_name => person.name)
  end
  
  def self.create!(*args)
  end
end

SubscriptionsController.new.create(3)
# Will return:
# foo.rb:23: in `create_for_person': undefined method `name` for `nil:NilClass (NoMethodError)`"
# from foo.rb:17:in `create`
# from foo.rb:30
```

Checking out the trace:

1. L30 is where we kick off our call
2. L17 is within our controller
3. L23 is in our `Subription` model, where the model is getting a `nil` from L16, passing that `nil` to the `Subscription`, and then the `Subscription` is accessing an attribute (`name`) on the `nil` that (understandably) does not exist. This is throwing the exception.

But!

The line that initially introduced the `nil` (L18: `people[id]`) is not in our trace. And that's the root of the problem.
There can be _so many_ lines of stack context between introducing that `nil` and attempting to access an attribute on it. (Heaven forbid you've got ActiveRecord in there too...good luck figuring out what ActiveRecord is doing in there.)

**Fundamental problem: the introduction of the `nil` is not local to the use of the `nil` in the returned trace.**

Our change to using `fetch()` is illustrative of an important takeaway:
If you're going to encounter this type of bug in production (and you will) then **you want the trace to return the line that introduced the `nil`, _not_ the line that happened to use it.**

You can avoid introducing `nil`s by using your language or library more carefully, and in ways that prevent `nil`s from existing in the first place.
