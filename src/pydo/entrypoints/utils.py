"""Define common entrypoint functions."""

import logging
import re
import sys
from contextlib import suppress
from typing import Any, Iterable, Tuple

from repository_orm import Repository, load_repository

from ..config import Config
from ..exceptions import ConfigError, DateParseError
from ..model import RecurrentTask, Task, TaskChanges, TaskSelector, convert_date

log = logging.getLogger(__name__)


def load_config(config_path: str) -> Config:
    """Load the configuration from the file."""
    log.debug(f"Loading the configuration from file {config_path}")
    try:
        config = Config(config_path)
    except ConfigError as error:
        log.error(
            f"Error parsing yaml of configuration file {config_path}: {str(error)}"
        )
        sys.exit(1)

    return config


def get_repo(config: Config) -> Repository:
    """Configure the Repository."""
    log.debug("Initializing the repository")
    repo = load_repository([Task, RecurrentTask], config["database_url"])

    return repo


# I have no idea how to test this function :(. If you do, please send a PR.
def load_logger(verbose: bool = False) -> None:  # pragma no cover
    """Configure the Logging logger.

    Args:
        verbose: Set the logging level to Debug.
    """
    logging.addLevelName(logging.INFO, "[\033[36m+\033[0m]")
    logging.addLevelName(logging.ERROR, "[\033[31m+\033[0m]")
    logging.addLevelName(logging.DEBUG, "[\033[32m+\033[0m]")
    logging.addLevelName(logging.WARNING, "[\033[33m+\033[0m]")
    if verbose:
        logging.basicConfig(
            stream=sys.stderr, level=logging.DEBUG, format="  %(levelname)s %(message)s"
        )
    else:
        logging.basicConfig(
            stream=sys.stderr, level=logging.INFO, format="  %(levelname)s %(message)s"
        )


def _parse_task_selector(task_args: Iterable[str]) -> TaskSelector:
    """Parse the task ids and task filter from the task cli arguments."""
    selector = TaskSelector()

    for arg in task_args:
        attribute_id, attribute_value = _parse_task_argument(arg)
        if attribute_id == "unprocessed":
            with suppress(ValueError):
                selector.task_ids.append(int(arg))
        elif attribute_id == "sort":
            selector.sort = attribute_value
        elif attribute_id not in ["tag_ids", "tags_rm", "recurring", "repeating"]:
            selector.task_filter[attribute_id] = attribute_value

    return selector


def _parse_changes(task_args: Iterable[str]) -> TaskChanges:
    """Parse the changes to take from a friendly task attributes string.

    Args:
        task_args: command line friendly task attributes representation.

    Returns:
        Changes on the task attributes.
    """
    changes = TaskChanges()

    unprocessed_args = []

    for task_arg in task_args:
        attribute_id, attribute_value = _parse_task_argument(task_arg)
        if attribute_id == "tag_ids":
            changes.tags_to_add.append(attribute_value)
        elif attribute_id == "tags_rm":
            changes.tags_to_remove.append(attribute_value)
        elif attribute_id == "unprocessed":
            unprocessed_args.append(attribute_value)
        elif attribute_id in ["recurring", "repeating"]:
            changes.task_attributes["recurrence"] = attribute_value
            changes.task_attributes["recurrence_type"] = attribute_id
        else:
            changes.task_attributes[attribute_id] = attribute_value

    if len(unprocessed_args) > 0:
        changes.task_attributes["description"] = " ".join(unprocessed_args)

    return changes


def _parse_task_argument(task_arg: str) -> Tuple[str, Any]:
    """Parse the Task attributes from a friendly task attribute string.

    If the key doesn't match any of the known keys, it will be returned with the key
    "unprocessed".

    Returns:
        attribute_id: Attribute key.
        attributes_value: Attribute value.
    """
    attribute_conf = {
        "body": {"regexp": re.compile(r"^body:"), "type": "str"},
        "due": {"regexp": re.compile(r"^due:"), "type": "date"},
        "estimate": {"regexp": re.compile(r"^(est|estimate):"), "type": "float"},
        "fun": {"regexp": re.compile(r"^fun:"), "type": "int"},
        "priority": {"regexp": re.compile(r"^(pri|priority):"), "type": "int"},
        "area": {"regexp": re.compile(r"^(ar|area):"), "type": "str"},
        "recurring": {"regexp": re.compile(r"^(rec|recurring):"), "type": "str"},
        "repeating": {"regexp": re.compile(r"^(rep|repeating):"), "type": "str"},
        "sort": {"regexp": re.compile(r"^(sort):"), "type": "sort"},
        "state": {"regexp": re.compile(r"^(st|state):"), "type": "str"},
        "tag_ids": {"regexp": re.compile(r"^\+"), "type": "tag"},
        "tags_rm": {"regexp": re.compile(r"^\-"), "type": "tag"},
        "type": {"regexp": re.compile(r"^type:"), "type": "model"},
        "value": {"regexp": re.compile(r"^(vl|value):"), "type": "int"},
        "willpower": {"regexp": re.compile(r"^(wp|willpower):"), "type": "int"},
    }
    attribute_value: Any = "initial_internal_value"

    for attribute_id, attribute in attribute_conf.items():
        if attribute["regexp"].match(task_arg):  # type: ignore
            if attribute["type"] == "tag":
                attribute_value = re.sub(r"^[+-]", "", task_arg)
            elif task_arg.split(":")[1] == "":
                attribute_value = None
            elif attribute["type"] == "str":
                attribute_value = task_arg.split(":")[1]
            elif attribute["type"] == "int":
                attribute_value = int(task_arg.split(":")[1])
            elif attribute["type"] == "float":
                attribute_value = float(task_arg.split(":")[1])
            elif attribute["type"] == "date":
                try:
                    attribute_value = convert_date(":".join(task_arg.split(":")[1:]))
                except DateParseError as error:
                    log.error(str(error))
                    sys.exit(1)
            elif attribute["type"] == "sort":
                attribute_value = task_arg.split(":")[1].split(",")
        if attribute_value != "initial_internal_value":
            return attribute_id, attribute_value
    return "unprocessed", task_arg
