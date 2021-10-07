---
title: Areas
date: 20200301
author: Lyz
---

Once you feel comfortable with the [basic usage](basic_usage.md) of `pydo`, you
may want to explore the different features it has to adapt it to your workflow.

As the number of tasks starts to increase, it's convenient to group them
together to help us with the prioritization and visualization.

One way of doing so is using areas. An area is an optional category that
defines the purpose of a task, so a task can *only have one area*. If
you feel that a task might need two areas or if you have hierarchical
problems with your tasks, you may want to use [tags](tags.md) instead.

For example, you can use `clean` for cleaning tasks, or `task_management` for `pydo`
developing tasks.

To add a area to a task, use the `area` or `ar` keywords.

```bash
pydo add Improve pydo documentation ar:task_management
```

To see all the existing areas, use the `areas` report:

```code
$: pydo areas
                  ╷
  Name            │ Open Tasks
╺━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━╸
  None            │ 2
  task_management │ 1
                  ╵
```

To change a task area use the `mod` command:

```bash
pydo mod {{ task_filter }} ar:new_area
```
