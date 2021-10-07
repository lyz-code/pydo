"""Gather all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

import datetime
import logging
from contextlib import suppress
from typing import List, Optional, Union

from repository_orm import EntityNotFoundError, Repository

from .model import RecurrentTask, Task, TaskChanges, TaskSelector, TaskState, TaskType
from .model.date import convert_date

log = logging.getLogger(__name__)


def add_task(repo: Repository, change: TaskChanges) -> Union[RecurrentTask, Task]:
    """Create a new task.

    If it's a RecurrentTask, it returns the parent.
    """
    task: Optional[TaskType] = None

    if len(change.tags_to_add) > 0:
        change.task_attributes["tags"] = change.tags_to_add

    if change.task_attributes.get("recurrence_type", None) in [
        "recurring",
        "repeating",
    ]:
        task = repo.add(RecurrentTask(**change.task_attributes))
        child_task = repo.add(task.breed_children())

        log.info(
            f"Added {task.recurrence_type} task {task.id_}:" f" {task.description}"
        )
        log.info(f"Added first child task with id {child_task.id_}")
    else:
        task = repo.add(Task(**change.task_attributes))
        log.info(f"Added task {task.id_}: {task.description}")

    repo.commit()

    return task


def do_tasks(
    repo: Repository,
    selector: TaskSelector,
    complete_date_str: str = "now",
    delete_parent: bool = False,
) -> None:
    """Complete tasks that match a task selector.

    Args:
        repo:
        selector: Object that identifies tasks by ids or their attributes
        complete_date_str:
        delete_parent:
    """
    _close_tasks(repo, selector, TaskState.DONE, complete_date_str, delete_parent)


def rm_tasks(
    repo: Repository,
    selector: TaskSelector,
    complete_date_str: str = "now",
    delete_parent: bool = False,
) -> None:
    """Delete tasks that match a task selector.

    Args:
        repo:
        selector: Object that identifies tasks by ids or their attributes
        complete_date_str:
        delete_parent:
    """
    _close_tasks(repo, selector, TaskState.DELETED, complete_date_str, delete_parent)


def _close_tasks(
    repo: Repository,
    selector: TaskSelector,
    state: TaskState,
    close_date_str: str = "now",
    delete_parent: bool = False,
) -> None:
    """Close a list of tasks based on a task filter.

    It gathers the common actions required to complete or delete tasks.
    """
    selector.task_filter["active"] = True
    tasks = _tasks_from_selector(repo, selector)

    for task in tasks:
        _close_task(repo, task, state, close_date_str, delete_parent)

    repo.commit()


def _tasks_from_selector(repo: Repository, selector: TaskSelector) -> List[TaskType]:
    """Return the tasks that match the criteria of the task selector."""
    tasks: List[TaskType] = [
        repo.get(task_id, [selector.model]) for task_id in selector.task_ids
    ]

    if selector.task_filter != {}:
        # Remove the tasks that don't meet the task_filter
        for task in tasks:
            # Check if the task_filter is not a subset of the properties of the task.
            # SIM205: Use 'selector.task_filter.items() > task.dict().items()' instead
            # No can't do, if we do, the subset checking doesn't work
            if not selector.task_filter.items() <= task.dict().items():  # noqa: SIM205
                tasks.remove(task)

        with suppress(EntityNotFoundError):
            tasks.extend(repo.search(selector.task_filter, [selector.model]))

    # Remove duplicates
    return list(set(tasks))


def _close_task(
    repo: Repository,
    task: Task,
    state: TaskState,
    close_date_str: str = "now",
    delete_parent: bool = False,
) -> None:
    """Close a task.

    It gathers the common actions required to complete or delete tasks.
    """
    close_date = convert_date(close_date_str)

    task.close(state, close_date)

    repo.add(task)

    # If it's a child task of another task
    if task.parent_id is not None:
        log.info(
            f"Closing child task {task.id_}: {task.description} with state {state}"
        )
        parent_task = repo.get(task.parent_id, [Task, RecurrentTask])
        # If we want to close the parent of the task.
        if delete_parent:
            parent_task.close(state, close_date)
            repo.add(parent_task)
            log.info(
                f"Closing parent task {parent_task.id_}: {parent_task.description} with"
                f" state {state}"
            )
        # If it's a child task of a recurrent one, we need to spawn the next child.
        elif isinstance(parent_task, RecurrentTask):
            new_child_task = parent_task.breed_children(task)
            repo.add(new_child_task)
            log.info(
                f"Added child task {new_child_task.id_}: {new_child_task.description}",
            )
    # If it's a simple task
    else:
        log.info(f"Closing task {task.id_}: {task.description} with state {state}")
        if delete_parent:
            log.info(f"Task {task.id_} doesn't have a parent")


def modify_tasks(
    repo: Repository,
    selector: TaskSelector,
    change: TaskChanges,
    modify_parent: bool = False,
    is_recurrent: bool = False,
) -> None:
    """Modify the attributes of the tasks matching a filter."""
    if not is_recurrent:
        selector.model = Task
        task_type = "task"
    else:
        selector.model = RecurrentTask
        task_type = "recurrent task"

    tasks = _tasks_from_selector(repo, selector)

    for task in tasks:
        original_task = task.copy(deep=True)
        for tag in change.tags_to_remove:
            try:
                task.tags.remove(tag)
            except ValueError:
                log.warning(f"Task {task.id_} doesn't have " f"the tag {tag} assigned.")

        for tag in change.tags_to_add:
            task.tags.append(tag)

        for attribute, value in change.task_attributes.items():
            task.__setattr__(attribute, value)

        if task != original_task:
            task.modified = datetime.datetime.now()
            repo.add(task)
            log.info(f"Modified {task_type} {task.id_}.")

        if modify_parent:
            if task.parent_id is not None:
                parent_change = change.copy()
                with suppress(EntityNotFoundError):
                    parent_selector = TaskSelector(task_ids=[task.parent_id])
                    modify_tasks(
                        repo, parent_selector, parent_change, is_recurrent=True
                    )
            else:
                log.warning(f"Task {task.id_} doesn't have a parent task.")
    repo.commit()


def freeze_tasks(
    repo: Repository,
    selector: TaskSelector,
) -> None:
    """Freeze a list of tasks based on a task filter."""
    tasks = _tasks_from_selector(repo, selector)
    for task in tasks:
        if type(task) == Task:
            child_task = task
            if child_task.parent_id is None:
                raise ValueError(
                    f"Task {child_task.id_}: {child_task.description} is not the child"
                    " of any recurrent task, so it can't be frozen"
                )
            parent_task = repo.get(child_task.parent_id, [RecurrentTask])
        elif type(task) == RecurrentTask:
            parent_task = task
            try:
                child_task = repo.search(
                    {"active": True, "parent_id": task.id_}, [Task]
                )[0]
            except EntityNotFoundError as error:
                raise EntityNotFoundError(
                    f"The recurrent task {task.id_}: {task.description} has no active "
                    "children"
                ) from error
        parent_task.freeze()
        repo.add(parent_task)
        repo.delete(child_task)
        log.info(
            f"Frozen recurrent task {parent_task.id_}: {parent_task.description} and "
            f"deleted it's last child {child_task.id_}"
        )
    repo.commit()


def thaw_tasks(
    repo: Repository, selector: TaskSelector, state: Optional[TaskState] = None
) -> None:
    """Thaw a list of tasks based on a task filter."""
    selector.model = RecurrentTask
    selector.task_filter["state"] = TaskState.FROZEN

    if state is None:
        state = TaskState.BACKLOG

    tasks = _tasks_from_selector(repo, selector)

    if len(tasks) == 0:
        raise EntityNotFoundError("No frozen tasks were found with that criteria")

    for task in tasks:
        if type(task) == RecurrentTask:
            task.thaw(state)
            repo.add(task)

            try:
                children = repo.search({"parent_id": task.id_, "active": False}, [Task])
            except EntityNotFoundError:
                children = []

            if len(children) == 0:
                last_child = None
            else:
                last_child = children[-1]

            child_task = repo.add(task.breed_children(last_child))

            log.info(
                f"Thawed task {task.id_}: {task.description}, and created it's next "
                f"child task with id {child_task.id_}"
            )
    repo.commit()
