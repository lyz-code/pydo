"""Tests the service layer."""

import logging
from datetime import datetime
from typing import Callable, List, Tuple

import pytest
from _pytest.logging import LogCaptureFixture
from faker import Faker
from freezegun.api import FrozenDateTimeFactory
from repository_orm import EntityNotFoundError, FakeRepository, Repository

from pydo import services
from pydo.model.task import RecurrentTask, Task, TaskChanges, TaskSelector, TaskState

from ..factories import RecurrentTaskFactory


class TestTaskAdd:
    """Test the implementation of addition of tasks."""

    def test_add_can_create_simple_task(
        self,
        repo: FakeRepository,
        faker: Faker,
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: Some desired task attributes for a simple task.
        When: using the add_task service.
        Then: The task is added to the repository.
        """
        now = datetime.now()
        description = faker.sentence()
        change = TaskChanges(task_attributes={"description": description})

        result = services.add_task(repo, change)

        # Ensure that the object is in the repository
        task = repo.get(result.id_, [Task])
        assert task.description == description
        assert task.state == "backlog"
        assert (task.created - now).total_seconds() < 1
        assert (task.modified - now).total_seconds() < 1
        assert task.closed is None
        assert task.area is None
        assert (
            "pydo.services",
            logging.INFO,
            f"Added task {task.id_}: {task.description}",
        ) in caplog.record_tuples

    def test_add_assigns_tags(self, repo: FakeRepository, faker: Faker) -> None:
        """
        Given: Nothing.
        When: Creating a task with a tag.
        Then: The tags attribute is set.
        """
        description = faker.sentence()
        tag = faker.word()
        change = TaskChanges(
            task_attributes={"description": description}, tags_to_add=[tag]
        )

        result = services.add_task(repo, change)

        assert result.tags == [tag]

    @pytest.mark.parametrize("recurrence_type", ["recurring", "repeating"])
    def test_add_generates_recurrent_tasks(
        self,
        repo: FakeRepository,
        faker: Faker,
        caplog: LogCaptureFixture,
        recurrence_type: str,
    ) -> None:
        """
        Given: Some desired task attributes for a recurrent or repeating task.
        When: using the add_task service.
        Then: Both parent and child tasks are added to the repository.
        """
        task_attributes = {
            "description": faker.sentence(),
            "due": faker.date_time(),
            "recurrence": "1d",
            "recurrence_type": recurrence_type,
            "state": "todo",
        }

        result = services.add_task(repo, TaskChanges(task_attributes=task_attributes))

        assert isinstance(result, RecurrentTask)
        parent_task = repo.get(result.id_, [RecurrentTask])
        child_task = repo.search({"parent_id": parent_task.id_}, [Task])[0]
        # Assert the id of the child is sequential with the parent's
        assert child_task.parent_id == parent_task.id_
        assert child_task.state == "todo"
        assert child_task.due >= task_attributes["due"]
        assert parent_task.recurrence == task_attributes["recurrence"]
        assert parent_task.recurrence_type == task_attributes["recurrence_type"]
        assert parent_task.due == task_attributes["due"]
        assert (
            "pydo.services",
            logging.INFO,
            f"Added {parent_task.recurrence_type} task {parent_task.id_}:"
            f" {parent_task.description}",
        ) in caplog.record_tuples
        assert (
            "pydo.services",
            logging.INFO,
            f"Added first child task with id {child_task.id_}",
        ) in caplog.record_tuples


@pytest.mark.parametrize(
    ("action", "state"),
    [(services.do_tasks, "done"), (services.rm_tasks, "deleted")],
)
class TestTaskDoAndDel:
    """Test the closing of tasks."""

    def test_close_task_sets_state_and_close_date(
        self,
        action: Callable[[FakeRepository, TaskSelector], None],
        state: str,
        repo: FakeRepository,
        task: Task,
        freezer: FrozenDateTimeFactory,  # noqa: W0613
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: An existent task.
        When: using the do_tasks or rm_tasks.
        Then: The task is closed with the respective state and the closed date is set.
        """
        selector = TaskSelector(task_ids=[task.id_])
        now = datetime.now()

        action(repo, selector)  # act

        task = repo.get(task.id_, [Task])
        assert task.closed == now
        assert task.modified == now
        assert task.state == state
        assert (
            "pydo.services",
            logging.INFO,
            f"Closing task {task.id_}: {task.description} with state {state}",
        ) in caplog.record_tuples

    def test_close_child_task_generates_next_children(
        self,
        action: Callable[[FakeRepository, TaskSelector], None],
        state: str,
        repo: FakeRepository,
        parent_and_child_tasks: Tuple[RecurrentTask, Task],
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: A repository with a parent and a child task.
        When: Using the do_tasks or rm_tasks on the child_id.
        Then: The child is closed, the new child is created, and the parent
            is left open.
        """
        now = datetime.now()
        parent_task, child_task = parent_and_child_tasks
        selector = TaskSelector(task_ids=[child_task.id_])

        action(repo, selector)  # act

        parent_task = repo.get(parent_task.id_, [RecurrentTask])
        new_child = repo.search({"parent_id": parent_task.id_, "active": True}, [Task])[
            -1
        ]
        assert new_child is not None
        assert new_child > child_task
        assert parent_task.state == "backlog"
        assert child_task.state == state
        assert child_task.closed is not None
        assert (child_task.closed - now).total_seconds() < 1
        assert new_child.state == "backlog"
        assert (new_child.created - now).total_seconds() < 1
        assert new_child.due is not None
        assert new_child.due >= parent_task.due
        assert (
            "pydo.services",
            logging.INFO,
            f"Closing child task {child_task.id_}: {child_task.description} with state"
            f" {state}",
        ) in caplog.record_tuples
        assert (
            "pydo.services",
            logging.INFO,
            f"Added child task {new_child.id_}: {new_child.description}",
        ) in caplog.record_tuples

    def test_close_child_task_with_delete_parent_true_also_do_parent(
        self,
        action: Callable[..., None],
        state: str,
        repo: FakeRepository,
        parent_and_child_tasks: Tuple[RecurrentTask, Task],
        freezer: FrozenDateTimeFactory,  # noqa: W0613
    ) -> None:
        """
        Given: A repository with a parent and a child task.
        When: Using the do_tasks or rm_tasks on the child_id
            with the delete_parent flag.
        Then: The child and parent are closed.
        """
        now = datetime.now()
        parent_task, child_task = parent_and_child_tasks
        selector = TaskSelector(task_ids=[child_task.id_])

        action(repo, selector, delete_parent=True)  # act

        parent_task = repo.get(parent_task.id_, [RecurrentTask])
        assert parent_task.state == state
        assert parent_task.closed == now
        assert child_task.state == state
        assert child_task.closed == now

    def test_close_orphan_child_task_with_delete_parent_logs_the_error(
        self,
        action: Callable[..., None],
        state: str,
        repo: FakeRepository,
        task: Task,
        freezer: FrozenDateTimeFactory,  # noqa: W0613
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: A repository with a task without a parent.
        When: Using the do_tasks or rm_tasks on the task
            with the delete_parent flag.
        Then: The task is closed, and the warning is raised.
        """
        now = datetime.now()
        selector = TaskSelector(task_ids=[task.id_])

        action(repo, selector, delete_parent=True)  # act

        assert task.state == state
        assert task.closed == now
        assert (
            "pydo.services",
            logging.INFO,
            f"Task {task.id_} doesn't have a parent",
        ) in caplog.record_tuples

    def test_close_task_doesnt_close_already_closed_tasks(
        self,
        action: Callable[[FakeRepository, TaskSelector], None],
        state: str,
        repo: FakeRepository,
        tasks: List[Task],
        freezer: FrozenDateTimeFactory,  # noqa: W0613
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: An existent closed task.
        When: using the do_tasks or rm_tasks.
        Then: Only the open task is closed.
        """
        closed_task = tasks[0]
        services._close_task(repo, closed_task, TaskState.DONE)
        caplog.clear()
        selector = TaskSelector(task_ids=[closed_task.id_, tasks[1].id_])

        action(repo, selector)  # act

        task = repo.get(tasks[1].id_, [Task])
        assert task.state == state
        assert (
            "pydo.services",
            logging.INFO,
            f"Closing task {closed_task.id_}: {closed_task.description} "
            f"with state {state}",
        ) not in caplog.record_tuples


class TestTaskMod:
    """Test the modification of tasks."""

    def test_modify_task_modifies_task_attributes(
        self,
        repo: FakeRepository,
        faker: Faker,
        task: Task,
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: An existent task.
        When: Using modify_task to modify the description.
        Then: The description is modified.
        """
        now = datetime.now()
        description = faker.sentence()
        selector = TaskSelector(task_ids=[task.id_])
        change = TaskChanges(
            task_attributes={"description": description},
        )

        services.modify_tasks(repo, selector, change)  # act

        modified_task = repo.get(task.id_, [Task])
        assert modified_task.description == description
        assert (modified_task.modified - now).total_seconds() < 1
        assert (
            "pydo.services",
            logging.INFO,
            f"Modified task {task.id_}.",
        ) in caplog.record_tuples

    def test_modify_raises_error_if_task_not_found(
        self, repo: FakeRepository, faker: Faker, task: Task, caplog: LogCaptureFixture
    ) -> None:
        """
        Given: An inexistent task
        When: Using modify_tasks on an that task
        Then: An error is raised
        """
        selector = TaskSelector(task_ids=[9999999])
        change = TaskChanges(
            task_attributes={"description": faker.sentence()},
        )

        with pytest.raises(
            EntityNotFoundError,
            match="There are no entities of type Task in the repository with id",
        ):
            services.modify_tasks(repo, selector, change)  # act

    def test_modify_task_adds_tags(
        self, repo: FakeRepository, task: Task, faker: Faker
    ) -> None:
        """
        Given: A task without tags
        When: modifying it to add a tag
        Then: the tags are added
        """
        selector = TaskSelector(task_ids=[task.id_])
        tag = faker.word()
        change = TaskChanges(tags_to_add=[tag])

        services.modify_tasks(repo, selector, change)  # act

        modified_task = repo.get(task.id_, [Task])
        assert modified_task.tags == [tag]

    @pytest.mark.secondary()
    def test_modify_task_removes_tags(
        self, repo: FakeRepository, task: Task, faker: Faker
    ) -> None:
        """
        Given: A task with a tag
        When: modifying it to remove the tag
        Then: the tags are removed, but the rest of the properties are kept.
        """
        tag = faker.word()
        selector = TaskSelector(task_ids=[task.id_])
        change = TaskChanges(tags_to_add=[tag])
        services.modify_tasks(repo, selector, change)
        change = TaskChanges(tags_to_remove=[tag])

        services.modify_tasks(repo, selector, change)  # act

        modified_task = repo.get(task.id_, [Task])
        assert modified_task.tags == []
        assert modified_task.description == task.description

    def test_modify_task_warns_if_task_doesnt_have_any_tag(
        self, repo: FakeRepository, task: Task, caplog: LogCaptureFixture, faker: Faker
    ) -> None:
        """
        Given: A task without a tag
        When: modifying it to remove the tag
        Then: A warning is shown that the task doesn't have any tag to remove
        """
        selector = TaskSelector(task_ids=[task.id_])
        tag = faker.word()
        change = TaskChanges(tags_to_remove=[tag])

        services.modify_tasks(repo, selector, change)  # act

        assert (
            "pydo.services",
            logging.WARNING,
            f"Task {task.id_} doesn't have the tag {tag} assigned.",
        ) in caplog.record_tuples

    def test_modify_task_modifies_parent_attributes(
        self,
        repo: FakeRepository,
        caplog: LogCaptureFixture,
        faker: Faker,
        insert_parent_task: Tuple[RecurrentTask, Task],
    ) -> None:
        """
        Given: A recurrent task and it's child
        When: modifying the child with modify_parent = True
        Then: Both parent and child attributes are changed.
        """
        parent_task, child_task = insert_parent_task
        selector = TaskSelector(task_ids=[child_task.id_])
        description = faker.sentence()
        change = TaskChanges(task_attributes={"description": description})

        services.modify_tasks(repo, selector, change, modify_parent=True)  # act

        modified_child_task = repo.get(child_task.id_, [Task])
        modified_parent_task = repo.get(parent_task.id_, [RecurrentTask])
        assert modified_child_task.description == description
        assert modified_parent_task.description == description

    def test_modify_child_task_parent_notifies_orphan_if_no_parent(
        self,
        repo: FakeRepository,
        task: Task,
        caplog: LogCaptureFixture,
        faker: Faker,
    ) -> None:
        """
        Given: A task without parent
        When: modifying the task with modify_parent = True
        Then: A warning is shown that the task has no parent.
        """
        selector = TaskSelector(task_ids=[task.id_])
        description = faker.sentence()
        change = TaskChanges(task_attributes={"description": description})

        services.modify_tasks(repo, selector, change, modify_parent=True)  # act

        modified_task = repo.get(task.id_, [Task])
        assert modified_task.description == description
        assert (
            "pydo.services",
            logging.WARNING,
            f"Task {task.id_} doesn't have a parent task.",
        ) in caplog.record_tuples

    def test_modify_doesnt_change_task_if_change_changes_nothing(
        self, repo: FakeRepository, task: Task, caplog: LogCaptureFixture, faker: Faker
    ) -> None:
        """
        Given: A task
        When: modifying it's description to the same value
        Then: The modified task log message is not shown
        """
        selector = TaskSelector(task_ids=[task.id_])
        change = TaskChanges(task_attributes={"description": task.description})

        services.modify_tasks(repo, selector, change)  # act

        assert (
            "pydo.services",
            logging.INFO,
            f"Modified task {task.id_}.",
        ) not in caplog.record_tuples


class TestTaskFreeze:
    """Test the freezing of tasks."""

    def test_freeze_child_task_sets_state(
        self,
        repo: FakeRepository,
        parent_and_child_tasks: Tuple[RecurrentTask, Task],
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: A recurrent parent and child tasks.
        When: using the freeze_tasks on the child task
        Then: The parent's state becomes frozen, and the last child is deleted from
            the repository.
        """
        now = datetime.now()
        parent_task, child_task = parent_and_child_tasks
        selector = TaskSelector(task_ids=[child_task.id_])

        services.freeze_tasks(repo, selector)  # act

        with pytest.raises(EntityNotFoundError):
            repo.get(child_task.id_, [Task])
        parent_task = repo.get(parent_task.id_, [RecurrentTask])
        assert parent_task.active is False
        assert parent_task.state == TaskState.FROZEN
        assert (parent_task.modified - now).total_seconds() < 1
        assert (
            "pydo.services",
            logging.INFO,
            f"Frozen recurrent task {parent_task.id_}: {parent_task.description} and "
            f"deleted it's last child {child_task.id_}",
        ) in caplog.record_tuples

    def test_freeze_parent_task_sets_state(
        self,
        repo: FakeRepository,
        parent_and_child_tasks: Tuple[RecurrentTask, Task],
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: A recurrent parent and child tasks.
        When: using the freeze_tasks on the child task
        Then: The parent's state becomes frozen, and the last child is deleted from
            the repository.
        """
        parent_task, child_task = parent_and_child_tasks
        selector = TaskSelector(task_ids=[parent_task.id_], model=RecurrentTask)

        services.freeze_tasks(repo, selector)  # act

        with pytest.raises(EntityNotFoundError):
            repo.get(child_task.id_, [Task])
        parent_task = repo.get(parent_task.id_, [RecurrentTask])
        assert parent_task.active is False
        assert parent_task.state == TaskState.FROZEN
        assert (
            "pydo.services",
            logging.INFO,
            f"Frozen recurrent task {parent_task.id_}: {parent_task.description} and "
            f"deleted it's last child {child_task.id_}",
        ) in caplog.record_tuples


class TestTaskThaw:
    """Test the thawing of tasks."""

    def test_thawing_a_parent_without_children_works(
        self, repo: FakeRepository
    ) -> None:
        """
        Given: A parent without children
        When: Thawing the parent
        Then: The parent is thawed and the first children is breeded
        """
        now = datetime.now()
        task = RecurrentTaskFactory(state="frozen")
        repo.add(task)
        repo.commit()
        selector = TaskSelector(task_ids=[task.id_])

        services.thaw_tasks(repo, selector)  # act

        parent_task = repo.get(task.id_, [RecurrentTask])
        assert parent_task.state == TaskState.BACKLOG
        assert (parent_task.modified - now).total_seconds() < 1
        children_tasks = repo.search({"parent_id": parent_task.id_}, [Task])
        assert len(children_tasks) == 1

    @pytest.mark.secondary()
    def test_thawing_a_parent_with_completed_children_works(
        self, repo: FakeRepository, insert_parent_task: Tuple[RecurrentTask, Task]
    ) -> None:
        """
        Given: A parent with completed children
        When: Thawing the parent
        Then: The parent is thawed and the next children is breeded
        """
        parent_task, child_task = insert_parent_task
        services._close_task(repo, child_task, TaskState.DONE)
        repo.commit()
        selector = TaskSelector(task_ids=[parent_task.id_], model=RecurrentTask)
        services.freeze_tasks(repo, selector)

        services.thaw_tasks(repo, selector)  # act

        parent_task = repo.get(parent_task.id_, [RecurrentTask])
        assert parent_task.state == TaskState.BACKLOG
        children_tasks = repo.search(
            {"parent_id": parent_task.id_, "active": True}, [Task]
        )
        assert len(children_tasks) == 1

    def test_thawing_returns_error_if_no_tasks_to_thaw(
        self, repo: FakeRepository
    ) -> None:
        """
        Given: An empty repository
        When: Thawing a list of tasks that don't exist
        Then: An error is shown
        """
        selector = TaskSelector(task_attributes={"state": "todo"})

        with pytest.raises(
            EntityNotFoundError, match="No frozen tasks were found with that criteria"
        ):
            services.thaw_tasks(repo, selector)  # act


def test_task_selector_doesnt_return_tasks_that_dont_match_filter(
    repo: Repository, task: Task
) -> None:
    """
    Given: A task in the repository
    When: using a task selector with that id and a filter that doesn't match the task
    Then: No task is returned
    """
    selector = TaskSelector(task_ids=[task.id_], task_filter={"body": "not there"})

    result = services._tasks_from_selector(repo, selector)

    assert len(result) == 0
