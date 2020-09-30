---
title: Basic Usage
date: 20200301
author: Lyz
---

All you need to know to use `pydo` effectively are these five commands (`add`,
`do`, `rm`, `mod` and `open`).

# add

To add a task run:

```bash
pydo add Improve the pydo manual
```

It is also possible to immediately add tags or projects when creating a task:

```bash
pydo add Improve the pydo manual pro:task_management +python
```

# open

To see the open tasks run:

```bash
pydo open
```

By default, `open` is the default command, so you can execute `pydo` alone.

# do

If you've completed a task, run:

```bash
pydo do {{ task_filter }}
```

Where `{{ task_filter }}`  can be a task id extracted from the `open` report or
a task expression like `pro:task_management +python`.

# rm

If you no longer need a task, run:

```bash
pydo del {{ task_filter }}
```

# mod

To modify existent tasks use the following syntax.

```bash
pydo mod '{{ task_filter }}' {{ task_attributes }}
```

Notice that the `task_filter` needs to be quoted if the filter contains more
than one word.

For example, to change the description of the first task, we'd do:

```bash
pydo a Improve the pydo documentation
```

If you are new to `pydo`, it is recommended that you stop here, go and start to
manage your task list for a while. We don't want you to be overwhelmed at a time
when you just need a way to organize and get things done.

When you are comfortable with basic `pydo` usage, there are many other features
you can learn about. While you are not expected to learn all of them, or even
find them useful, you might just find exactly what you need.
