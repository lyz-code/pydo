# Desing docs

## Todo

### 0.1.0
* [x] Add
* [x] Done
* [x] Delete
* [x] List
* [x] Projects
* [x] Create a basic Config object

* [ ] Short uid
  * [x] rev ulid and search in open/waiting for unique values
  * [x] Create friendli ulids fulids with a set of defined characters for the
    random part.
  * [x] Substitute the ulids from fulids in the code
  * [x] apply sulids into the list report
  * [x] apply sulids into the add/remove/done methods
  * [ ] Generate fulids in a more clever way
    * [ ] convert string to numeric aaaaaaaaaaaa -> 0
    * [ ] Get the last ulid, increment in 1 and encode back

* [ ] Priority

* [ ] Tags

* [ ] `undo`
  * [ ] Set up the log

* [ ] Modify
  * [ ] Review all the .session.commit() to see if you can use the modify method

* [ ] Recurrence (https://tasklite.org/concepts.html)
  * [ ] Repeating
  * [ ] Recurring

* [ ] Delete/Complete multiple tasks

* [ ] Import from taskwarrion

### 0.2.0

* [ ] Refactor using Config
  * [ ] Introduce the labels into the config
  * [ ] Config print
  * [ ] Config add
  * [ ] Add task attribute labels in the config
    * [ ] refactor
* [ ] Kanban
* [ ] Wait
* [ ] Start/Stop
* [ ] Tags report
* [ ] Projects report
* [ ] Export to json

### 0.3.0

* [ ] Create nested subtasks in a way as I use vc
* [ ] Add body of tasks
* [ ] Add epics
* [ ] Add description, priority to projects, migrate to it's own object
* [ ] Color on reports
  * [ ] optional
  https://github.com/astanin/python-tabulate/issues/8
  https://en.wikipedia.org/wiki/ANSI_escape_code#24-bit

* [ ] Improve the fulids
  * [ ] Allow a charset with length != 10 doing base n number operations
  * [ ] Reuse completed tasks number part of the fulid

* [ ] Stats - Dash
* [ ] task done on date, on due date
* [ ] Modify start/stop date

### 0.4.0

* [ ] Review overdue tasks in a way di -w does
* [ ] Organize week, organize the next x days in a way di -w does
* [ ] Scrum and sprint support

## Technologies

* Show database schema: https://github.com/Alexis-benoist/eralchemy
* Search: https://github.com/mengzhuo/sqlalchemy-fulltext-searchttps://faker.readthedocs.io/en/latest/h

## Related

* [Tasklite](https://tasklite.org/)
* [Taskwarrior](https://taskwarrior.org/)
