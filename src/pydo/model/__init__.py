"""Module to store the common business model of all entities.

Abstract Classes:
    Entity: Gathers common methods and define the interface of the entities.
"""

from typing import TypeVar

from repository_orm import Entity

from .date import convert_date
from .task import (
    RecurrentTask,
    Task,
    TaskAttrs,
    TaskChanges,
    TaskSelector,
    TaskState,
    TaskType,
)

EntityType = TypeVar("EntityType", bound=Entity)

__all__ = [
    "convert_date",
    "EntityType",
    "RecurrentTask",
    "Sulid",
    "Task",
    "TaskAttrs",
    "TaskChanges",
    "TaskSelector",
    "TaskType",
    "TaskState",
]
