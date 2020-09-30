"""
Module to store the business model of the project entities.

Classes:
    Project: Entity used to hierarchically organize the tasks.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydo.model import Entity

if TYPE_CHECKING:
    from pydo.model.task import Task


class Project(Entity):
    """
    Class to define the project model, used to hierarchically organize the tasks.

    Attributes:
        id: Entity identifier.
        description: Short definition of the entity.
        state: Categorizes and defines the actions that can be executed over the
            entity. One of ['open', 'completed', 'deleted', 'frozen']

    Properties:
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
        state: Optional[str] = "open",
        closed: Optional[datetime] = None,
        created: Optional[datetime] = None,
    ):
        super().__init__(id, description, state, created, closed)
        self.tasks: List["Task"] = []

    def __eq__(self, other) -> bool:
        """
        Internal Python method to assess the equally between class objects.
        """

        if not isinstance(other, Project):
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

    def __repr__(self) -> str:
        """
        Internal Python method to show when printing the object.
        """

        return f"<Project {self.id}>"

    def __str__(self) -> str:
        """
        Internal Python method to show when printing the object.
        """

        return f"<Project {self.id}>"
