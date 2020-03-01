---
title: Dates
date: 20200301
author: Lyz
---

A task does not require a due date, and can simply be a statement of need:

```pydo
pydo add Send Alice a birthday card
```

However this is exactly the kind of task can benefit from having a due date, and
perhaps several other dates also.

There are several dates that can decorate a task, each with its own meaning and
effects. You can choose to use some, all or none of these, but like all
pydo features, they are there in case your needs require it, but you do
not pay a performance or friction penalty by not using them.

# The `due` Date

Use a `due` date to specify the exact date by which a task must be completed. This
corresponds to the last possible moment when the task can be considered on-time.
Using our example, we can set the due date to be Alice's birthday:

```bash
pydo add Send Alice a birthday card due:2016-11-08
```

Now your task has an associated due date, to help you determine when you need to
work on it.
There is also an overdue report that makes use of the OVERDUE virtual tag, to show you what is already late. If you run the calendar report, your due date will be highlighted on it.

What we see here is that Taskwarrior leverages the metadata to drive various features. Several reports will sort by due date, and as we see above, a task that has a due date now belongs on your schedule.
