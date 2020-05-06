# Recurrence

Recurrence is used to create tasks periodically, such as paying the rent or
mowing the lawn.

There are two types of recurrence:

* Recurring: Task which needs to be done every specified period of time, like
    day, week, etc. It doesn't matter when you complete the task, the next one
    will be created based on the original due date.
* Repeating: When this task gets completed or deleted, a duplicate will be
    created with the specified time offset from the closing date. I.e.
    subsequent tasks get delayed (e.g. mowing the lawn).

`pydo` implements recurrence with the creation of two kind of tasks: parent and
children. The first one holds the template for the second. So each time a child
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
pydo add Pay the rent due:1st rec:1mo
pydo add Mow the lawn due:today rep:20d
```

Once they are created, the children will show in the `open` report, but not the
parent.
```bash
$: pydo

ID    Title          Due
----  -------------  ----------------
f     Mow the lawn  2020-05-03 14:36
s     Pay the rent   2020-05-03 14:29
```

The parent can be seen with the `repeating` and `recurring` reports.

```bash
$: pydo repeating

ID    Title          Recurrence    Due
----  -------------  ------------  ----------------
d     Mown the lawn  20d           2020-05-03 14:36

$: pydo recurring

ID    Title         Recurrence    Due
----  ------------  ------------  ----------------
a     Pay the rent  1mo           2020-05-03 14:29
```

# Completing or deleting a repeating task

If you complete or delete the children of a recurrent or repeating task, the
next child will be spawned. But if you wish to delete or complete the parent so
no further children gets created, you can do either by calling `done` or `del`
with the parent task id, or with the `-p` argument with the child id. The
advantage of the second method is that you don't need to know the parent id, and
it will close both parent and children

```bash
$: pydo del -p f
$: pydo
ID    Title         Due
----  ------------  ----------------
s     Pay the rent  2020-05-03 14:29
```

# Modifying a recurring task

If changes are made in a child task, those changes wont be propagated to the
following children, so If you want to make changes permanent, you need to modify
the parent either using the parent task id or using `mod -p` with the children
id.

# Freeze a parent task

If you need to temporary pause the creation of new children you can `freeze` the
parent task either with it's id or with `freeze -p` using the children id.
Frozen tasks will appear in the `frozen` report.

To resume the children creation use the `unfreeze` command.


