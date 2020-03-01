# Desing docs

## Idea on epics, task and subtasks management

Change the idea on how we work on the tasks. With something like `plan task` it
opens a editor window where you specify the subtask hierarchy (as many levels as
needed), once it closes it creates the tasks and blocks the ones that are not
actionable. You can decide to work on the epic (or the parent of all subtasks)
or directly on the first available subtask and both will point to the same subtask.

Maybe we can use this notation in the editor parser:

```markdown
# [ ] Task title: Task description
## [ ] Subtask title: subtask description
```

Also it's important to define if the tasks at the same level are blocking or
paralelizable, so once you mark one as blocked or in review it suggest you to
continue with the next available subtask.

For example, we could use hte following syntax
```markdown
# [P] Task title: Task description
## [ ] paralelizable Subtask title: subtask description
## [ ] (Blocking) blocking Subtask title: subtask description
```

You define till what level of task (only epic and tasks?) to define the est, ov,
fun attributes, the rest will go plain as they are supposed to be done inside
the sprint scope

In the display we could have something like a parent task fulid field.

## Todo

### 0.1.0. Task structure to be able to import from taskwarrior

* [x] Add
* [x] Done
* [x] Delete
* [x] List
* [x] Projects
* [x] Create a basic Config object
* [x] Support fulids
* [x] Projects report
* [x] Tags
* [x] Priority
* [x] Add est to tasks
* [x] Add willpower to tasks
* [x] Add fun to tasks
* [x] Add value to tasks
* [x] Add body of tasks
* [x] Kanban
  * Set in config available values
* [x] Due

* [ ] Recurrence (https://tasklite.org/concepts.html)
  * [ ] Repeating
  * [ ] Recurring

* [ ] Import from taskwarrior

* [ ] Complete documentation with:
  * https://taskwarrior.org/docs/
  * https://tasklite.org/usage/index.html

### 0.2.0. Make it usable

* [ ] Wait

* [ ] Dependencies and blocks

* [ ] Modify
  * [ ] Modify tasks
  * [ ] Modify projects
  * [ ] Modify tags
  * [ ] Review all the .session.commit() to see if you can use the modify method

* [ ] Delete/Complete multiple tasks

* [ ] Display task, project, tag information

* [ ] Sort as an argument `sort:priority+`
* [ ] Urgency
  * Task inactivity at x months
  * Task dead at x months

* [ ] `undo`
  * [ ] Set up the log

* [ ] Refactor using Config
  * [ ] Introduce the labels into the config
  * [ ] Config print
  * [ ] Config add
  * [ ] Add task attribute labels in the config
    * [ ] refactor

* [ ] log
* [ ] Export to json
* [ ] Search
* [ ] Reports
  * [ ] all
  * [ ] open
  * [ ] waiting
  * [ ] recurring
  * [ ] query (sql)

* [ ] Complete documentation with:
  * https://taskwarrior.org/docs/
  * https://tasklite.org/usage/index.html

### 0.3.0. Add further functionality

* [ ] Start/Stop
* [ ] Create nested subtasks in a way as I use vc
* [ ] Create VC as some kind of subtasks
* [ ] Add epics
* [ ] Add habits
  * Positive and negative habits, annotate when they happen and add alarms. Set
    a max and min recurrence.
* [ ] Serial tasks, recurrent without date, process book, 25 pages starting value, increment

* [ ] Stats - Dash
  * Speed of sprint, week, day with filter by project or tag
  * [ ] Average day est consumption and evolution, also filter possibility by
    tag and project

### X.X.X Implement Agile functionality

* [ ] Scrum and sprint support
* [ ] When add task to sprint ask for removal of lowest priority
* [ ] Implement a planning command to organize week, or x days in a way di -w does
* [ ] Implement a review command to do similar stuff as taskban does.
* [ ] Week and day overburden, compare due tasks with average est consumption,
  also fun and willpower to see if you are overcommiting



### X.X.X. To implement some time

* Recommendations
  * Remove dead or inactive tasks
  * Change recurrence of periodic tasks
  * Create Automatic estimate based on 90 percentil of the recurrent tasks
  * Average deviation of est of tasks base on project, tag and est.

* Alerts:
  * Fun and wp overconsumption or underconsumption alert
  * Alert when x% of estimate of task has been completed
  * Alert when the expected day wp consumption is greater than the max or is
    increasing towards the max
    * Manual estimate override the automatic to turn the previous alarm off

* Add real wp, fun, ov when done to study the differences between the estimate
  and the real.
* [ ] Add recurrence on specified days: recur:sun,tue-fri
* [ ] task done on date, on due date
* [ ] Modify start/stop date
* [ ] Color on reports
  * [ ] optional
  https://github.com/astanin/python-tabulate/issues/8
  https://en.wikipedia.org/wiki/ANSI_escape_code#24-bit

* [ ] Improve the fulids
  * [ ] Reuse completed tasks number part of the fulid

* Mark days as holidays so we can get an idea of remaining holidays and that the
  recurrence scheduler asks if you want to skip, move after or before the task
  that would fall there.
* [ ] Add uda support
  * [ ] Add metadata to tasks
* [ ] Review overdue tasks in a way di -w does
* [ ] Change of contexts through i3 focus

## Technologies

* Show database schema: https://github.com/Alexis-benoist/eralchemy
* Search: https://github.com/mengzhuo/sqlalchemy-fulltext-search

## Related

* [Tasklite](https://tasklite.org/)
* [Taskwarrior](https://taskwarrior.org/)
