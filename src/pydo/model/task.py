"""Define the model of the task entities.

Classes:
    Task: Singular task
    RecurrentTask: Task that is repeated over the time
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field
from repository_orm import Entity

from .date import convert_date

log = logging.getLogger(__name__)


TaskAttrs = Dict[str, Any]


class TaskState(str, Enum):
    """Define the possible task states."""

    BACKLOG = "backlog"
    # T101: fixme found (T O D O). Lol, it's not a comment to fix something
    TODO = "todo"  # noqa: T101
    BLOCKED = "blocked"
    DOING = "doing"
    REVIEW = "review"
    DONE = "done"
    DELETED = "deleted"
    FROZEN = "frozen"


class Task(Entity):
    """Base definition of a task.

    Attributes:
        body: Long definition of the entity.
        description: Short definition of the entity.
        due: Date before the task has to be closed.
        estimate: Measure of the size of the task in time or points.
        fun: Measure of the amount of fun doing the task gives you.
        id_: Entity identifier.
        parent: Task parent task. It's populated by the repositories.
        parent_id: Id of Task parent task.
        priority: Measure of the urgency to close the task.
        area:
        state: Categorizes and defines the actions that can be executed over the
            One of ['backlog', 'done', 'doing', 'review', todo', 'deleted', 'frozen'].
        tag_ids: List of Tag Ids associated to the task.
        value: Measure how much you feel this task is going to help you achieve a
            specific goal.
        wait: Date to start to show the task in the reports.
        willpower: Measure how much energy the execution of the task consumes.
            Understanding energy as physical or mental energy.
        closed: Date when the entity was closed.
        created: Date when the entity was created.
    """

    id_: int = -1
    description: Optional[str] = None
    state: TaskState = TaskState.BACKLOG
    closed: Optional[datetime] = None
    created: datetime = Field(default_factory=datetime.now)
    modified: datetime = Field(default_factory=datetime.now)
    body: Optional[str] = None
    due: Optional[datetime] = None
    wait: Optional[datetime] = None
    estimate: Optional[float] = None
    fun: Optional[int] = None
    priority: Optional[int] = None
    value: Optional[int] = None
    willpower: Optional[int] = None
    parent_id: Optional[int] = None
    active: bool = True
    area: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    def close(
        self,
        state: TaskState = TaskState.DONE,
        close_date: Optional[datetime] = None,
    ) -> None:
        """Close the task.

        It will set the following attributes:
            * state: `state`.
            * closed: to `closed` unless it is None, in which case it will set the
                current date.
        """
        if close_date is None:
            close_date = datetime.now()
        self.closed = close_date
        self.modified = datetime.now()
        self.state = state
        self.active = False


class RecurrenceType(str, Enum):
    """Define the possible task states."""

    RECURRING = "recurring"
    REPEATING = "repeating"


class RecurrentTask(Task):
    """Define the model of a task that is repeated over the time.

    Attributes:
        body: Long definition of the entity.
        children: List of the task children task. It's populated by the repositories.
        description: Short definition of the entity.
        due: Date before the task has to be closed.
        estimate: Measure of the size of the task in time or points.
        fun: Measure of the amount of fun doing the task gives you.
        id: Entity identifier.
        parent: Task parent task. It's populated by the repositories.
        parent_id: Id of Task parent task.
        priority: Measure of the urgency to close the task.
        area: .
        state: Categorizes and defines the actions that can be executed over the
            entity. One of ['open', 'completed', 'deleted', 'frozen'].
        tag_ids: List of Tag Ids associated to the task.
        type: Defines the task kind. One of ['task', 'recurrent_task'].
        value: Measure how much you feel this task is going to help you achieve a
            specific goal.
        wait: Date to start to show the task in the reports.
        willpower: Measure how much energy the execution of the task consumes.
            Understanding energy as physical or mental energy.
        agile: Defines the agile state of the task.
            One of ['backlog', 'complete', 'doing', 'review', todo'].
        closed: Date when the entity was closed.
        created: Date when the entity was created.
        recurrence: Time between creation of recurrent tasks.
        recurrence_type: Kind of recurrence.  One of ['recurring', 'repeating'].
    """

    due: datetime
    recurrence: str
    recurrence_type: RecurrenceType

    def breed_children(self, last_child: Optional[Task] = None) -> Task:
        """Create the next children task."""
        child_attributes = self._generate_children_attributes()

        if last_child is None:
            now = datetime.now()
            if self.due > now:
                child_attributes["due"] = self.due
            else:
                child_attributes["due"] = datetime.now()
        elif self.recurrence_type == "recurring":
            child_attributes["due"] = self._next_recurring_due()
        elif self.recurrence_type == "repeating":
            child_attributes["due"] = self._next_repeating_due(last_child)

        return Task(**child_attributes)

    def _next_recurring_due(self) -> datetime:
        """Calculate the next due date of recurring parent children.

        It will apply `recurrence` to the parent's due date, till we get the next
        one in the future.

        To speed it up, you can't use the last child attributes. You'll need to
        Improve the convergence algorithm, maybe a Bisection, Regula Falsi or Newton.
        """
        last_due = self.due
        while True:
            next_due = convert_date(self.recurrence, last_due)
            if next_due > datetime.now():
                return next_due
            last_due = next_due

    def _next_repeating_due(self, last_child: Task) -> datetime:
        """Calculate the next due date of repeating parent children.

        It will apply `recurrence` to the last completed or deleted child's
        completed date. If no child exists, it will use the parent's due date.
        """
        now = datetime.now()
        next_due = convert_date(self.recurrence, last_child.closed)

        if next_due < now:
            return now

        return next_due

    def _generate_children_attributes(self) -> Dict[str, Any]:
        """Create the child attributes from the parent's."""
        child_attributes = self.dict(
            exclude={"created", "id_", "recurrence_type", "recurrence", "last_child"}
        )

        # Set child particular attributes
        child_attributes["parent_id"] = self.id_

        return child_attributes

    def freeze(self) -> None:
        """Freeze the task."""
        self.state = TaskState.FROZEN
        self.modified = datetime.now()
        self.active = False

    def thaw(self, state: TaskState = TaskState.BACKLOG) -> None:
        """Reactivate a frozen task.

        Args:
            state: Task state for the reactivated task.
        """
        if not self.state == TaskState.FROZEN:
            raise ValueError(f"Task {self.id_}: {self.description} is not frozen")

        self.state = state
        self.modified = datetime.now()
        self.active = True


TaskType = Union[Task, RecurrentTask]


class TaskSelector(BaseModel):
    """Represent a group of tasks by their ID or a task filter.

    Args:
        task_ids: List of the ids of the tasks you want to act upon.
        task_filter: Task attributes of the tasks you want to act upon. A search will
            be done in the repo with them.
    """

    task_ids: List[int] = Field(default_factory=list)
    task_filter: TaskAttrs = Field(default_factory=dict)
    model: Union[Type[Task], Type[RecurrentTask]] = Task
    sort: List[str] = Field(default_factory=list)


class TaskChanges(BaseModel):
    """Represent a change done on a task or group of tasks.

    Args:
        task_attributes: The task attributes you want to change and their value.
        tags_to_add: The tags you want to add to the tasks.
        tags_to_remove: The tags you want to remove to the tasks.
        task_ids: List of the ids of the tasks you want to act upon.
        task_filter: Task attributes of the tasks you want to act upon. A search will
            be done in the repo with them.
    """

    task_attributes: TaskAttrs = {}
    tags_to_add: List[str] = Field(default_factory=list)
    tags_to_remove: List[str] = Field(default_factory=list)
