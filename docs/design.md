# Desing docs

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

* [ ] Due

* [ ] Wait

* [ ] Recurrence (https://tasklite.org/concepts.html)
  * [ ] Repeating
  * [ ] Recurring

* [ ] Dependencies and blocks

* [ ] Import from taskwarrior

* [ ] Complete documentation with:
  * https://taskwarrior.org/docs/
  * https://tasklite.org/usage/index.html

### 0.2.0. Make it usable

* [ ] Modify
  * [ ] Modify tasks
  * [ ] Modify projects
  * [ ] Modify tags
  * [ ] Review all the .session.commit() to see if you can use the modify method

* [ ] Delete/Complete multiple tasks

* [ ] Display task, project, tag information

* [ ] Urgency

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
* [ ] Add behaviors

* [ ] Stats - Dash

### X.X.X. Implement some time

* [ ] task done on date, on due date
* [ ] Modify start/stop date
* [ ] Color on reports
  * [ ] optional
  https://github.com/astanin/python-tabulate/issues/8
  https://en.wikipedia.org/wiki/ANSI_escape_code#24-bit

* [ ] Improve the fulids
  * [ ] Reuse completed tasks number part of the fulid

* [ ] Add uda support
  * [ ] Add metadata to tasks
* [ ] Review overdue tasks in a way di -w does
* [ ] Organize week, organize the next x days in a way di -w does
* [ ] Scrum and sprint support

## Technologies

* Show database schema: https://github.com/Alexis-benoist/eralchemy
* Search: https://github.com/mengzhuo/sqlalchemy-fulltext-search

## Related

* [Tasklite](https://tasklite.org/)
* [Taskwarrior](https://taskwarrior.org/)
