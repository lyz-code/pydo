Date: 2021-05-27

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Accepted

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
Older versions of `pydo` use fulid ids to define the entities as it's easy to
create the short ids from them in order to present them to the user through the
cli interface. To do it, at service level it creates the next id with the
`_create_next_id` function.

The current system adds a lot of complexity for the sake of identifying entities
through the minimum amount of keystrokes chosen from a set of keys defined by
the user.

Newer versions of the repository-orm library manages automatically id increments
if the `id_` field is of type `int`. This allows the addition of entities
without id, which will be very useful to create children task objects at model level
instead of service level.

I'm more and more convinced that the ideal everyday user interface is not a command line
program, but an REPL interface. The first one is meant only for bulk operations,
not for operations on one item. That means that being able to tell apart tasks
using short ids has loosing importance as this idea evolves.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->
Change the entities `id_` type from `str` to `Optional[int]`, so pydo can
delegate it's management to the repository.

When using the command line, we can show the ids as numbers, or optionally do
the translation from numbers to the user chosen keys. But we won't be as optimal
as before, because currently the short ids are defined by the subset of open
tasks, and we'll use all the tasks, so more keystrokes will be needed. But this
is acceptable as most of the times you'll use the REPL interface to interact
with individual tasks, and when bulk editing you'll use task filters instead of
the ids. We can even envision how to effectively do bulk edits through the REPL.

The REPL interface will not even show the ids, you'll move through the tasks by
vim movement keys or by fuzzy searching.

# Decision
<!-- What is the change that we're proposing and/or doing? -->

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
