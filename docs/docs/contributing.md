---
title: Contributing
date: 20200424
author: Lyz
---

So you've started using `pydo` and want to show your gratitude to the project,
depending on your programming skills there are different ways to do so.

# I don't know how to program

There are several ways you can contribute:

* [Open an issue](https://github.com/lyz-code/pydo/issues/new) if you encounter
    any bug or to let us know if you want a new feature to be implemented.
* Spread the word about the program.
* Review the [documentation](https://lyz-code.github.io/pydo) and try to improve
    it.

# I know how to program in Python

If you have some python knowledge there are some additional ways to contribute.
We've ordered the [issues](https://github.com/lyz-code/pydo/issues) in
[milestones](https://github.com/lyz-code/pydo/milestones), check the issues in
the smaller one, as it's where we'll be spending most of our efforts. Try the
[good first
issues](https://github.com/lyz-code/pydo/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22),
as they are expected to be easier to get into the project.

We develop the program with
[TDD](https://en.wikipedia.org/wiki/Test-driven_development), so we expect any
contribution to have it's associated tests. We also try to maintain an updated
[documentation](https://lyz-code.github.io/pydo) of the project, so think if
your contribution needs to update it.

The [database schema](database_schema.md) is defined with
[SQLAlchemy](https://lyz-code.github.io/blue-book/coding/python/sqlalchemy/)
objects and maintained with
[Alembic](https://lyz-code.github.io/blue-book/coding/python/alembic/).

To generate the testing data we use
[FactoryBoy](https://lyz-code.github.io/blue-book/coding/python/factoryboy/)
with [Faker](https://lyz-code.github.io/blue-book/coding/python/faker/).

We know that the expected code quality is above average. Therefore it might
be changeling to get the initial grasp of the project structure, know how to make the
tests, update the documentation or use all the project technology stack. but please
don't let this fact discourage you from contributing:

* If you want to develop a new feature, explain how you'd like to do it in the related issue.
* If you don't know how to test your code, do the pull request without the tests
    and we'll try to do them for you.

Finally, to ensure a quicker pull request resolution, remember to *[Allow edits from
maintainers](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/allowing-changes-to-a-pull-request-branch-created-from-a-fork)*.

Check [Developing pydo](developing/developing.md) to get better insights of the
internals of the program.
