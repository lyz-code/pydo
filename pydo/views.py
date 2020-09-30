"""
Module to store the representations of the data.

Functions:
    open: Print the open tasks that match a task filter.

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
from pydo.model.task import Task


def _print_entities(
    config: config.Config,
    entities: List[types.Entity],
    columns: List[str],
    labels: List[str],
) -> None:
    """
    Function to print the entity attributes.
    """

    report_data: List = []

    columns, labels = _remove_null_columns(entities, columns, labels)

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
        report_data.append(entity_line)
    print(tabulate(report_data, headers=labels, tablefmt="simple"))


def _remove_null_columns(
    entities: List[types.Entity], columns: List[str], labels: List[str]
) -> Tuple[List[str], List[str]]:
    """
    Function to remove the columns that have all None items.

    Returns the columns and labels without the unneeded elements.
    """

    for attribute in columns.copy():
        # If all entities have the None attribute value, remove the column from
        # the report.
        attribute_used = False
        for entity in entities:
            try:
                if getattr(entity, attribute) is not None:
                    attribute_used = True
            except AttributeError:
                continue

        if not attribute_used:
            index_to_remove = columns.index(attribute)
            columns.pop(index_to_remove)
            labels.pop(index_to_remove)
    return columns, labels


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

    columns = config.get("report.open.columns")
    labels = config.get("report.open.labels")

    if not isinstance(columns, list):
        raise ValueError("The columns configuration of the open report is not a list.")
    if not isinstance(labels, list):
        raise ValueError("The labels configuration of the open report is not a list.")

    # Convert task ids in short ids.
    short_ids = repo.fulid.sulids([task.id for task in tasks])
    for task in tasks:
        # The following line is required for the tags to be loaded in the report,
        # otherwise it appears as empty :S
        task.tags
        task.id = short_ids[task.id]

    _print_entities(config, tasks, columns, labels)
