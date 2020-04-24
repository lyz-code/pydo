---
title: Willpower
date: 20200424
author: Lyz
---

The `willpower` optional task attribute registers how much energy the execution
of the task consumes. Understanding energy as physical or mental energy. For
example, solving a complex programming problem, doing long boring tasks or
running a marathon have high `willpower` value, meanwhile watering the plants,
going for a walk or to the cinema have a low value.

If your tasks have this property, it can help you determine the tasks to be done
during the sprint and in what order so as not to burn yourself out. Or to
analyze which tasks can be candidates for automation or habit building.

To set the value of a task use the `wp` or `willpower` keyword:

```
pydo add Add recurrence support to pydo willpower:4
```

As with the [priority](priority.md), I use a range of values from `0` to `5` but
the parameter allows any integer.
