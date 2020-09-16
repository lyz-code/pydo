"""
Module to store the business model of the task entities.

Classes:
    Task: Singular task
    RecurrentTask: Task that is repeated over the time
"""

import logging
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from pydo import exceptions
from pydo.model import Entity
from pydo.model.date import convert_date

log = logging.getLogger(__name__)


class Task(Entity):
    """
    Class to define the simple task model.

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
        project_id: Id of Project of the task.
        state: Categorizes and defines the actions that can be executed over the
            entity. One of ['open', 'completed', 'deleted', 'frozen'].
        tag_ids: List of Tag Ids associated to the task.
        type: Defines the task kind. One of ['task', 'recurrent_task'].
        value: Measure how much you feel this task is going to help you achieve a
            specific goal.
        wait: Date to start to show the task in the reports.
        willpower: Measure how much energy the execution of the task consumes.
            Understanding energy as physical or mental energy.

    Properties:
        agile: Defines the agile state of the task.
            One of ['backlog', 'complete', 'doing', 'review', todo'].
        closed: Date when the entity was closed.
        closed: Date when the entity was created.

    Methods:
        close: Method to close the entity.

    Internal Methods:
        _get_attributes: Method to extract the entity attributes to a dictionary.
        __eq__: Internal Python method to assess the equally between class objects.
        __lt__: Internal Python method to compare class objects.
        __gt__: Internal Python method to compare class objects.
        __hash__: Internal Python method to create an unique hash of the class object.
        __repr__: Internal Python method to show when printing the object.
        __str__: Internal Python method to show when printing the object.
    """

    def __init__(
        self,
        id: str,
        description: Optional[str] = None,
        agile: Optional[str] = None,
        body: Optional[str] = None,
        closed: Optional[datetime] = None,
        created: Optional[datetime] = None,
        due: Optional[datetime] = None,
        estimate: Optional[int] = None,
        fun: Optional[int] = None,
        parent_id: Optional[str] = None,
        priority: Optional[int] = None,
        project_id: Optional[str] = None,
        state: str = "open",
        tag_ids: Optional[List[str]] = None,
        type: str = "task",
        value: Optional[int] = None,
        wait: Optional[datetime] = None,
        willpower: Optional[int] = None,
    ):
        super().__init__(id, description, state, created, closed)
        self.agile = agile
        self.body = body
        self.children: Optional[List["Task"]] = []
        self.due = due
        self.estimate = estimate
        self.fun = fun
        self.parent: Optional["Task"] = None
        self.parent_id = parent_id
        self.priority = priority
        self.project_id = project_id
        self.project: Optional["Project"] = None
        self.tag_ids = tag_ids
        self.tags: Optional[List["Tag"]] = None
        self.type = type
        self.value = value
        self.wait = wait
        self.willpower = willpower

    def __eq__(self, other) -> bool:
        """
        Internal Python method to assess the equally between class objects.
        """

        if not isinstance(other, Task):
            return False
        return other.id == self.id

    def __lt__(self, other) -> bool:
        """
        Internal Python method to compare class objects.
        """

        return super().__lt__(other)

    def __gt__(self, other) -> bool:
        """
        Internal Python method to compare class objects.
        """

        return super().__gt__(other)

    def __hash__(self) -> int:
        """
        Internal Python method to create an unique hash of the class object.
        """

        return super().__hash__()

    def __str__(self) -> str:
        """
        Internal Python method to show when printing the object.
        """

        return f"<Task {self.id}>"

    def __repr__(self) -> str:
        """
        Internal Python method to show when printing the object.
        """

        return f"<Task {self.id}>"

    def _get_attributes(self) -> Dict:
        """
        Method to extract the entity attributes to a dictionary.
        """

        attributes = super()._get_attributes()

        # Pop the orm generated attributes
        for attribute in ["parent", "project", "tags"]:
            try:
                attributes.pop(attribute)
            except KeyError:
                pass

        return attributes

    @property
    def agile(self) -> Optional[str]:
        """
        Property getter of the attribute that stores the agile state of the task.
        """

        return self._agile

    @agile.setter
    def agile(self, agile_state: Optional[str]) -> None:
        """
        Property setter of the attribute that stores the agile state of the task.

        If the agile property value isn't between the specified ones,
        a `ValueError` will be raised.
        """

        allowed_agile_states: Iterable[str] = [
            "backlog",
            "complete",
            "doing",
            "review",
            "todo",
        ]
        if agile_state is not None and agile_state not in allowed_agile_states:
            raise ValueError(
                f"Agile state {agile_state} is not in the allowed agile states: "
                f"{', '.join(allowed_agile_states)}"
            )
        self._agile = agile_state


