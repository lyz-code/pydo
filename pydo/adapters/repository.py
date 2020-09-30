"""
Module to store the storage repository abstractions.

Abstract Classes:
    AbstractRepository: Gathers common methods and define the interface of the
        repositories.

Classes:
    SqlAlchemyRepository: Implement the repository pattern using the SQLAlchemy ORM.

References:
* https://lyz-code.github.io/blue-book/architecture/repository_pattern/
"""

import abc
import logging
import re
import time
from typing import Any, Dict, List, Type, Union

import alembic.command
from alembic.config import Config as AlembicConfig

from pydo import exceptions, fulids, types
from pydo.config import Config
from pydo.model.tag import Tag
from pydo.model.task import Task

log = logging.getLogger(__name__)


class AbstractRepository(abc.ABC):
    """
    Abstract class to gathers common methods and define the interface of the
    repositories.

    Properties:
        fulid: A configured entity id generator.

    Abstract Methods:
        add: Append an entity to the repository.
        all: Obtain all the entities of a type from the repository.
        apply_migrations: Run the migrations of the repository schema.
        commit: Persist the changes into the repository.
        get: Obtain an entity from the repository by it's ID.
        msearch: Obtain the entities whose attributes match several conditions.
        search: Obtain the entities whose attribute match a condition.

    Methods:
        create_next_id: Create the next entity's ID.
        entity_model_to_str: Obtain a nice string from an entity model.
        short_id_to_id: Convert a shortened ID into the complete one.
    """

    @abc.abstractmethod
    def __init__(self, config: Config, session: Any) -> None:
        self.config = config
        self.session = session

    @property
    def fulid(self):
        """
        Property to hold a configured entity id generator.

        It uses the fulid format.
        """

        return fulids.fulid(
            self.config.get("fulid.characters"),
            self.config.get("fulid.forbidden_characters"),
        )

    @abc.abstractmethod
    def add(self, entity: types.Entity) -> None:
        """
        Method to append an entity to the repository.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def apply_migrations(self) -> None:
        """
        Method to run the migrations of the repository schema.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def get(self, entity_model: Type[types.Entity], entity_id: str) -> types.Entity:
        """
        Method to obtain an entity from the repository by it's ID.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def all(self, entity_model: Type[types.Entity]) -> List[types.Entity]:
        """
        Method to obtain all the entities of a type from the repository.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def commit(self) -> None:
        """
        Method to persist the changes into the repository.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def msearch(
        self, entity_model: Type[types.Entity], fields: Dict
    ) -> List[types.Entity]:
        """
        Method to obtain the entities whose attributes match several conditions.

        fields is a dictionary with the {key}:{value} to search.

        If None is found an EntityNotFoundError is raised.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def search(
        self, entity_model: Type[types.Entity], field: str, value: str
    ) -> Union[List[types.Entity], None]:
        """
        Method to obtain the entities whose attribute match a condition.
        """

        raise NotImplementedError

    def create_next_id(self, entity_model: Type[types.Entity]) -> str:
        """
        Method to create the next entity's ID.
        """

        matching_entities = self.search(entity_model, "state", "open")

        if matching_entities is None:
            last_id = None
        else:
            last_entity = max(matching_entities)
            last_id = last_entity.id
        log.debug(f"Last entity id: {str(last_id)}")

        # Required to ensure the sortability of the fulids as their precision goes
        # down to the 0.001s
        time.sleep(0.01)

        return self.fulid.new(last_id).str

    def short_id_to_id(
        self, short_id: str, entity_model: Type[types.Entity], state: str = "open"
    ) -> str:
        """
        Method to convert a shortened ID into the complete one.
        """

        if len(short_id) < 10:
            matching_entities = self.search(entity_model, "state", state)
            if matching_entities is None:
                raise exceptions.EntityNotFoundError(
                    f"There are no {state} {self.entity_model_to_str(entity_model)}s"
                )

            entity_ids = [entity.id for entity in matching_entities]
            try:
                entity_id = self.fulid.sulid_to_fulid(short_id, entity_ids)
            except KeyError:
                raise exceptions.EntityNotFoundError(
                    f"There is no {state} {self.entity_model_to_str(entity_model)} with"
                    f" short_id {short_id}"
                )
        else:
            entity_id = short_id

        return entity_id

    def entity_model_to_str(self, entity_model: Type[types.Entity]) -> str:
        """
        Method to obtain a nice string from an entity model
        """
        return re.sub(r".*\.(.*)'>", r"\1", str(entity_model))


