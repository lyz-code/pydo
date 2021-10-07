---
title: Tags
date: 20200301
author: Lyz
---

Tags are the other way of clustering your tasks, unlike [areas](areas.md),
a task can have many tags. So adding tags is the way to cluster tasks that
share an attribute. For example, you can use `python` for tasks related to
developing programs with that language, or if you don't use
[`willpower`](willpower.md), `light`
could be used to gather easily done tasks.

To add a tag to a task, we use the `+tag` keyword.

```bash
pydo add Fix pydo install process +python
```

To see all the existing tags, use the `tags` report:

```code
$: pydo tags
         ╷
  Name   │ Open Tasks
╺━━━━━━━━┿━━━━━━━━━━━━╸
  None   │ 4
  python │ 1
```

To add a tag to an existing task or to remove one, use the `mod` command.

```bash
pydo mod {{ task_filter }} +new_tag
pydo mod {{ task_filter }} -existing_tag
```
