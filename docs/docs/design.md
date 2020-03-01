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

