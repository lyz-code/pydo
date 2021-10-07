"""Store the representations of the data."""

import re
from contextlib import suppress
from datetime import datetime
from enum import Enum
from operator import attrgetter
from typing import Dict, List, Optional, Tuple, TypeVar

from repository_orm import Repository

from . import config
from .exceptions import ConfigError
from .model.task import RecurrentTask, Task, TaskAttrs, TaskSelector
from .model.views import Colors, Report

EntityType = TypeVar("EntityType", Task, RecurrentTask)


def print_task_report(
    repo: Repository,
    config: config.Config,
    report_name: str,
    task_selector: Optional[TaskSelector] = None,
) -> None:
    """Gather the common tasks required to print several tasks."""
    if task_selector is None:
        task_selector = TaskSelector()

    # Initialize the Report
    (
        columns,
        labels,
        default_task_filter,
        sort_criteria,
    ) = _get_task_report_configuration(config, report_name)
    colors = Colors(**config.data["themes"][config.get("theme")])

    report = Report(labels=labels, colors=colors)

    # Complete the task_selector with the report task_filter
    task_selector.task_filter.update(default_task_filter)

    # Change the sorting of the report with the values of the task selector
    if task_selector.sort != []:
        sort_criteria = task_selector.sort

    with suppress(KeyError):
        if task_selector.task_filter["type"] == "recurrent_task":
            task_selector.model = RecurrentTask
        task_selector.task_filter.pop("type")

    # Fill up the report with the selected tasks
    tasks = repo.search(task_selector.task_filter, [task_selector.model])
    for task in sort_tasks(tasks, sort_criteria):
        entity_line = []
        for attribute in columns:
            value = getattr(task, attribute)
            if isinstance(value, list):
                value = ", ".join(value)
            elif isinstance(value, datetime):
                value = _date2str(config, value)
            elif isinstance(value, Enum):
                value = value.value.title()
            elif value is None:
                value = ""

            entity_line.append(value)
        report.add(entity_line)

    # Clean up the report and print it
    report._remove_null_columns()
    report.print()


def _get_task_report_configuration(
    config: config.Config,
    report_name: str,
) -> Tuple[List[str], List[str], TaskAttrs, List[str]]:
    """Retrieve a task report configuration from the config file."""
    columns = config.get(f"reports.task_reports.{report_name}.columns")
    available_labels = config.get("reports.task_attribute_labels")
    default_task_filter = config.get(f"reports.task_reports.{report_name}.filter")
    try:
        sort = config.get(f"reports.task_reports.{report_name}.sort")
    except ConfigError:
        # Sort by id_ by default
        sort = ["id_"]

    if not isinstance(columns, list):
        raise ValueError(
            f"The columns configuration of the {report_name} report is not a list."
        )
    if not isinstance(default_task_filter, dict):
        raise ValueError(
            f"The filter configuration of the {report_name} report is not a dictionary."
        )

    if not isinstance(available_labels, dict):
        raise ValueError("The labels configuration of the reports is not a dictionary.")

    if not isinstance(sort, list):
        raise ValueError(
            f"The sort configuration of the {report_name} report is not a list."
        )
    labels = [available_labels[task_attribute] for task_attribute in columns]

    return columns, labels, default_task_filter, sort


def sort_tasks(tasks: List[Task], sort_criteria: List[str]) -> List[Task]:
    """Sorts the tasks given the criteria.

    Args:
        tasks: List of tasks to sort
        sort_criteria: An ordered list of task attributes to use for sorting.
            If the attribute is prepended with a + it will be sort in increasing value,
            if it's prepended with a -, it will be sorted decreasingly.
    Returns:
        List of ordered tasks
    """
    for criteria in reversed(sort_criteria):
        if re.match("^-", criteria):
            reverse = True
            criteria = criteria[1:]
        elif re.match(r"^\+", criteria):
            reverse = False
            criteria = criteria[1:]
        else:
            reverse = False

        tasks.sort(key=attrgetter(criteria), reverse=reverse)
    return tasks


def _date2str(config: config.Config, date: datetime) -> str:
    """Convert a datetime object into a string.

    Using the format specified in the reports.date_format configuration.
    """
    date_format = str(config.get("reports.date_format"))

    return date.strftime(date_format)


def areas(repo: Repository) -> None:
    """Print the areas information."""
    report = Report(labels=["Name", "Open Tasks"])
    open_tasks = repo.search({"active": True}, [Task])

    # Gather areas
    areas: Dict[str, int] = {}
    for task in open_tasks:
        if task.area is None:
            area = "None"
        else:
            area = task.area

        areas.setdefault(area, 0)
        areas[area] += 1

    for area in sorted(areas.keys()):
        report.add([area, str(areas[area])])

    report.print()


def tags(repo: Repository) -> None:
    """Print the tags information."""
    report = Report(labels=["Name", "Open Tasks"])
    open_tasks = repo.search({"active": True}, [Task])

    # Gather tags
    tags: Dict[str, int] = {}
    for task in open_tasks:
        if len(task.tags) == 0:
            tags.setdefault("None", 0)
            tags["None"] += 1
        else:
            for tag in task.tags:
                tags.setdefault(tag, 0)
                tags[tag] += 1

    for tag in sorted(tags.keys()):
        report.add([tag, str(tags[tag])])

    report.print()
