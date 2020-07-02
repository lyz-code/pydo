---
title: Estimate
date: 20200301
author: Lyz
---

The `estimate` optional task attribute registers how many hours do you expect to
spend on a task.

In the [Scrum](https://en.wikipedia.org/wiki/Scrum_%28software_development%29)
methodology, assigning time estimate to tasks is a sin. Instead they use *story
points*, which is an dimensionless quantity to compare tasks between themselves.
The advantages of using *story points* is that you are not commiting to do
a task in a specified amount of time and that it's easier to estimate if you
are going to need more or less time to do a task than an other in relative
terms. Once you complete several
[sprints](https://en.wikipedia.org/wiki/Scrum_%28software_development%29#Sprint),
this estimate method is said to be more accurate.

I've tried using *story points* in the past, but I find them unintuitive and
useless when trying to improve your estimations. But as the `estimate` keyword
accepts any float, you can use it to store *story points*.

To set the estimate of a task use the `est` or `estimate` keyword:

```
$: pydo add Task that takes 5 hours to complete est:5
  [+] Added task 3: Task that takes 5 hours to complete
```

Right now we only use the `estimate` for filtering or visualization purposes.
But we plan to support reports to do data analysis on the difference between the
estimation and the real time required to complete the task, so as to suggest
estimation improvements.
