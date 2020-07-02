Recurrence is used to create periodical tasks, such as paying the rent or
mowing the lawn.

There are two types of recurrence:

* *Recurring*: Task which needs to be done every specified period of time, like
    day, week, etc. It doesn't matter when you complete the task, the next one
    will be created based on the original due date.
* *Repeating*: When this task gets completed or deleted, a duplicate will be
    created with the specified time offset from the closing date. I.e.
    subsequent tasks get delayed (e.g. mowing the lawn).

`pydo` implements recurrence with the creation of two kind of tasks: parent and
children. The first one holds the template for the second. Each time a child
is completed or deleted, the parent attributes are copied and the due date is
set according to the recurrence type.

`pydo` will only maintain one children per parent, so it won't create new tasks
until the existent is either completed or deleted. Furthermore, it will create
only the next actionable task. So if from the last completed children you've
missed 3 tasks, those won't be created.

# Create a recurring or repeating task.

To create a recurrent or repeating task, the recurrence time must be set under
the `rec` or `rep` attribute. That attribute must match the [pytho
date](dates.md) format.

```bash
$: pydo add Pay the rent due:2021-11-01 rec:1mo
  [+] Added recurring task 0: Pay the rent
  [+] Added first child task with id 1

$: pydo add Mow the lawn due:today rep:20d
  [+] Added repeating task 1: Mow the lawn
  [+] Added first child task with id 2
```

Once they are created, the children will show in the `open` report, but not the
parent.
```bash
$: pydo
     ╷              ╷                  ╷
  ID │ Description  │ Due              │ Parent
╺━━━━┿━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━┿━━━━━━━━╸
  1  │ Pay the rent │ 2021-11-01 00:00 │ 0
  2  │ Mow the lawn │ 2021-10-07 13:38 │ 1
     ╵              ╵                  ╵
```

The recurrent and repeating parents can be seen with the `recurring` report.

```bash
$: pydo recurring

     ╷              ╷       ╷           ╷
  ID │ Description  │ Recur │ RecurType │ Due
╺━━━━┿━━━━━━━━━━━━━━┿━━━━━━━┿━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━╸
  0  │ Pay the rent │ 1mo   │ Recurring │ 2021-11-01 00:00
  1  │ Mow the lawn │ 20d   │ Repeating │ 2021-10-07 13:38
     ╵              ╵       ╵           ╵
```

# Completing or deleting a repeating task

If you complete or delete the children of a recurrent or repeating task, the
next child will be spawned. But if you wish to delete or complete the parent so
no further children gets created, you can do either by calling `do` or `rm`
with the parent task id, or with the `--parent` flag with the child id. The
advantage of the second method is that you don't need to know the parent id, and
it will close both parent and children.

```bash
$: pydo rm --parent 1
  [+] Closed child task 1: Pay the rent with state deleted
  [+] Closed parent task 0: Pay the rent with state deleted

$: pydo
     ╷              ╷                  ╷
  ID │ Description  │ Due              │ Parent
╺━━━━┿━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━┿━━━━━━━━╸
  2  │ Mow the lawn │ 2021-10-07 13:43 │ 1
     ╵              ╵                  ╵
```

# Modifying a recurring task

If changes are made in a child task, those changes wont be propagated to the
following children, if you want to make changes permanent, you need to change
the parent either using the parent task id or using `mod --parent` with the children
id.

# Freeze a parent task

If you need to temporary pause the creation of new children you can `freeze` the
parent task either with it's id or with `freeze --parent` using the children id.
Frozen tasks will appear in the `frozen` report.

To resume the children creation use the `thaw` command.

```
$: pydo freeze 2 --parent
  [+] Frozen recurrent task 1: Mow the lawn and deleted it's last child 2

$: pydo thaw 1
  [+] Thawed task 1: Mow the lawn, and created it's next child task with id 3
```
