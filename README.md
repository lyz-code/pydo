[![Actions
Status](https://github.com/lyz-code/pydo/workflows/Python%20package/badge.svg)](https://github.com/lyz-code/pydo/actions)

# Pydo

`pydo` is a free software command line task manager built with
[Python](https://en.wikipedia.org/wiki/Python_%28programming_language%29) and
[SQLAlchemy](https://en.wikipedia.org/wiki/SQLAlchemy).

`pydo` scales to fit your workflow. Use it as a simple app that captures tasks,
shows you the list, and removes tasks from that list. Leverage its capabilities
though, and it becomes a sophisticated data query tool that can help you stay
organized, and get through your work.

* [Documentation](https://lyz-code.github.io/pydo)
* [Issue tracker](https://github.com/lyz-code/pydo/issues)
* [Contributing](https://lyz-code.github.io/pydo/contributing)

# Why another CLI Task Manager?

[Taskwarrior](https://taskwarrior.org/) has been the gold standard for CLI task managers so far. However,
It has the following inconveniences:

* It uses a plaintext file as data storage.
* It stores the data in a non standard way in different files.
* It's written in C, which I don't speak.
* It's development has come to [code maintenance
  only](https://github.com/GothenburgBitFactory/taskwarrior/graphs/code-frequency).
* There are several issues with how it handles
  [recurrence](https://taskwarrior.org/docs/design/recurrence.html).
* It doesn't have [friendly task
    identifiers](https://lyz-code.github.io/pydo/developing/fulids).
* There is no way of accessing the task time tracking from the python library.

And lacks the following features:

* Native Kanban or Scrum support.
* Task estimations.
* Task criteria [validation](https://en.wikipedia.org/wiki/Software_verification_and_validation).
* Easy report creation.
* Easy way to manage the split of a task in subtasks.

Most of the above points can be addressed through the [Taskwarrior plugin
system](https://taskwarrior.org/docs/3rd-party.html) or
[udas](https://taskwarrior.org/docs/udas.html), but sometimes it's difficult to
access the data or as the database grows, the performance drops so quick that it
makes them unusable.

[tasklite](https://tasklite.org) is a promising project that tackles most of the
points above. But as it's written in
[Haskel](https://en.wikipedia.org/wiki/Haskell_%28programming_language%29),
I won't be able to add support for the features I need.

# A quick demonstration

Let's see `pydo` in action. We'll first add a few tasks to our list.

```bash
pydo add Buy milk
pydo add Buy eggs
pydo add Bake cake
```

Now let's see the list.

```bash
pydo list

ID    Title
----  ---------
d     Bake cake
s     Buy eggs
a     Buy milk
```

Suppose we bought our ingredients and wish to mark the first two tasks as done.

```
pydo a done
pydo s done
pydo list

ID    Title
----  ---------
d     Bake cake
```

Those are the first three features, the `add`, `list` and `done` commands, but
they represent all you really need to know, to get started with `pydo`.

But there are hundreds of other features, so if you learn more, you can do more.
It's entirely up to you to choose how you use `pydo`. Stick to the simple
three commands above, or learn about sophisticated agile support, custom reports,
user defined metadata and many more.

# Installation

To install pydo, simply:

```bash
pip3 install git+git://github.com/lyz-code/pydo
```

The installation method will create a new pydo database at:
```
~/.local/share/pydo/main.db
```

`pydo` configuration is done through the yaml file located at
`~/.local/share/pydo/config.yaml`. The [default
template](https://github.com/lyz-code/pydo/blob/master/assets/config.yaml) is
provided at installation time.

# What's next?

Probably the most important next step is to simply start using `pydo`.
Capture your tasks, don't try to remember them. Review your task list to keep it
current. Consult your task list to guide your actions. Develop the habit.

It doesn't take long until you realize that you might want to modify your
workflow. Perhaps you are missing due dates, and need more defined deadlines.
Perhaps you need to make greater use of tags to help you filter tasks
differently. You'll know if your workflow is not really helping you as much as
it could.

This is when you might look closer at the
[docs](https://lyz-code.github.io/pydo) and the recommended Best Practices.

If you want to contribute to the project follow [this
guidelines](https://lyz-code.github.io/pydo/contributing).

Welcome to `pydo`.
