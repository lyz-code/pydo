"""Store the classes and fixtures used throughout the tests."""

from random import SystemRandom
from shutil import copyfile
from typing import List, Tuple

import pytest
from _pytest.tmpdir import TempdirFactory
from repository_orm import FakeRepository, Repository, load_repository
from tests import factories

from pydo.config import Config
from pydo.model.task import RecurrentTask, Task


@pytest.fixture(name="config")
def fixture_config(tmpdir_factory: TempdirFactory) -> Config:
    """Configure the Config object for the tests."""
    data = tmpdir_factory.mktemp("data")
    config_file = str(data.join("config.yaml"))
    copyfile("tests/assets/config.yaml", config_file)
    config = Config(config_file)
    config["database_url"] = f"tinydb://{data}/database.tinydb"
    config.save()

    return config


@pytest.fixture(scope="session", autouse=True)
def faker_seed() -> int:
    """Make faker use a random seed when generating values.

    There is no need to add it anywhere, the faker fixture uses it.
    """
    return SystemRandom().randint(0, 999999)


@pytest.fixture(name="repo")
def repo_() -> FakeRepository:
    """Configure a FakeRepository instance."""
    return FakeRepository([Task, RecurrentTask])


@pytest.fixture(name="task")
def task_(repo: Repository) -> Task:
    """Insert a Task in the FakeRepository."""
    task = factories.TaskFactory.create(state="backlog")
    repo.add(task)
    repo.commit()

    return task


@pytest.fixture(name="tasks")
def tasks_(repo: Repository) -> List[Task]:
    """Insert three Tasks in the FakeRepository."""
    tasks = sorted(factories.TaskFactory.create_batch(3, state="backlog"))
    for task in tasks:
        repo.add(task)
    repo.commit()

    return tasks


@pytest.fixture(name="parent_and_child_tasks")
def parent_and_child_tasks_(
    repo: Repository,
) -> Tuple[RecurrentTask, Task]:
    """Insert a RecurrentTask and it's children Task in the FakeRepository."""
    parent_task = factories.RecurrentTaskFactory.create(state="backlog")
    child_task = parent_task.breed_children()

    repo.add(parent_task)
    repo.add(child_task)
    repo.commit()

    return parent_task, child_task


@pytest.fixture()
def insert_parent_task(
    repo: Repository,
) -> Tuple[RecurrentTask, Task]:
    """Insert a RecurrentTask and it's children Task in the FakeRepository."""
    parent_task = factories.RecurrentTaskFactory.create(state="backlog")
    child_task = parent_task.breed_children()

    repo.add(parent_task)
    repo.add(child_task)
    repo.commit()

    return parent_task, child_task


@pytest.fixture()
def insert_parent_tasks(
    repo: Repository,
) -> Tuple[List[RecurrentTask], List[Task]]:
    """Insert a RecurrentTask and it's children Task in the FakeRepository."""
    parent_tasks = factories.RecurrentTaskFactory.create_batch(3, state="backlog")
    child_tasks = []

    for parent_task in parent_tasks:
        child_task = parent_task.breed_children()
        parent_task.children = [child_task]
        child_task.parent = parent_task
        repo.add(parent_task)
        repo.add(child_task)

        child_tasks.append(child_task)

    repo.commit()

    return parent_tasks, child_tasks


@pytest.fixture()
def insert_multiple_tasks(repo: Repository) -> List[Task]:
    """Insert three Tasks in the repository."""
    tasks = sorted(factories.TaskFactory.create_batch(20, state="backlog"))
    [repo.add(task) for task in tasks]
    repo.commit()

    return tasks


@pytest.fixture()
def repo_e2e(config: Config) -> Repository:
    """Configure the end to end repository."""
    return load_repository([Task, RecurrentTask], config["database_url"])


@pytest.fixture()
def insert_task_e2e(repo_e2e: Repository) -> Task:
    """Insert a task in the end to end repository."""
    task = factories.TaskFactory.create(state="backlog")
    repo_e2e.add(task)
    repo_e2e.commit()
    return task


@pytest.fixture()
def insert_tasks_e2e(repo_e2e: Repository) -> List[Task]:
    """Insert many tasks in the end to end repository."""
    tasks = factories.TaskFactory.create_batch(3, priority=3, state="backlog")
    different_task = factories.TaskFactory.create(priority=2, state="backlog")
    tasks.append(different_task)

    for task in tasks:
        repo_e2e.add(task)
        repo_e2e.commit()

    return tasks


@pytest.fixture()
def insert_parent_task_e2e(repo_e2e: Repository) -> Tuple[RecurrentTask, Task]:
    """Insert a RecurrentTask and it's children Task in the repository."""
    parent_task = factories.RecurrentTaskFactory.create(state="backlog")
    child_task = parent_task.breed_children()

    repo_e2e.add(parent_task)
    repo_e2e.add(child_task)
    repo_e2e.commit()

    return parent_task, child_task


@pytest.fixture()
def insert_parent_tasks_e2e(
    repo_e2e: Repository,
) -> Tuple[List[RecurrentTask], List[Task]]:
    """Insert a RecurrentTask and it's children Task in the repository."""
    parent_tasks = factories.RecurrentTaskFactory.create_batch(3, state="backlog")
    child_tasks = [parent_task.breed_children() for parent_task in parent_tasks]

    [repo_e2e.add(parent_task) for parent_task in parent_tasks]
    [repo_e2e.add(child_task) for child_task in child_tasks]
    repo_e2e.commit()

    return parent_tasks, child_tasks


@pytest.fixture()
def insert_frozen_parent_task_e2e(repo_e2e: Repository) -> RecurrentTask:
    """Insert a RecurrentTask in frozen state."""
    parent_task = factories.RecurrentTaskFactory.create(state="backlog")
    parent_task.freeze()
    repo_e2e.add(parent_task)
    repo_e2e.commit()

    return parent_task


@pytest.fixture()
def insert_frozen_parent_tasks_e2e(repo_e2e: Repository) -> List[RecurrentTask]:
    """Insert many RecurrentTask in frozen state."""
    parent_tasks = factories.RecurrentTaskFactory.create_batch(3, state="backlog")
    for parent_task in parent_tasks:
        parent_task.freeze()
        repo_e2e.add(parent_task)
    repo_e2e.commit()

    return parent_tasks
