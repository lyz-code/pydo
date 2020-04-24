---
title: Projects
date: 20200301
author: Lyz
---

Once you feel comfortable with the [basic usage](basic_usage.md) of `pydo`, you
may want to explore the different features it has to adapt it to your workflow.

As the number of tasks starts to increase, it's convenient to group them
together to help us with the priorization and visualization.

One way of doing so is using projects. A project is an optional category that
defines the purpose of a task therefore a task can *only have one project*. If
you feel that a task might have two projects or if you have hierarchical
problems with your tasks, you may want to use [tags](tags.md) instead.

For example, I'd use `clean` for cleaning tasks, or `time_management` for `pydo`
developing tasks.

To add a project to a task, use the `project` or `pro` keyword.

```bash
pydo add Improve pydo documentation pro:time_management
```

To see all the existing projects, use the `projects` report:

```
pydo projects

Name             Tasks  Description
--------       -------  ---------------------
None                 3  Tasks without project
time_management      1
```

To modify a task project use the `mod` command:

```bash
pydo mod {{ task_id }} pro:new_project
```
