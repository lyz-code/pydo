---
title: Basic Usage
date: 20200301
author: Lyz
---

All you need to know to use `pydo` effectively are these four commands (`add`, `done`, `del`,
`list`).

# Add

To add a task run:

```bash
pydo add Improve the pydo manual
```

It is also possible to immediately add tags or projects when creating a task:

```bash
pydo add Improve the pydo manual pro:task_management +python
```

# List

To see the open tasks run:

```bash
pydo list
```

By default, `list` is the default command, so you can execute `pydo` alone.

# Done

If you've completed a task, run:

```bash
pydo done {{ task_id }}
```

Where `{{ task_id }}` is the task id that can be extracted from the `list`
report.

# Delete

If you no longer need a task, run:

```bash
pydo del {{ task_id }}
```

Where `{{ task_id }}` is the task id that can be extracted from the `list`
report.

If you are new to `pydo`, it is recommended that you stop here, go and start to
manage your task list for a while. We don't want you to be overwhelmed at a time
when you just need a way to organize and get things done.

When you are comfortable with basic `pydo` usage, there are many other features
you can learn about. While you are not expected to learn all of them, or even
find them useful, you might just find exactly what you need.
