"""
Module to store the classes and fixtures used throughout the tests.

Classes:
    FakeRepository: Implement the repository pattern using a memory dictionary.

Fixtures:
    Configuration Fixtures:
        sqlite_db: Create an SQLite database engine.
        session: Create an SQLite session.
        faker_seed: Make faker use a random seed when generating values.
        config: Configure the sqlite tests environment.
        repo: Configure a FakeRepository with the SQLite session.

    Insert Fixtures:
        Insert Fixtures in FakeRepository:
            insert_project: Insert a Project in the FakeRepository.
            insert_projects: Insert three Projects in the FakeRepository.

            insert_tag: Insert a Tag in the FakeRepository.
            insert_tags: Insert three Tags in the FakeRepository.

            insert_task: Insert a Task in the FakeRepository.
            insert_tasks: Insert three Tasks in the FakeRepository.
            insert_parent_task: Insert a RecurrentTask and it's children Task in the
                FakeRepository.

            insert_object: Insert an Entity in the FakeRepository.
            insert_objects: Insert three Entities in the FakeRepository.

        Insert Fixtures in SQL raw commands:
            insert_project_sql_: Insert a Project in the SQLAlchemyRepository using
                raw SQL.

            insert_tag_sql_: Insert a Tag in the SQLAlchemyRepository using
                raw SQL.

            insert_task_sql_: Insert a Task in the SQLAlchemyRepository using
                raw SQL.

            insert_object: Insert an Entity in the SQLAlchemyRepository using raw SQL.
            insert_objects:  Insert three Entities in the SQLAlchemyRepository using
                raw SQL.
"""

# pylint: disable=redefined-outer-name

import os
import random
import re
from shutil import copyfile
from typing import Any, Dict, List, Optional, Set, Tuple, Type

import pytest
from deepdiff import extract, grep
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from pydo import exceptions, types
from pydo.adapters import repository
from pydo.adapters.orm import metadata, start_mappers
from pydo.config import Config
from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import RecurrentTask, Task
from tests import factories


@pytest.fixture
def sqlite_db(tmpdir):
    """
    Fixture to create an SQLite database engine.
    """

    sqlite_file = str(tmpdir.join("sqlite.db"))
    engine = create_engine(f"sqlite:///{sqlite_file}")
    metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(sqlite_db):
    """
    Fixture to create an SQLite session.
    """

    clear_mappers()
    start_mappers()
    session = sessionmaker(bind=sqlite_db)()
    yield session
    clear_mappers()
    session.close()


@pytest.fixture()
def config(tmpdir):
    """
    Fixture to configure the sqlite tests environment.

    It returns a Config object and sets:
        * A temporal config file based on the default.
        * PYDO_CONFIG_PATH environmental variable pointing to the temporal config
            file.
    """

    config_file = str(tmpdir.join("config.yaml"))
    os.environ["PYDO_CONFIG_PATH"] = config_file
    copyfile("assets/config.yaml", config_file)

    config = Config(config_file)
    config.set("storage.sqlite.path", str(tmpdir.join("sqlite.db")))
    config.save()

    yield config


@pytest.fixture(scope="session", autouse=True)
def faker_seed():
    """
    Fixture to make faker use a random seed when generating values.

    There is no need to add it anywhere, the faker fixture uses it.
    """

    return random.randint(0, 999999)