class RecurrentTask(Task):
    """
    Class to define the model of a task that is repeated over the time.

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
        project_id: Id of Project of the task.
        state: Categorizes and defines the actions that can be executed over the
            entity. One of ['open', 'completed', 'deleted', 'frozen'].
        tag_ids: List of Tag Ids associated to the task.
        type: Defines the task kind. One of ['task', 'recurrent_task'].
        value: Measure how much you feel this task is going to help you achieve a
            specific goal.
        wait: Date to start to show the task in the reports.
        willpower: Measure how much energy the execution of the task consumes.
            Understanding energy as physical or mental energy.

    Properties:
        agile: Defines the agile state of the task.
            One of ['backlog', 'complete', 'doing', 'review', todo'].
        closed: Date when the entity was closed.
        closed: Date when the entity was created.
        recurrence: Time between creation of recurrent tasks.
        recurrence_type: Kind of recurrence.  One of ['recurring', 'repeating'].

    Methods:
        breed_children: Method to create the next parent children
        close: Method to close the entity.

    Internal Methods:
        _generate_children_attributes: Method to generate the child attributes from
            the parent's.
        _get_attributes: Method to extract the entity attributes to a dictionary.
        _next_recurring_due: Method to calculate the next due date of recurring parent
            children.
        _next_repeating_due: Method to calculate the next due date of repeating parent
            children.
        __eq__: Internal Python method to assess the equally between class objects.
        __lt__: Internal Python method to compare class objects.
        __gt__: Internal Python method to compare class objects.
        __hash__: Internal Python method to create an unique hash of the class object.
        __repr__: Internal Python method to show when printing the object.
        __str__: Internal Python method to show when printing the object.
    """

    def __init__(
        self,
        id: str,
        recurrence: str,
        recurrence_type: str,
        description: Optional[str] = None,
        state: str = "open",
        type: str = "recurrent_task",
        agile: Optional[str] = None,
        body: Optional[str] = None,
        closed: Optional[datetime] = None,
        created: Optional[datetime] = None,
        due: Optional[datetime] = None,
        estimate: Optional[int] = None,
        fun: Optional[int] = None,
        parent_id: Optional[str] = None,
        priority: Optional[int] = None,
        project_id: Optional[str] = None,
        tag_ids: Optional[List[str]] = None,
        value: Optional[int] = None,
        wait: Optional[datetime] = None,
        willpower: Optional[int] = None,
    ):
        super().__init__(
            id,
            description=description,
            state=state,
            type=type,
            agile=agile,
            body=body,
            closed=closed,
            created=created,
            due=due,
            estimate=estimate,
            fun=fun,
            parent_id=parent_id,
            priority=priority,
            project_id=project_id,
            tag_ids=tag_ids,
            value=value,
            wait=wait,
            willpower=willpower,
        )
        if due is None:
            raise exceptions.TaskAttributeError(
                f"You need to specify a due date for {recurrence_type} tasks"
            )

        self.recurrence = recurrence
        self.recurrence_type = recurrence_type

    @property
    def recurrence(self) -> Optional[str]:
        """
        Property getter of the attribute that stores the time between creation
        of recurrent tasks.
        """

        return self._recurrence

    @recurrence.setter
    def recurrence(self, recurrence: Optional[str]) -> None:
        """
        Property setter of the attribute that stores the time between creation
        of recurrent tasks.
        """

        # TODO: We need to perform input validation
        self._recurrence = recurrence

    @property
    def recurrence_type(self) -> Optional[str]:
        """
        Property getter of the attribute that stores the kind of recurrence.
        One of ['recurring', 'repeating'].
        """

        return self._recurrence_type

    @recurrence_type.setter
    def recurrence_type(self, recurrence_type: Optional[str]) -> None:
        """
        Property setter of the attribute that stores the kind of recurrence.
        """

        if recurrence_type in ["repeating", "recurring"]:
            self._recurrence_type = recurrence_type
        else:
            raise exceptions.TaskAttributeError(
                "recurrence_type must be either recurring or repeating"
            )

    def _next_recurring_due(self) -> datetime:
        """
        Method to calculate the next due date of recurring parent children.

        It will apply `recurrence` to the parent's due date, till we get the next
        one in the future.
        """

        # To speed it up, you can't use the last child attributes. You'll need to
        # Improve the convergence algorithm, maybe a Bisection, Regula Falsi or Newton.

        if self.recurrence is None:
            raise ValueError(
                "The recurrence of the task {self.id} is None, so it can't breed"
                " children"
            )
        last_due = self.due
        while True:
            next_due = convert_date(self.recurrence, last_due)
            if next_due > datetime.now():
                return next_due
            last_due = next_due

    def _next_repeating_due(self) -> datetime:
        """
        Method to calculate the next due date of repeating parent children.

        It will apply `recurrence` to the last completed or deleted child's
        completed date. If no child exists, it will use the parent's due date.
        """

        if self.recurrence is None:
            raise ValueError(
                "The recurrence of the task {self.id} is None, so it can't breed"
                " children"
            )
        if self.children is None or len(self.children) == 0:
            if self.due is None:
                raise exceptions.TaskAttributeError(
                    f"The task {self.id} doesn't have a due date, so it can't breed"
                    " children"
                )
            return self.due
        else:
            return convert_date(self.recurrence, max(self.children).closed)

    def _generate_children_attributes(self) -> Dict:
        """
        Method to generate the child attributes from the parent's.
        """

        child_attributes = self._get_attributes()

        # Set child particular attributes
        child_attributes["parent_id"] = self.id
        child_attributes["type"] = "task"

        # Internal attributes to copy
        for attribute in ["agile", "closed", "parent"]:
            try:
                child_attributes[attribute] = child_attributes[f"_{attribute}"]
                child_attributes.pop(f"_{attribute}")
            except KeyError:
                pass

        # Attributes to delete
        for attribute in [
            "_created",
            "id",
            "_recurrence_type",
            "_recurrence",
            "children",
            "parent",
        ]:
            try:
                child_attributes.pop(attribute)
            except KeyError:
                pass

        return child_attributes

    def breed_children(self, children_id: str) -> Task:
        """
        Method to create the next parent children
        """

        try:
            self.children
        except AttributeError:
            self.children: List = []

        child_attributes = self._generate_children_attributes()

        if self.recurrence_type == "recurring":
            child_attributes["due"] = self._next_recurring_due()
        elif self.recurrence_type == "repeating":
            child_attributes["due"] = self._next_repeating_due()

        child_task = Task(children_id, **child_attributes)
        self.children.append(child_task)

        return child_task
