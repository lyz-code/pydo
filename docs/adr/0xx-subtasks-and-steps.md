Date: 2021-09-23

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
We need to define how are we going to split long tasks into smaller actionable
steps in an user friendly way.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->

There are two use cases:

* Big tasks that need to be subdivided in smaller tasks to enter a sprint
* Small enough tasks to enter the sprint, where the user wants to define the
    small steps required to complete it.

Creating a task requires time to fill up it's attributes: assign an area, tags,
priority, description... It also adds time to the overall management of all the
tasks. This time investment makes sense only for the first case, the small steps
often change and don't have the size to be managed with the rest of the tasks.

## Task division

This idea supports the plan to subdivide a task at two levels: subtasks and
steps.

Subtasks will be `Task` entities so that we can do infinite levels of subtask
nesting. To achieve this we'll need to change the `Task` model to add an
attribute `parent_id` that allows us to relate a task with its subtasks.

Steps will be a new simpler entity `Step` with only `parent_id`, `created`,
`closed`, `state` and `description`, so that it will be easier to create,
potentially only the `description` will be filled by the user, and as it follows
the same structure it will be easy to promote to `Task` if needed.

`Step`s don't have identity by themselves, they are tightly coupled with a task,
that's why they could be saved under the `steps` attribute of the `Task`. Until
`repository-orm` supports nested objects, we'll only be able to use the
`TinyDB` and `Fake` repositories. The benefit from being a task attribute is
that recurrent tasks will inherit them automatically.

In the first iteration to simplify the logic:

* Steps and subtasks will be mutually exclusive.
* Recurrent tasks won't support subtasks, as the children breed won't be
    trivial.

## Paths

Sometimes the task divisions (steps or subtasks) are related between each other,
to model this relationships we'll create `Path`s.

A `Path` is an ordered list of task divisions that need to be consecutively
done, so until one is completed the next are not actionable, therefore if it
get's blocked the whole `Path` is blocked.

```mermaid
graph TD
    First step --> Second step
    Second step --> Third step
```

A `Task` may have many `Path`s.

```mermaid
graph TD
    subgraph Path 1
    Path 1: step 1 --> Path 1: step 2
    Path 1: step 2 --> Path 1: step 3
    end

    subgraph Path 2
    Path 2: step 1 --> Path 2: step 2
    Path 2: step 2 --> Path 2: step 3
    end
```

A `Path` may start from one or more other `Path` steps

```mermaid
graph TD
    subgraph Path 1
    Path 1: step 1 --> Path 1: step 2
    Path 1: step 2 --> Path 1: step 3
    end

    subgraph Path 2
    Path 1: step 2 --> Path 2: step 1
    Path 2: step 1 --> Path 2: step 2
    end
```

```mermaid
graph TD
    subgraph Path 1
    Path 1: step 1 --> Path 1: step 2
    Path 1: step 2 --> Path 1: step 3
    end

    subgraph Path 2
    Path 2: step 1 --> Path 2: step 2
    Path 2: step 2 --> Path 2: step 3
    end

    subgraph Path 3
    Path 1: step 2 --> Path 3: step 1
    Path 2: step 2 --> Path 3: step 1
    Path 2: step 1 --> Path 2: step 2
    end
```

### Path definition

A `Path` will have the next attributes:

* `id_`
* `parent_id`: the `Task` id which this path is related to, whenever there is
    a change in the `Path`, the `modified` attribute of the `Task` will be
    changed.
* `type`: Either `step` or `subtask`, used to fetch the subdivision elements.
* `starting_nodes`: `Optional[List[str]]` If specified, these are the ids of the
    steps or subtasks that need to be completed before the path can be acted
    upon. If it's `None` the `parent_id` is assumed, and the `Path` is
    actionable from the start.

### Paths TUI

The TUI of the paths will show at the top the attributes of the parent task and
then a graph  with the different paths.

The first option is to use a output inspired by `git graph`:

```
Description: This is the parent task's description

---------------------------------------------------------------

 [x] Path 1: Step 1
  |
 [x] Path 1: Step 2
  |
 [x] -------------------- [A] ----------------------- [\] Path 3: Step 1
  | Path 1: Step 3         | Path 2: Step 1                - No longer interesting
  |                        |
 [B] Path 1: Step 4       [ ] Path 2: Step 2
     - Waiting for X
       To happen
```

Where:

* `[ ]`: Todo step
* `[x]`: Done step
* `[B]`: Blocked step
* `[A]`: Currently active step
* `[\]`: Dead end, won't follow this path

Blocked and dead end steps will have a list of reasons why they are in that
state.

Colors will help:

* Inactive tasks (done or still not actionable) will be in grey.
* Active task will be in green.
* Blocked task will be in yellow.

This representation has two main problems that can be difficult to handle the visualization and
controls: long task descriptions and many parallel paths. As these are no corner
cases, maybe a representation similar to `tree` is better.

```
 [A] This is the parent task's description
  │
  ├── [B] Path 1: Definition
  │    ├── [x] Path 1: Step 1
  │    ├── [x] Path 1: Step 2
  │    ├── [x] Path 1: Step 3
  │    └── [B] Path 1: Step 4
  │            * Waiting for X to happen
  │
  ├── [A] Path 2: Definition
  │    ├── [A] Path 2: Step 1
  │    ├── [ ] Path 2: Step 2
  │    └── [ ] Path 2: Step 3
  │         ├── [ ] Path 2.1: Step 1
  │         └── [ ] Path 2.1: Step 2
  │
  └── [\] Path 3: Definition
          * No longer interesting
```

If a task has only one path, a simplified version will be:

```
 [B] This is the parent task's description
  ├── [x] Path 1: Step 1
  ├── [x] Path 1: Step 2
  ├── [x] Path 1: Step 3
  └── [B] Path 1: Step 4
          * Waiting for X to happen
```

The only downside of this visualization is that we won't be able to represent
a path that depends on more than one path. Compared with the other
representation, the downside is neglectible, so we'll start with this
representation. The upsides, is that the interface has only one column, instead
of the undefined number of the first visualization, which makes the coding of
the interface much more simple.

The state of the path is defined by the state of it's subelements:

* If all elements are in state `done`, the path is in state `done`.
* If all elements are in state `blocked`, the path is in state `blocked`.
* If one element is in state `active`, the path is in state `active`.
* If one element is in state `open`, the path is in state `open`.

#### Controls

The user will be able to interact with the Paths TUI through:

* `jklh`: to move between the elements and the paths
* `d`: Toggle element state from done to todo.
* `\`: Toggle element state from dead end to todo.
* `b`: Toggle element state from blocked to todo.
* `A`: Toggle element state from active to todo.
* `D`: Delete the element
* `a`: Add an element below the highlighted one. It uses the task creation TUI
    or the step creation TUI.
* `p`: Start a new path from the highlighted element
* `h`: Toggle the hiding of completed and dead end elements
* `m`: Toggle the moving mode. Moving mode will move the highlighted element with
    `jklh` within the path or to adjacent paths.
* `e`: Edit the highlighted element description.
* `enter`: Enter the Task TUI. If it's a step, do nothing
* `zc`: Fold current path
* `zM`: Fold all paths
* `zo`: Unfold current path
* `zO`: Unfold all paths
* `v`: Enter in visual mode, to select a group of elements and perform an action
    over them.
* `E`: Extract element or elements to a new task.

#### Subtasks CLI interface

Get inspiration in [grit](https://github.com/climech/grit).

# Decision
<!-- What is the change that we're proposing and/or doing? -->

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