class FakeRepository(repository.AbstractRepository):
    """
    Class to implement the repository pattern using a memory dictionary.

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

    Internal Methods:
        _get_object: Return an entity given it's ID and type.
        _select_table: Return the list of objects matching an object model type.
        _populate_children: Populate the children task attribute.
        _populate_parent: Populate the parent task attribute.

    """

    def __init__(self, config: Config, session: Any) -> None:
        super().__init__(config, session)
        self._project: Set[Project] = set()
        self._tag: Set[Tag] = set()
        self._task: Set[Task] = set()

    def add(self, entity: types.Entity):
        """
        Method to append an entity to the repository.
        """

        if isinstance(entity, Project):
            self._project.add(entity)
        elif isinstance(entity, Tag):
            self._tag.add(entity)
        elif isinstance(entity, Task):
            if entity.project_id is not None:
                project = self.get(Project, entity.project_id)
                project.tasks.append(entity)
                project.tasks = list(set(project.tasks))
                self._project.add(project)
                entity.project = project
            else:
                entity.project = None
            if entity.tag_ids is not None:
                for tag_id in entity.tag_ids:
                    tag = self.get(Tag, tag_id)
                    tag.tasks.append(entity)
                    tag.tasks = list(set(tag.tasks))
                    self._tag.add(tag)
                    entity.tags.append(tag)
            self._task.add(entity)

    def apply_migrations(self) -> None:
        """
        Method to run the migrations of the repository schema.
        """

        pass

    def _get_object(self, id: str, entities: List[types.Entity]):
        """
        Method to return an entity given it's ID and type.
        """

        try:
            return next(entity for entity in entities if entity.id == id)
        except StopIteration:
            return None

    def _select_table(self, entity_model: Type[types.Entity]) -> List[types.Entity]:
        """
        Method to return the list of objects matching an object model type.
        """
        # I need a better way to extract the type. The problem is that as the
        # objects are not instiated type(entity_model) == abc.ABC.

        if re.match(r"<class 'pydo.model.project.*", str(entity_model)):
            return list(self._project)  # type: ignore
        elif re.match(r"<class 'pydo.model.tag.*", str(entity_model)):
            return list(self._tag)  # type: ignore
        elif re.match(r"<class 'pydo.model.task.*", str(entity_model)):
            return list(self._task)  # type: ignore
        else:
            raise NotImplementedError

    def _populate_children(self, parent_task: Task) -> None:
        """
        Method to populate the children task attribute.
        """

        parent_task.children = self.search(Task, "parent_id", parent_task.id)

    def _populate_parent(self, child_task: Task) -> None:
        """
        Method to populate the parent task attribute.
        """

        if child_task.parent_id is None:
            raise ValueError("trying to load a parent task of an orphan child")

        parent = self.get(Task, child_task.parent_id)

        if isinstance(parent, Task):
            child_task.parent = parent
        else:
            raise TypeError("trying to load wrong object as a parent task")

    def get(self, entity_model: Type[types.Entity], entity_id: str) -> types.Entity:
        """
        Method to obtain an entity from the repository by it's ID.
        """

        if entity_model == Task:
            entity_id = self.short_id_to_id(entity_id, entity_model)

        entity = self._get_object(entity_id, self._select_table(entity_model))

        if entity is None:
            raise exceptions.EntityNotFoundError(
                f"No {self.entity_model_to_str(entity_model)} found with id {entity_id}"
            )

        try:
            if entity.type == "recurrent_task":
                self._populate_children(entity)
            elif entity.parent_id is not None:
                self._populate_parent(entity)
        except AttributeError:
            pass

        return entity

    def all(self, entity_model: Type[types.Entity]) -> List[types.Entity]:
        """
        Method to obtain all the entities of a type from the repository.
        """

        return sorted(list(self._select_table(entity_model)))

    def commit(self) -> None:
        """
        Method to persist the changes into the repository.
        """

        # They are saved when adding them, if we want to mimic the behaviour of the
        # other repositories, we should save the objects in a temporal list and move
        # them to the real set when using this method.
        pass

    def msearch(
        self, entity_model: Type[types.Entity], fields: Dict
    ) -> List[types.Entity]:
        """
        Method to obtain the entities whose attributes match several conditions.

        fields is a dictionary with the `key`:`value` to search.

        It assumes that the attributes of the entities are str.

        If None is found an EntityNotFoundError is raised.
        """

        all_entities = self.all(entity_model)
        entities_dict = {entity.id: entity for entity in all_entities}
        entity_attributes = {
            entity.id: entity._get_attributes() for entity in all_entities
        }

        for key, value in fields.items():
            # Get entities that have the value `value`
            entities_with_value = entity_attributes | grep(value)
            matching_entity_attributes = {}

            try:
                entities_with_value["matched_values"]
            except KeyError:
                raise exceptions.EntityNotFoundError(
                    f"There are no {self.entity_model_to_str(entity_model)}s "
                    "that match the task filter"
                )

            for path in entities_with_value["matched_values"]:
                entity_id = re.sub(r"root\['(.*)'\]\[.*", r"\1", path)
                # Add the entity to the matching ones only if the value is of the
                # attribute `key`.
                if re.match(re.compile(fr"root\['{entity_id}'\]\['{key}'\]"), path):
                    matching_entity_attributes[entity_id] = extract(
                        entity_attributes, f"root[{entity_id}]"
                    )

            entity_attributes = matching_entity_attributes
        entities = [entities_dict[key] for key in entity_attributes.keys()]

        if len(entities) == 0:
            raise exceptions.EntityNotFoundError(
                f"There are no {self.entity_model_to_str(entity_model)}s "
                "that match the task filter"
            )
        else:
            return entities

    def search(
        self, entity_model: Type[types.Entity], field: str, value: str
    ) -> Optional[List[types.Entity]]:
        """
        Method to obtain the entities whose attribute match a condition.
        """

        result = []
        try:
            for entity in self._select_table(entity_model):
                field_value = getattr(entity, field)
                if field_value is not None and re.match(value, field_value):
                    result.append(entity)
            result = sorted(result)
        except AttributeError:
            return None

        if len(result) == 0:
            return None
        else:
            return result


@pytest.fixture()
def repo(config):
    """
    Fixture to configure a FakeRepository with the SQLite session.
    """

    return FakeRepository(config, session)


@pytest.fixture()
def insert_task(repo):
    """
    Fixture to insert a Task in the FakeRepository.
    """

    task = factories.TaskFactory.create(state="open")
    repo.add(task)
    repo.commit()

    return task


@pytest.fixture()
def insert_tasks(repo):
    """
    Fixture to insert three Tasks in the FakeRepository.
    """

    tasks = sorted(factories.TaskFactory.create_batch(3, state="open"))
    [repo.add(task) for task in tasks]
    repo.commit()

    return tasks


