"""
Module to store the representations of the data.

Functions:
    open: Print the open tasks that match a task filter.
    projects: Print the projects information.
    tags: Print the tags information.

Classes:
    Report: Class to manage the data to print.

Internal Functions:
    _print_entities: Print the entity attributes.
    _remove_null_columns: Remove the columns that have all None items.
    _date2str: Convert a datetime object into a string with the format specified in
        the configuration.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from tabulate import tabulate

from pydo import config, exceptions, types
from pydo.adapters import repository
from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import Task


class Report(list):
    """
    Class to manage the data to print.

    Public Methods:
        add: Add a row of data to the report.
        print: Print the report.

    Internal Methods:
        _remove_null_columns: Remove the columns that have all None items.
    """

    def __init__(self, labels: List["str"]) -> None:
        self.labels = labels
        self.data: List = []

    def _remove_null_columns(self) -> None:
        """
        Method to remove the columns that have all None items from the report_data.
        """

        for column in reversed(range(0, len(self.labels))):
            # If all entities have the None attribute value, remove the column from
            # the report.
            column_used = False
            for row in range(0, len(self.data)):
                if self.data[row][column] not in [None, ""]:
                    column_used = True

            if not column_used:
                [row.pop(column) for row in self.data]
                self.labels.pop(column)

    def add(self, data: List) -> None:
        """
        Method to add a row of data to the report.
        """
        self.data.append(data)

    def print(self) -> None:
        """
        Method to print the report.
        """
        self._remove_null_columns()

        if len(self.data) == 0:
            raise exceptions.EntityNotFoundError(
                "The report doesn't have any data to print"
            )
        print(tabulate(self.data, headers=self.labels, tablefmt="simple"))


def _get_columns_and_labels(
    config: config.Config,
    entities: List[types.Entity],
    report_name: str,
) -> Tuple[List[str], List[str]]:
    """
    Function to prepare the columns and labels from the reports.
    """

    columns = config.get(f"report.{report_name}.columns", [])
    labels = config.get(f"report.{report_name}.labels", [])

    if not isinstance(columns, list):
        raise ValueError("The columns configuration of the open report is not a list.")
    if not isinstance(labels, list):
        raise ValueError("The labels configuration of the open report is not a list.")

    return columns, labels


def _print_entities(
    config: config.Config,
    entities: List[types.Entity],
    columns: List[str],
    labels: List[str],
) -> None:
    """
    Function to print the entity attributes.

    The report_name will be used to extract the columns and labels from the
    configuration.
    """

    report = Report(labels)

    for entity in entities:
        entity_line = []
        for attribute in columns:
            if isinstance(entity, Task) and attribute == "tags":
                value = ", ".join([tag.id for tag in entity.tags])
            elif isinstance(entity, Task) and attribute == "project":
                if entity.project is not None:
                    value = entity.project.id
                else:
                    value = ""
            else:
                try:
                    value = getattr(entity, attribute)
                except AttributeError:
                    value = ""
                if isinstance(value, list):
                    value = ", ".join(value)
                elif isinstance(value, datetime):
                    value = _date2str(config, value)
            entity_line.append(value)
        report.add(entity_line)

    report._remove_null_columns()
    report.print()


def _date2str(config: config.Config, date: datetime) -> str:
    """
    Function to convert a datetime object into a string with the format
    specified in the report.date_format configuration.
    """
    date_format = config.get("report.date_format")

    if not isinstance(date_format, str):
        raise ValueError(
            "The date format definition in the configuration is not a string."
        )
    return date.strftime(date_format)


def open(
    repo: repository.AbstractRepository,
    config: config.Config,
    entity_filter: Optional[Dict] = None,
) -> None:
    """
    Function to print the open tasks that match a task filter.
    """

    default_search = {"state": "open", "type": "task"}
    search = {**default_search}

    if entity_filter is not None:
        search = {**search, **entity_filter}

    try:
        tasks = repo.msearch(Task, search)
    except exceptions.EntityNotFoundError:
        raise exceptions.EntityNotFoundError(
            "No open tasks found that match the filter criteria"
        )

    # Convert task ids in short ids.
    short_ids = repo.fulid.sulids([task.id for task in tasks])
    for task in tasks:
        # The following line is required for the tags to be loaded in the report,
        # otherwise it appears as empty :S
        task.tags
        task.id = short_ids[task.id]

    columns, labels = _get_columns_and_labels(config, tasks, "open")
    _print_entities(config, tasks, columns, labels)


def projects(repo: repository.AbstractRepository) -> None:
    """
    Function to print the projects information.
    """

    projects = repo.all(Project)
    report = Report(["Name", "Open Tasks", "Description"])

    # Gather tasks without project
    try:
        report.add(
            [
                "None",
                len(repo.msearch(Task, {"state": "open", "project_id": None})),
                "Tasks without project",
            ]
        )
    except exceptions.EntityNotFoundError:
        pass

    # Gather projects data
    for project in projects:
        if project.tasks is not None:
            open_tasks = [task for task in project.tasks if task.state == "open"]
        else:
            continue

        if len(open_tasks) > 0:
            report.add([project.id, len(open_tasks), project.description])

    report.print()


def tags(repo: repository.AbstractRepository) -> None:
    """
    Function to print the tags.
    """

    tags = repo.all(Tag)
    report = Report(["Name", "Open Tasks", "Description"])

    # Gather tasks without tags
    try:
        open_tasks = repo.search(Task, "state", "open")
        open_tasks_without_tags = [task for task in open_tasks if len(task.tags) == 0]
        if len(open_tasks_without_tags) > 0:
            report.add(
                [
                    "None",
                    len(open_tasks_without_tags),
                    "Tasks without tags",
                ]
            )
    except exceptions.EntityNotFoundError:
        pass

    # Gather tags data
    for tag in tags:
        if tag.tasks is not None:
            open_tasks = [task for task in tag.tasks if task.state == "open"]
        else:
            continue

        if len(open_tasks) > 0:
            report.add([tag.id, len(open_tasks), tag.description])
    report.print()
