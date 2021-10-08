[![Actions Status](https://github.com/lyz-code/pydo/workflows/Tests/badge.svg)](https://github.com/lyz-code/pydo/actions)
[![Actions Status](https://github.com/lyz-code/pydo/workflows/Build/badge.svg)](https://github.com/lyz-code/pydo/actions)
[![Coverage Status](https://coveralls.io/repos/github/lyz-code/pydo/badge.svg?branch=master)](https://coveralls.io/github/lyz-code/pydo?branch=master)

# Pydo

`pydo` is a free software command line task manager built in
[Python](https://en.wikipedia.org/wiki/Python_%28programming_language%29).

# Why another CLI Task Manager?

[Taskwarrior](https://taskwarrior.org/) has been the gold standard for CLI task
managers so far. However, It has the following inconveniences:

* It uses a plaintext file as data storage.
* It stores the data in a non standard way in different files.
* It's written in C, which I don't speak.
* It's development has come to [code maintenance
    only](https://github.com/GothenburgBitFactory/taskwarrior/graphs/code-frequency).
* There are many issues with how it handles
    [recurrence](https://taskwarrior.org/docs/design/recurrence.html).
* It doesn't have [friendly task
    identifiers](https://lyz-code.github.io/pydo/developing/sulids).
* There is no way of accessing the task time tracking from the python library.

And lacks the following features:

* Native Kanban or Scrum support.
* Task estimations.
* Easy report creation.
* Easy way to manage the split of a task in subtasks.
* Freezing of recurrent tasks.

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

Let's see `pydo` in action. We'll first add three tasks to our list.

```bash
$: pydo add Buy milk
  [+] Added task 0: Buy milk
$: pydo add Buy eggs
  [+] Added task 1: Buy eggs
$: pydo add Bake cake
  [+] Added task 2: Bake cake
```

Now let's see the list.

```bash
$: pydo list
     ╷
  ID │ Description
╺━━━━┿━━━━━━━━━━━━━╸
  0  │ Buy milk
  1  │ Buy eggs
  2  │ Bake cake
     ╵
```

Suppose we bought our ingredients and wish to mark the first two tasks as done.

```bash
$: pydo do 0 1
  [+] Closed task 0: Buy milk with state done
  [+] Closed task 1: Buy eggs with state done

$: pydo list
     ╷
  ID │ Description
╺━━━━┿━━━━━━━━━━━━━╸
  2  │ Bake cake
     ╵
```

Those are the first three features, the `add`, `list` and `done` commands, but
they represent all you need to know, to get started with `pydo`.

But there are hundreds of other features, so if you learn more, you can do more.
It's entirely up to you to choose how you use `pydo`. Stick to the
three commands above, or learn about sophisticated agile support, custom reports,
user defined metadata and more.

# Install

To install pydo, run:

```bash
pip install py-do
```

The installation method will create a new pydo database at
`~/.local/share/pydo/database.tinydb`.

`pydo` reads it's configuration from the yaml file located at
`~/.local/share/pydo/config.yaml`. The [default
template](https://github.com/lyz-code/pydo/blob/master/assets/config.yaml) is
provided at installation time.

# What's next?

Probably the most important next step is to start using `pydo`.
Capture your tasks, don't try to remember them. Review your task list to keep it
current. Consult your task list to guide your actions. Develop the habit.

It doesn't take long until you realize that you might want to change your
workflow. Perhaps you are missing due dates, and need more defined deadlines.
Perhaps you need to make greater use of tags to help you filter tasks
differently. You'll know if your workflow is not helping you as much as it
could.

This is when you might look closer at the
[docs](https://lyz-code.github.io/pydo) and the recommended Best Practices.

If you want to contribute to the project follow [this
guidelines](https://lyz-code.github.io/pydo/contributing).

Welcome to `pydo`.
