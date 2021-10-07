---
title: Dates
date: 20200301
author: Lyz
---

A task does not require a due date:

```pydo
pydo add Send Alice a birthday card
```

However these are the kind of tasks can benefit from having a due date.

# The `due` date

Use the `due` task attribute to define the date by which a task
needs to be completed. Using the previous example, you can set the `due` date to
Alice's birthday:

```bash
pydo add Send Alice a birthday card due:2016-11-08
```

Now your task has an associated due date, to help you determine when you need to
work on it.

To change the due date of a task use the `mod` command:

```bash
pydo mod {{ task_id }} due:{{ new_due_date }}
```

# Date format

`pydo` understands different ways of expressing dates.

* `YYYY-MM-DD`: Enter year, month and day.
* `YYYY-MM-DDTHH:mm`: Enter year, month, day, hour and minute.
* `now`: Current local date and time.
* `tomorrow`: Local date for tomorrow, same as `now + 24h`.
* `yesterday`: Local date for yesterday, same as `now - 24h`.
* `monday`, `tuesday`, ...: Local date for the specified day, after today. There
    is also available in the short three lettered version: `mon`, `tue`...
* Combination of the next operators to specify a relative date from `now`:

    * `s`: seconds,
    * `m`: minutes.
    * `h`: hours,
    * `d`: days.
    * `w`: weeks.
    * `mo`: months.
    * `rmo`: relative months. Use this if you want to set the 3rd Friday of the month.
    * `y`: years.

    So `1y2mo30s` will set the date to `now + 1 year + 2 months + 30 seconds`.