class SqlAlchemyRepository(AbstractRepository):
    """
    Class to implement the repository pattern using the SQLAlchemy ORM.

    Properties:
        fulid: A configured entity id generator.

    Abstract Methods:
        add: Append an entity to the repository.
        all: Obtain all the entities of a type from the repository.
        apply_migrations: Run the migrations of the repository schema.
        commit: Persist the changes into the repository.
        get: Obtain an entity from the repository by it's ID.
        search: Obtain the entities whose attribute match a condition.

    Methods:
        create_next_id: Create the next entity's ID.
        entity_model_to_str: Obtain a nice string from an entity model.
        short_id_to_id: Convert a shortened ID into the complete one.
    """

    def __init__(self, config: Config, session: Any) -> None:
        super().__init__(config, session)

    def add(self, entity: types.Entity) -> None:
        """
        Method to append an entity to the repository.
        """
        try:
            if isinstance(entity, Task) and len(entity.tag_ids) > 0:
                entity.tags = [self.get(Tag, tag_id) for tag_id in entity.tag_ids]
        except AttributeError:
            pass

        self.session.add(entity)

    def apply_migrations(self) -> None:
        """
        Method to run the migrations of the repository schema.
        """

        log.debug("Running Database Migrations")
        alembic_config = AlembicConfig("pydo/migrations/alembic.ini")
        alembic_config.attributes["configure_logger"] = False
        alembic.command.upgrade(alembic_config, "head")

    def get(self, entity_model: Type[types.Entity], entity_id: str) -> types.Entity:
        """
        Method to obtain an entity from the repository by it's ID.
        """

        if entity_model == Task:
            entity_id = self.short_id_to_id(entity_id, entity_model)
        entity = self.session.query(entity_model).get(entity_id)
        if entity is None:
            raise exceptions.EntityNotFoundError(
                f"No {self.entity_model_to_str(entity_model)} found with id {entity_id}"
            )

        return entity

    def all(self, entity_model: Type[types.Entity]) -> List[types.Entity]:
        """
        Method to obtain all the entities of a type from the repository.
        """

        return self.session.query(entity_model).all()

    def commit(self) -> None:
        """
        Method to persist the changes into the repository.
        """

        self.session.commit()

    def msearch(
        self, entity_model: Type[types.Entity], fields: Dict
    ) -> List[types.Entity]:
        """
        Method to obtain the entities whose attributes match several conditions.

        fields is a dictionary with the {key}:{value} to search.

        If None is found an EntityNotFoundError is raised.
        """

        query = self.session.query(entity_model)
        try:
            for key, value in fields.items():
                query = query.filter(getattr(entity_model, key).like(f"%{value}"))
        except AttributeError:
            raise exceptions.EntityNotFoundError(
                f"There are no {self.entity_model_to_str(entity_model)}s "
                "that match the task filter"
            )

        result = query.all()

        if len(result) == 0:
            raise exceptions.EntityNotFoundError(
                f"There are no {self.entity_model_to_str(entity_model)}s "
                "that match the task filter"
            )
        else:
            return result

    def search(
        self, entity_model: Type[types.Entity], field: str, value: str
    ) -> Union[List[types.Entity], None]:
        """
        Method to obtain the entities whose attribute match a condition.
        """

        try:
            result = (
                self.session.query(entity_model)
                .filter(getattr(entity_model, field).like(f"%{value}"))
                .all()
            )
        except AttributeError:
            return None

        if len(result) == 0:
            return None
        else:
            return result
