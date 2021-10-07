Date: 2021-09-23

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
We want in a user friendly way to:

* See the tasks that need to be done today, and in this week
* Plan the day, which task needs to be done when
* Get notifications when it's time to do a task (for example attend a meeting)
* Graphical visualization on how much time is left for the active task

# Proposals
<!-- What are the possible solutions to the problem described in the context -->
We can create two TUI interfaces:

* Landing page: Where the relevant information about the state of the tasks is
    shown
* Day planning: Where the user can organize the day.

## Landing page

The user will have the choice to activate or deactivate any of the next
sections.

### Day's plan section

Shows the day's plan, something like:

```
07:00 - 08:00  Breakfast
07:30          Review Anki
08:00 - 13:00  Work
08:00          Work on task 1
11:00 - 11:30  Meeting
13:00 - 14:00  Lunch
```

Where:

* Active elements are in green. An element is activated if `their start planned
    date < actual date` and they are not closed.
* Overdue elements are in red. An element is overdue if `their end planned date
    > actual date` and they are not closed.
* Closed elements are in grey.

If a task doesn't have an end planned date, it means that it can be done
whenever in the day since the start planned date.

If a task has the `notify` attribute set, an alert will be raised when the
`start` date arrives, so that it's actionable, it'll also raise another alert
when it becomes overdue. If a task has the `start_reminder` or `end_reminder`
attributes set, a notification will be shown that amount of time before the
start or end date.

By default the cursor will be at the first active task.

#### Controls

The user will be able to interact with the TUI through:

* `jk`: to move between the elements
* `d`: Toggle element state from done to todo.
* `D`: Delete the element
* `h`: Toggle the hiding of completed elements
* `m`: Toggle the moving mode. Moving mode will move the highlighted element with
    `jk`.
* `enter`: Enter the Task TUI
* `e`: Edit the highlighted element description.
* `a`: Add an element through the task creation TUI

### Close future task section

Shows the tasks that have a due date in the next X days:

```
----------- 2021-09-25 --------------
 11:00  Meeting
        Task 2

----------- 2021-09-26 --------------
        Task 3
```

#### Controls

The user will be able to interact with the TUI through:

* `jk`: to move between the elements
* `d`: Toggle element state from done to todo.
* `D`: Delete the element
* `m`: Toggle the moving mode. Moving mode will move the highlighted element with
    `jk`.
* `enter`: Enter the Task TUI
* `e`: Edit the highlighted element description.
* `a`: Add an element through the task creation TUI

### Notifications section

Shows relevant events related to the tasks state:

* A task has become overdue
* A task has become actionable

```
Overdue: Task 1
Actionable: Task 2
```

#### Controls

The user will be able to interact with the TUI through:

* `jk`: to move between the elements
* `d`: Mark the element as seen
* `enter`: Enter the Task TUI

### Next tasks section

An ordered list of the tasks that should be actioned upon next. Returned by the
`Next` report.

#### Controls

The user will be able to interact with the TUI through:

* `jk`: to move between the elements
* `d`: Toggle element state from done to todo.
* `D`: Toggle element state from deleted to todo.
* `m`: Toggle the moving mode. Moving mode will move the highlighted element with
    `jk`.
* `enter`: Enter the Task TUI
* `e`: Edit the highlighted element description.
* `a`: Add an element through the task creation TUI

### Task section

Shows the active Task TUI. Defined in [this adr]().

## Day planning

* The tasks for the day need to have a `plan` date.

# Decision
<!-- What is the change that we're proposing and/or doing? -->

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
