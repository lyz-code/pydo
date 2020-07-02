---
title: Objective value
date: 20200424
author: Lyz
---

The `value` optional task attribute registers how much you feel this task
is going to help you achieve a specific goal. It can be associated with
[Scrum business
value](https://medium.com/the-liberators/what-is-this-thing-called-business-value-3b88b734d5a9).

Business value is an horrendous capitalist term with a lot of implications,
therefore we've shorten it to `value`.

If you've categorized your tasks in [projects](projects.md), each one
probably has one or several main objectives. If your tasks have this property,
it can help you priorize which ones need to be done first, or measure the
difference in value between sprints.

To set the value of a task use the `vl` or `value` keyword:

```
$: pydo add Task with high value value:5
  [+] Added task 4: Task with high value
```

As with the [priority](priority.md), I use a range of values from `0` (it
doesn't get me closer to the objective at all) to `5` (it's a critical advance
towards the goal) but the parameter allows any integer.
