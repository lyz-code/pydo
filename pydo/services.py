"""
Module to store the operation functions needed to maintain the program.

Functions:
    add_task: Create a new task.
    do_tasks: Complete tasks that match a task filter.
    modify_tasks: Modify the attributes of the tasks matching a filter.
    rm_tasks: Delete tasks that match a task filter.

    tasks_from_task_filter: Extract task ids from a task filter
    parse_task_arguments: Parse the Task attributes from a friendly task
        attributes string.

    install: Function to create the environment for pydo.
    export: Function to export the database to json to stdout.

Internal functions:
    Configure:
        _configure_task: Configures a new task.
        _set_task_tags: Configure the tags of a task.
        _set_task_project: Configure the projects of a task.
    Add:
        _add_simple_task: Adds a non recurrent task.
        _add_recurrent_task: Adds a non recurrent task.
    Close:
        _close_task: Closes a task
        _close_tasks: Closes several tasks based on a task filter

    Filter:
        _parse_task_argument: Parse the Task attributes from a friendly task
            attribute string.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Tuple, Union

from pydo import exceptions
from pydo.adapters import repository
from pydo.model.date import convert_date
from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import RecurrentTask, Task

log = logging.getLogger(__name__)


def _configure_task(repo: repository.AbstractRepository, task: Task) -> None:
    """
    Internal Function to configure the new task:
        * Setting task project
        * Setting task tags
    """
    _set_task_project(repo, task)
    _set_task_tags(repo, task)


def _add_simple_task(
    repo: repository.AbstractRepository, task_attributes: Dict
) -> Task:
    """
    Function to create a new simple task.
    """

    task = Task(repo.create_next_id(Task), **task_attributes)
    _configure_task(repo, task)

    repo.add(task)
    repo.commit()

    log.info(f"Added task {task.id}: {task.description}")

    return task


def _add_recurrent_task(
    repo: repository.AbstractRepository, task_attributes: Dict
) -> Tuple[RecurrentTask, Task]:
    """
    Function to create a new recurring or repeating task.

    Returns both parent and first children tasks.
    """

    parent_task = RecurrentTask(repo.create_next_id(Task), **task_attributes)
    _configure_task(repo, parent_task)
    repo.add(parent_task)
    repo.commit()

    child_task = parent_task.breed_children(repo.create_next_id(Task))
    repo.add(child_task)
    repo.commit()

    log.info(
        f"Added {parent_task.recurrence_type} task {parent_task.id}:"
        f" {parent_task.description}"
    )
    log.info(f"Added first child task with id {child_task.id}")

    return parent_task, child_task


def add_task(
    repo: repository.AbstractRepository, task_attributes: Dict
) -> Union[Tuple[RecurrentTask, Task], Task]:
    """
    Function to create a new task.

    It returns the created task and None if its simple, and the RecurrentTask and the
    first child task if it's recurring or repeating.
    """

    if task_attributes.get("recurrence_type", None) in ["recurring", "repeating"]:
        return _add_recurrent_task(repo, task_attributes)
    else:
        return _add_simple_task(repo, task_attributes)


def _set_task_tags(repo: repository.AbstractRepository, task: Task) -> None:
    """
    Function to set the tags attribute.

    A new tag will be created if it doesn't exist yet.
    """

    try:
        if task.tag_ids is None:
            return
    except AttributeError:
        return

    for tag_id in task.tag_ids:
        try:
            tag = repo.get(Tag, tag_id)
        except exceptions.EntityNotFoundError:
            tag = Tag(id=tag_id, description="")
            repo.add(tag)
            log.info(f"Added tag {tag.id}")


def _set_task_project(repo: repository.AbstractRepository, task: Task):
    """
    Function to set the project of a task.

    A new project will be created if it doesn't exist yet.
    """

    if task.project_id is not None:
        try:
            project = repo.get(Project, task.project_id)
        except exceptions.EntityNotFoundError:
            project = Project(id=task.project_id, description="")
            repo.add(project)
            log.info(f"Added project {project.id}")


def _close_task(
    repo: repository.AbstractRepository,
    task: Task,
    state: str,
    close_date_str: str = "now",
    delete_parent: bool = False,
) -> None:
    """
    Function to close a task.

    It gathers the common actions required to complete or delete tasks.
    """

    if not isinstance(task, Task):
        raise TypeError("Trying to close a task, but the object is a {task}")

    close_date = convert_date(close_date_str)

    task.close(state, close_date)
    repo.add(task)
    repo.commit()

    # If it's a recurrent parent task
    if task.type == "recurrent_task":
        # We need to close its children.
        if task.children is not None:
            for child in task.children:
                child.close(state, close_date)
                repo.add(child)
                repo.commit()
                log.info(
                    f"Closed child task {child.id}: {child.description} with state"
                    f" {state}"
                )
        log.info(f"Closed parent task {task.id}: {task.description} with state {state}")

    # If it's a child task of another task
    elif task.parent is not None:
        log.info(f"Closed child task {task.id}: {task.description} with state {state}")
        # If we want to close the parent of the task.
        if delete_parent:
            task.parent.close(state, close_date)
            repo.add(task.parent)
            repo.commit()
            log.info(
                f"Closed parent task {task.parent.id}: {task.parent.description} with"
                f" state {state}"
            )
        # If it's a child task of a recurrent one, we need to spawn the next child.
        elif isinstance(task.parent, RecurrentTask):
            new_child_task = task.parent.breed_children(repo.create_next_id(Task))
            repo.add(new_child_task)
            repo.commit()
            log.info(
                f"Added child task {new_child_task.id}: {new_child_task.description}",
            )
    # If it's a simple task
    else:
        log.info(f"Closed task {task.id}: {task.description} with state {state}")
        if delete_parent:
            log.info(f"Task {task.id} doesn't have a parent")


def _close_tasks(
    repo: repository.AbstractRepository,
    task_filter: str,
    state: str,
    close_date_str: str = "now",
    delete_parent: bool = False,
) -> None:
    """
    Function to close a list of tasks based on a task filter.

    It gathers the common actions required to complete or delete tasks.
    """

    tasks = tasks_from_task_filter(repo, task_filter)

    for task in tasks:
        _close_task(repo, task, state, close_date_str, delete_parent)


def _parse_task_argument(task_arg: str) -> Tuple[str, Union[str, int, float, datetime]]:
    """
    Function to parse the Task attributes from a friendly task attribute string.

    If the key doesn't match any of the known keys, it will be returned with the key
    "unprocessed".

    Returns:
        attribute_id (str): Attribute key.
        attributes_value (str|int|float|date): Attribute value.
    """

    attribute_conf = {
        "agile": {"regexp": r"^(ag|agile):", "type": "str"},
        "body": {"regexp": r"^body:", "type": "str"},
        "due": {"regexp": r"^due:", "type": "date"},
        "estimate": {"regexp": r"^(est|estimate):", "type": "float"},
        "fun": {"regexp": r"^fun:", "type": "int"},
        "priority": {"regexp": r"^(pri|priority):", "type": "int"},
        "project_id": {"regexp": r"^(pro|project):", "type": "str"},
        "recurring": {"regexp": r"^(rec|recurring):", "type": "str"},
        "repeating": {"regexp": r"^(rep|repeating):", "type": "str"},
        "state": {"regexp": r"^(state):", "type": "str"},
        "tag_ids": {"regexp": r"^\+", "type": "tag"},
        "tags_rm": {"regexp": r"^\-", "type": "tag"},
        "value": {"regexp": r"^(vl|value):", "type": "int"},
        "willpower": {"regexp": r"^(wp|willpower):", "type": "int"},
    }

    for attribute_id, attribute in attribute_conf.items():
        if re.match(attribute["regexp"], task_arg):
            if attribute["type"] == "tag":
                if len(task_arg) < 2:
                    raise ValueError("Empty tag value")
                return attribute_id, re.sub(r"^[+-]", "", task_arg)
            elif task_arg.split(":")[1] == "":
                return attribute_id, ""
            elif attribute["type"] == "str":
                return attribute_id, task_arg.split(":")[1]
            elif attribute["type"] == "int":
                return attribute_id, int(task_arg.split(":")[1])
            elif attribute["type"] == "float":
                return attribute_id, float(task_arg.split(":")[1])
            elif attribute["type"] == "date":
                return (
                    attribute_id,
                    convert_date(":".join(task_arg.split(":")[1:])),
                )
    return "unprocessed", task_arg


def parse_task_arguments(task_args: List[str], mode: str = "add") -> Dict:
    """
    Function to parse the Task attributes from a friendly task attributes string.

    Depending of the mode, the strings that don't match the {key}:{value} notation
    will be:
        * add: Added to the description attribute.
        * filter: Added to task ids attribute.
    """

    task_attributes: Dict = {}

    for task_arg in task_args:
        attribute_id, attribute_value = _parse_task_argument(task_arg)
        if attribute_id in ["tag_ids", "tags_rm", "unprocessed"]:
            try:
                task_attributes[attribute_id]
            except KeyError:
                task_attributes[attribute_id] = []
            task_attributes[attribute_id].append(attribute_value)
        elif attribute_id in ["recurring", "repeating"]:
            task_attributes["recurrence"] = attribute_value
            task_attributes["recurrence_type"] = attribute_id
        else:
            task_attributes[attribute_id] = attribute_value

    try:
        if mode == "add":
            task_attributes["description"] = " ".join(task_attributes["unprocessed"])
        elif mode == "filter":
            task_attributes["task_ids"] = task_attributes["unprocessed"]
        task_attributes.pop("unprocessed")
    except KeyError:
        pass

    return task_attributes


def tasks_from_task_filter(
    repo: repository.AbstractRepository, task_filter: str
) -> List[Task]:
    """
    Function to extract task ids from a task filter.

    If none is found, an EntityNotFoundError error is raised.
    """
    tasks = []
    task_attributes = parse_task_arguments(task_filter.split(" "), "filter")

    try:
        for task_id in task_attributes["task_ids"]:
            tasks.append(repo.get(Task, task_id))
        task_attributes.pop("task_ids")
    except KeyError:
        pass
    if len(task_attributes.keys()) > 0:
        matching_tasks = repo.msearch(Task, task_attributes)
        if matching_tasks is not None:
            tasks.extend(matching_tasks)

    return sorted(tasks)  # type: ignore


def do_tasks(
    repo: repository.AbstractRepository,
    task_filter: str,
    complete_date_str: str = "now",
    delete_parent: bool = False,
) -> None:
    """
    Function to complete tasks that match a task filter.
    """

    _close_tasks(repo, task_filter, "completed", complete_date_str, delete_parent)


def rm_tasks(
    repo: repository.AbstractRepository,
    task_filter: str,
    complete_date_str: str = "now",
    delete_parent: bool = False,
) -> None:
    """
    Function to delete tasks that match a task filter.
    """

    _close_tasks(repo, task_filter, "deleted", complete_date_str, delete_parent)


def modify_tasks(
    repo: repository.AbstractRepository,
    task_filter: str,
    task_attributes: Dict,
    modify_parent: bool = False,
) -> None:
    """
    Function to modify the attributes of the tasks matching a filter.
    """

    tasks = tasks_from_task_filter(repo, task_filter)
    for task in tasks:
        for attribute, value in task_attributes.items():
            if attribute == "tags_rm":
                if task.tag_ids is None:
                    log.warning(
                        f"Task {task.id} doesn't have any tag assigned.",
                    )
                else:
                    for tag in value:
                        try:
                            task.tag_ids.remove(tag)
                        except ValueError:
                            log.warning(
                                f"Task {task.id} doesn't have the tag {tag} assigned."
                            )
            else:
                task.__setattr__(attribute, value)
        _configure_task(repo, task)
        repo.add(task)

        log.info(f"Modified task {task.id}.")

        if modify_parent:
            if task.parent_id is not None:
                modify_tasks(repo, task.parent_id, task_attributes)
            else:
                log.warning(f"Task {task.id} doesn't have a parent task.")
    repo.commit()


# import json
# from pydo.model import engine

# from sqlalchemy import MetaData
# def export(log):
#     """
#     Function to export the database to json to stdout.
#
#     Arguments:
#         log (logging object): log handler
#
#     Returns:
#         stdout: json database dump.
#     """
#
#     meta = MetaData()
#     meta.reflect(bind=engine)
#     data = {}
#     log.debug("Extracting data from database")
#     for table in meta.sorted_tables:
#         data[table.name] = [dict(row) for row in engine.execute(table.select())]
#
#     log.debug("Converting to json and printing")
#     print(json.dumps(data))
