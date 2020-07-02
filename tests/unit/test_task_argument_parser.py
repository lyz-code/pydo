"""Test the task argument parsing from the friendly string."""

from datetime import datetime

import pytest
from faker import Faker
from freezegun.api import FrozenDateTimeFactory

from pydo.entrypoints.utils import _parse_changes, _parse_task_selector


def test_parse_extracts_description_without_quotes(faker: Faker) -> None:
    """Test description extraction."""
    description = faker.sentence()
    task_arguments = description.split(" ")

    result = _parse_changes(task_arguments)

    assert result.task_attributes == {"description": description}


def test_parse_allows_empty_description() -> None:
    """Test empty description extraction."""
    result = _parse_changes([""])

    assert result.task_attributes == {"description": ""}


@pytest.mark.parametrize(
    ("string", "attribute"),
    [
        ("ar", "area"),
        ("area", "area"),
        ("body", "body"),
        ("st", "state"),
        ("state", "state"),
    ],
)
def test_parse_extracts_string_properties(
    faker: Faker, string: str, attribute: str
) -> None:
    """Test parsing of properties that are strings."""
    description = faker.sentence()
    value = faker.word()
    task_arguments = [
        description,
        f"{string}:{value}",
    ]

    result = _parse_changes(task_arguments)

    assert result.task_attributes == {"description": description, attribute: value}


@pytest.mark.parametrize(
    ("string", "attribute"),
    [
        ("pri", "priority"),
        ("priority", "priority"),
        ("est", "estimate"),
        ("estimate", "estimate"),
        ("wp", "willpower"),
        ("willpower", "willpower"),
        ("vl", "value"),
        ("value", "value"),
        ("fun", "fun"),
    ],
)
def test_parse_extracts_integer_properties(
    faker: Faker, string: str, attribute: str
) -> None:
    """Test parsing of properties that are integers."""
    description = faker.sentence()
    value = faker.random_number()
    task_arguments = [
        description,
        f"{string}:{value}",
    ]

    result = _parse_changes(task_arguments)

    assert result.task_attributes == {"description": description, attribute: value}


def test_parse_extracts_due(faker: Faker, freezer: FrozenDateTimeFactory) -> None:
    """Test parsing of due dates."""
    description = faker.sentence()
    freezer.move_to("2017-05-20")
    due = "1d"
    task_arguments = [
        description,
        f"due:{due}",
    ]

    result = _parse_changes(task_arguments)

    assert result.task_attributes == {
        "description": description,
        "due": datetime(2017, 5, 21),
    }


def test_parse_return_none_if_argument_is_empty() -> None:
    """Test that the attributes can be set to None.

    One of each type (str, date, float, int) and the description
    empty tags are tested separately.
    """
    task_arguments = [
        "",
        "area:",
        "due:",
        "estimate:",
        "fun:",
    ]

    result = _parse_changes(task_arguments)

    assert result.task_attributes == {
        "description": "",
        "area": None,
        "due": None,
        "estimate": None,
        "fun": None,
    }


@pytest.mark.parametrize(
    ("string", "attribute", "recurrence_type"),
    [
        ("recurring", "recurring", "recurring"),
        ("rec", "recurring", "recurring"),
        ("repeating", "repeating", "repeating"),
        ("rep", "repeating", "repeating"),
    ],
)
def test_parse_extracts_recurring_in_long_representation(
    faker: Faker, string: str, attribute: str, recurrence_type: str
) -> None:
    """Test parsing of recurrent tasks."""
    description = faker.sentence()
    recurring = faker.word()
    task_arguments = [
        description,
        f"{string}:{recurring}",
    ]

    result = _parse_changes(task_arguments)

    assert result.task_attributes == {
        "description": description,
        "recurrence_type": recurrence_type,
        "recurrence": recurring,
    }


def test_parse_extracts_task_ids(faker: Faker) -> None:
    """Test the parsing of task ids."""
    task_arguments = ["1", "235", "29044"]

    result = _parse_task_selector(task_arguments)

    assert result.task_ids == [1, 235, 29044]


def test_parse_extracts_tags(faker: Faker) -> None:
    """Test the parsing of tags to add."""
    description = faker.sentence()
    tags = [faker.word(), faker.word()]
    task_arguments = [
        description,
        f"+{tags[0]}",
        f"+{tags[1]}",
    ]

    result = _parse_changes(task_arguments)

    assert result.task_attributes == {"description": description}
    assert result.tags_to_add == tags


def test_parse_extracts_tags_to_remove(faker: Faker) -> None:
    """Test the parsing of tags to remove."""
    description = faker.sentence()
    tags = [faker.word(), faker.word()]
    task_arguments = [
        description,
        f"-{tags[0]}",
        f"-{tags[1]}",
    ]

    result = _parse_changes(task_arguments)

    assert result.task_attributes == {"description": description}
    assert result.tags_to_remove == tags
