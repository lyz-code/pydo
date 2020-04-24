---
title: Tags
date: 20200301
author: Lyz
---

Tags are the other way of clustering your tasks, unlike [projects](projects.md),
a task can have several tags. So adding tags is the way to register that several
tags share an attribute. For example, I'd use `python` for tasks related to
developing programs with that language, or if you don't use `willpower`, `light`
could be used to gather easily done tasks.

To add a tag to a task, we use the `+tag` keyword.

```bash
pydo add Fix pydo install process +python
```

To see all the existing tags, use the `tags` report:

```
pydo tags

Name      Tasks  Description
------  -------  -------------
python        1
```

To add a tag to an existing task or to remove one, use the `mod` command.

```bash
pydo mod {{ task_id }} +new_tag
pydo mod {{ task_id }} -existing_tag
```
