"""Test generic behaviour of all Task objects and subclasses."""

from datetime import datetime
from typing import Dict

import pytest
from faker.proxy import Faker
from pydantic import ValidationError
from tests import factories
from tests.factories import RecurrentTaskFactory

from pydo.model.task import RecurrentTask, Task


@pytest.fixture(name="task_attributes")
def task_attributes_(faker: Faker) -> Dict[str, str]:
    """Create the basic attributes of a task."""
    return {
        "id_": faker.pyint(),
        "description": faker.sentence(),
    }


@pytest.fixture(name="task")
def task_() -> Task:
    """Create a task"""
    return factories.TaskFactory.create()


@pytest.fixture(name="open_task")
def open_task_() -> Task:
    """Create an open task"""
    return factories.TaskFactory.create(state="backlog")


def test_raise_error_if_add_task_assigns_unvalid_agile_state(
    task_attributes: Dict[str, str], faker: Faker
) -> None:
    """
    Given: Nothing
    When: A Task is initialized with an invalid agile state
    Then: ValueError is raised
    """
    task_attributes["state"] = faker.word()

    with pytest.raises(
        ValidationError,
        match="value is not a valid enumeration member; permitted: 'backlog'",
    ):
        Task(**task_attributes)


@pytest.mark.freeze_time("2017-05-21")
def test_task_closing(open_task: Task) -> None:
    """
    Given: An open task
    When: The close method is called
    Then: The current date is registered and the state is transitioned to closed.
    """
    now = datetime.now()

    open_task.close()  # act

    assert open_task.state == "done"
    assert open_task.active is False
    assert open_task.closed == now


def test_add_recurrent_task_raises_exception_if_recurrence_type_is_incorrect(
    task_attributes: Dict[str, str],
    faker: Faker,
) -> None:
    """
    Given: The task attributes of a recurrent task with a wrong recurrence_type
    When: A RecurrentTask is initialized.
    Then: TaskAttributeError exception is raised.
    """
    task_attributes = {
        **task_attributes,
        "due": faker.date_time(),
        "recurrence": "1d",
        "recurrence_type": "inexistent_recurrence_type",
    }

    with pytest.raises(
        ValidationError,
        match="value is not a valid enumeration member; permitted: 'recurring'",
    ):
        RecurrentTask(**task_attributes)


@pytest.mark.parametrize("recurrence_type", ["recurring", "repeating"])
def test_raise_exception_if_recurring_task_doesnt_have_due(
    task_attributes: Dict[str, str],
    recurrence_type: str,
) -> None:
    """
    Given: The task attributes of a recurrent task without a due date.
    When: A RecurrentTask is initialized.
    Then: TaskAttributeError exception is raised.
    """
    task_attributes = {
        **task_attributes,
        "recurrence": "1d",
        "recurrence_type": recurrence_type,
    }

    with pytest.raises(
        ValidationError,
        match="field required",
    ):
        RecurrentTask(**task_attributes)


@pytest.mark.parametrize("recurrence_type", ["recurring", "repeating"])
def test_breed_children_removes_unwanted_parent_data(
    recurrence_type: str,
) -> None:
    """
    Given: A valid parent task.
    When: The breed_children method is called.
    Then: The children doesn't have the recurrence and recurrence_type attributes.
    """
    parent = RecurrentTaskFactory(recurrence_type=recurrence_type)

    result = parent.breed_children()

    assert "recurrence" not in result.__dict__.keys()
    assert "recurrence_type" not in result.__dict__.keys()


@pytest.mark.parametrize("recurrence_type", ["recurring", "repeating"])
@pytest.mark.freeze_time("2017-05-21")
def test_breed_children_new_due_uses_parent_if_no_children(
    recurrence_type: str,
) -> None:
    """
    Given: A recurring parent task without children, and it's due is after today.
    When: breed_children is called.
    Then: The first children's due date will be the parent's.
    """
    parent = factories.RecurrentTaskFactory(
        recurrence_type=recurrence_type, recurrence="1mo", due=datetime(2020, 8, 2)
    )

    result = parent.breed_children()

    assert result.due == parent.due


@pytest.mark.freeze_time("2017-05-21")
def test_breed_children_new_due_follows_recurr_algorithm() -> None:
    """
    Given: A recurring parent task.
    When: breed_children is called.
    Then: The children's due date is calculated using the recurring algorithm.
        It will apply `recurrence` to the parent's due date, until we get the next
        one in the future.
    """
    parent = RecurrentTaskFactory(
        recurrence_type="recurring", recurrence="1mo", due=datetime(1800, 8, 2)
    )
    first_child = factories.TaskFactory(parent_id=parent.id_)
    first_child.close("completed", datetime(1800, 8, 2))

    result = parent.breed_children(first_child)

    assert result.due == datetime(2017, 6, 2)


@pytest.mark.freeze_time("2017-05-21")
def test_breed_children_new_due_follows_repeating_algorithm() -> None:
    """
    Given: A repeating parent task, and it's first child.
    When: breed_children is called.
    Then: The second children's due date is calculated using the repeating algorithm.
        It will apply `recurrence` to the last completed or deleted child's
        completed date independently of when today is.
    """
    parent = RecurrentTaskFactory(
        recurrence_type="repeating", recurrence="1mo", due=datetime(1800, 8, 2)
    )
    first_child = factories.TaskFactory(parent_id=parent.id_)
    first_child.close("completed", datetime(2020, 8, 2))

    result = parent.breed_children(first_child)

    assert result.due == datetime(2020, 9, 2)


@pytest.mark.freeze_time("2017-05-21")
def test_breed_children_new_due_follows_repeating_algorithm_if_no_children() -> None:
    """
    Given: A repeating parent task without any child
    When: breed_children is called.
    Then: The first child is created with a date of today.
    """
    parent = RecurrentTaskFactory(
        recurrence_type="repeating", recurrence="1mo", due=datetime(1800, 8, 2)
    )

    result = parent.breed_children()

    assert result.due == datetime(2017, 5, 21)


@pytest.mark.freeze_time("2017-05-21")
def test_breed_children_repeating_when_last_child_plus_rec_older_than_today() -> None:
    """
    Given: A repeating parent task, and the last child due plus the recurrence date is
        before today.
    When: breed_children is called.
    Then: The second children's due date is set to now.
    """
    parent = RecurrentTaskFactory(
        recurrence_type="repeating", recurrence="1mo", due=datetime(1800, 8, 2)
    )
    first_child = factories.TaskFactory(parent_id=parent.id_)
    first_child.close("completed", datetime(1800, 8, 3))

    result = parent.breed_children(first_child)

    assert result.due == datetime(2017, 5, 21)


def test_not_frozen_recurrent_task_cant_be_thawed() -> None:
    """
    Given: A non frozen recurrent task
    When: trying to thaw it
    Then: an error is returned
    """
    task = RecurrentTaskFactory(state="backlog")

    with pytest.raises(
        ValueError, match=rf"Task {task.id_}: {task.description} is not frozen"
    ):
        task.thaw()
