---
title: Priority
date: 20200301
author: Lyz
---

The `priority` optional task attribute registers how urgent a task is.

The parameter allows any integer, but I use from `0` (really low priority) to
`5` (really high priority), being `3` the standard medium priority.

To set the priority of a task use the `pri` or `priority` keyword:

```bash
pydo add Task with highest priority pri:5
```

Right now we only use the
`priority` for filtering or visualization purposes. But we plan to support
reports that sort the tasks by their
[urgency](https://github.com/lyz-code/pydo/issues/17). The `priority` will be
one of the main factors to take into account.