@pytest.fixture()
def insert_parent_task(
    repo: repository.AbstractRepository,
) -> Tuple[RecurrentTask, Task]:
    """
    Fixture to insert a RecurrentTask and it's children Task in the FakeRepository.
    """

    parent_task = factories.RecurrentTaskFactory.create(state="open")
    child_task = parent_task.breed_children(factories.create_fulid())

    parent_task.children = [child_task]
    child_task.parent = parent_task

    repo.add(parent_task)
    repo.add(child_task)
    repo.commit()

    return parent_task, child_task


@pytest.fixture()
def insert_tag(repo):
    """
    Fixture to insert a Tag in the FakeRepository.
    """

    tag = factories.TagFactory.create()
    repo.add(tag)
    repo.commit()

    return tag


@pytest.fixture()
def insert_tags(repo):
    """
    Fixture to insert three Tags in the FakeRepository.
    """

    tags = factories.TagFactory.create_batch(3)
    [repo.add(tag) for tag in tags]
    repo.commit()

    return tags


@pytest.fixture()
def insert_project(repo):
    """
    Fixture to insert a Project in the FakeRepository.
    """

    project = factories.ProjectFactory.create()
    repo.add(project)
    repo.commit()

    return project


@pytest.fixture()
def insert_projects(repo):
    """
    Fixture to insert three Projects in the FakeRepository.
    """

    projects = factories.ProjectFactory.create_batch(3)
    [repo.add(project) for project in projects]
    repo.commit()

    return projects


@pytest.fixture
def insert_object(request, insert_task, insert_tag, insert_project):
    """
    Fixture to insert an Entity in the FakeRepository.
    """

    if request.param == "insert_task":
        return insert_task
    elif request.param == "insert_project":
        return insert_project
    elif request.param == "insert_tag":
        return insert_tag


@pytest.fixture
def insert_objects(request, insert_tasks, insert_tags, insert_projects):
    """
    Fixture to insert three Entities in the FakeRepository.
    """

    if request.param == "insert_task":
        return insert_tasks
    elif request.param == "insert_project":
        return insert_projects
    elif request.param == "insert_tag":
        return insert_tags


@pytest.fixture(name="insert_task_sql")
def insert_task_sql_(session):
    """
    Fixture to insert a Task in the SQLAlchemyRepository using raw SQL.

    It returns a generator, so it can be used more than once in a test.
    """

    def insert_task_sql(session):
        task = factories.TaskFactory.create(state="open")

        session.execute(
            "INSERT INTO task (id, description, state, type)"
            "VALUES ("
            f'"{task.id}", "{task.description}", "{task.state}", "task"'
            ")"
        )

        return task

    yield insert_task_sql


@pytest.fixture(name="insert_project_sql")
def insert_project_sql_(session):
    """
    Fixture to insert a Project in the SQLAlchemyRepository using raw SQL.

    It returns a generator, so it can be used more than once in a test.
    """

    def insert_project_sql(session):
        project = factories.ProjectFactory.create(state="open")

        session.execute(
            "INSERT INTO project (id, description, state)"
            f'VALUES ("{project.id}", "{project.description}", "{project.state}")'
        )

        return project

    yield insert_project_sql


@pytest.fixture(name="insert_tag_sql")
def insert_tag_sql_(session):
    """
    Fixture to insert a Tag in the SQLAlchemyRepository using raw SQL.

    It returns a generator, so it can be used more than once in a test.
    """

    def insert_tag_sql(session):
        tag = factories.TagFactory.create(state="open")

        session.execute(
            f'INSERT INTO tag (id, description, state) VALUES ("{tag.id}",'
            f' "{tag.description}", "{tag.state}")'
        )

        return tag

    return insert_tag_sql


@pytest.fixture
def insert_object_sql(
    request, session, insert_task_sql, insert_tag_sql, insert_project_sql
):
    """
    Fixture to insert an Entity in the SQLAlchemyRepository using raw SQL.

    It returns the generated entity.
    """

    if request.param == "insert_task_sql":
        return insert_task_sql(session)
    elif request.param == "insert_project_sql":
        return insert_project_sql(session)
    elif request.param == "insert_tag_sql":
        return insert_tag_sql(session)


@pytest.fixture
def insert_objects_sql(
    request, session, insert_task_sql, insert_tag_sql, insert_project_sql
):
    """
    Fixture to insert three Entities in the SQLAlchemyRepository using raw SQL.

    It returns the generated entity.
    """

    if request.param == "insert_task_sql":
        return [
            insert_task_sql(session),
            insert_task_sql(session),
            insert_task_sql(session),
        ]
    elif request.param == "insert_project_sql":
        return [
            insert_project_sql(session),
            insert_project_sql(session),
            insert_project_sql(session),
        ]
    elif request.param == "insert_tag_sql":
        return [
            insert_tag_sql(session),
            insert_tag_sql(session),
            insert_tag_sql(session),
        ]
