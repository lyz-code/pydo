---
title: Roadmap
date: 20200301
author: Lyz
---

`pydo`'s initial development has been split into phases. Follow the evolution
of each item in the [issues](https://github.com/lyz-code/pydo/issues) page.

# 0.1.0. Task structure to be able to import from taskwarrior

Create the initial infrastructure to import Taskwarrior tasks and do basic
operation on them.

* [ ] Define initial program structure.
    * [x] Configuration management.
    * [x] Tasks initial schema:
        * [x] Body.
        * [x] Priority.
        * [x] Due.
        * [x] Estimate.
        * [x] Willpower.
        * [x] Fun.
        * [x] Value.
        * [x] Kanban.
    * [x] Command line friendly IDs system.
    * [x] Projects initial schema.
    * [x] Tags initial schema.
    * [x] Installation.
    * [x] Continuous Integration pipeline.
    * [ ] Initial documentation.
    * [ ] [Recurrence](https://tasklite.org/concepts.html):
        * [ ] Repeating.
        * [ ] Recurring.

    * [ ] Import from taskwarrior.

* [x] Basic commands:
    * [x] Add task.
    * [x] Complete task.
    * [x] Delete task.

* [x] Basic reports:
    * [x] List report.
    * [x] Projects report.
    * [x] Tags report.

# 0.2.0. Make it usable

Create the commands to match Taskwarrior functionality.

* [ ] Display task, project, tag information

* [ ] Task attributes:
    * [ ] Task wait.
    * [ ] Task dependencies and blocks.
    * [ ] Task Urgency

* [ ] Commands
    * [ ] Modify command
        * [ ] Modify tasks
        * [ ] Modify projects
        * [ ] Modify tags

    * [ ] Delete/Complete multiple tasks
    * [ ] `undo`
    * [ ] Config
        * [ ] Introduce the labels into the config
        * [ ] Config print
        * [ ] Config add
        * [ ] Add task attribute labels in the config
    * [ ] log
    * [ ] Export to json
    * [ ] Search

* [ ] Reports
    * [ ] Sort as an argument for the list report `sort:priority+`
    * [ ] all
    * [ ] open
    * [ ] waiting
    * [ ] recurring
    * [ ] query (sql)
    * [ ] overdue

# 0.3.0. Add further functionality

Start creating additional value.

* [ ] Start/Stop
* [ ] Create nested subtasks in a way as I use vc
* [ ] Task rotting: task inactivity at x months, task dead at x months.
* [ ] Create validation criteria as some kind of subtasks
* [ ] Add epics
* [ ] Add habits: Positive and negative habits, annotate when they happen and
      add alarms. Set a max and min recurrence.
* [ ] Serial tasks: recurrent without date, like study book, 25 pages starting value, increment
* [ ] Set up an end of tasks, can be both relative to the due or absolute that
  will be automatically deleted or completed if it hasn't been acted upon.
* [ ] Create data visualizations for data analysis using Dash:
    * Speed of sprint, week, day with filter by project or tag
    * [ ] Average day estimate consumption and evolution, also filter possibility by
      tag and project.

# X.X.X Implement Agile functionality

* [ ] Scrum and sprint support
* [ ] Implement a planning command to organize week, or x days in a way di -w does
* [ ] Implement a review command to do similar stuff as taskban does.
* [ ] Week and day overburden, compare due tasks with average est consumption,
  also fun and willpower to see if you are over commiting.
* [ ] When add task to sprint ask for removal of lowest priority.

# X.X.X. To implement some time

* Recommendations:
  * Remove dead or inactive tasks.
  * Change recurrence of periodic tasks.
  * Create Automatic estimate based on 90 percentile of the recurrent tasks
  * Average deviation of est of tasks base on project, tag and est.

* Alerts:
  * Fun and willpower overconsumption or underconsumption alert.
  * Alert when x% of estimate of task has been completed.
  * Alert when the expected day willpower consumption is greater than the max or is
    increasing towards the max.
    * Manual estimate override the automatic to turn the previous alarm off.

* Add real willpower, fun, objective value when done to study the differences between the estimate
  and the real.
* Add recurrence on specified days: recur:sun,tue-fri
* Task done on date, on due date
* Modify start/stop date
* Color on reports: check this [tabulate
  issue](https://github.com/astanin/python-tabulate/issues/8) and the [ANSI
  escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code#24-bit).

* Improve the fulids: Reuse completed tasks number part of the fulid.

* Mark days as holidays so we can get an idea of remaining holidays and that the
  recurrence scheduler asks if you want to skip, move after or before the task
  that would fall there.
* [ ] Add User Defined Attributes support: maybe with metadata in the tasks.

# Not in our roadmap

I'm probably not going to develop the following features, but I'll be glad to
accept PR.

* *Synchronization between devices*: If you want to synchronize your state between
  devices, you can either share your SQLite database through [git](https://en.wikipedia.org/wiki/Git) or
  [Syncthing](https://en.wikipedia.org/wiki/Syncthing), or use MySQL as your
  database and configure the connection of the different devices.

# Possible technologies

* Show database schema: https://github.com/Alexis-benoist/eralchemy
* Search: https://github.com/mengzhuo/sqlalchemy-fulltext-search
