"""Test the view implementations."""

import re
from contextlib import suppress
from typing import Any, Dict, List, Tuple

import pytest
from _pytest.capture import CaptureFixture
from faker import Faker
from repository_orm import EntityNotFoundError, Repository
from tests import factories

from pydo import views
from pydo.config import Config
from pydo.model.task import Task, TaskSelector
from pydo.model.views import Report
from pydo.views import print_task_report


def run_report(
    report_name: str, report_arguments: Dict[str, Any], capsys: CaptureFixture[Any]
) -> Tuple[str, str]:
    """Run a report and return the out and err."""
    report = getattr(views, report_name)
    report(**report_arguments)

    out, err = capsys.readouterr()

    return out, err


def report_prints_expected(
    out: str, expected_out: List[str], err: str, exact: bool = True
) -> bool:
    """Check that the output is the expected, and that no error was shown.

    Args:
        out: report stdout
        expected_output: the output we expect.
        err: report stderr
        exact: expected_out and out must have the same lines
    """
    if err != "":
        return False

    out_lines = out.splitlines()

    if exact and (len(out_lines) != len(expected_out)):
        __import__("pdb").set_trace()  # XXX BREAKPOINT
        return False
    for line_id in range(0, len(out_lines) - 1):
        with suppress(IndexError):
            if not re.match(expected_out[line_id], out_lines[line_id]):
                __import__("pdb").set_trace()  # XXX BREAKPOINT
                return False

    return True


def test_remove_null_columns_removes_columns_if_all_nulls(config: Config) -> None:
    """Test that columns without values are removed from the report."""
    tasks = factories.TaskFactory.create_batch(100, due=None, area="")
    report = Report(labels=["ID", "Description", "Due", "Area"])
    for task in tasks:
        report.add([task.id_, task.description, task.due, task.area])

    report._remove_null_columns()  # act

    assert report.labels == ["ID", "Description"]
    assert report.data[0] == [tasks[0].id_, tasks[0].description]


def test_task_report_prints_task_attributes(
    repo: Repository, config: Config, capsys: CaptureFixture[Any], faker: Faker
) -> None:
    """Test that the open report prints the task attributes."""
    task = Task(description="Description", due=faker.date_time(), priority=3)
    repo.add(task)
    repo.commit()
    expected_output = [
        r".*",
        r" +ID +│ +Description +│ +Pri.*",
        r".*",
        fr" +{task.id_} +│ +{task.description} +│ +{task.priority}.*",
        r".*",
    ]

    out, err = run_report(
        "print_task_report",
        {"repo": repo, "config": config, "report_name": "open"},
        capsys,
    )  # act

    assert report_prints_expected(out, expected_output, err)


def test_task_report_allows_task_filter(
    repo: Repository,
    config: Config,
    insert_multiple_tasks: List[Task],
    capsys: CaptureFixture[Any],
) -> None:
    """
    Given: Many tasks and only one matches a criteria
    When: The open report is called with that criteria
    Then: Only one task is shown
    """
    task = factories.TaskFactory.create(area="special_area")
    task = Task(description="Description", area="special_area")
    repo.add(task)
    repo.commit()
    task_selector = TaskSelector(task_filter={"area": "special_area"})
    expected_output = [
        r".*",
        r" +ID +│ +Description +│ +Area .*",
        r".*",
        fr" +{task.id_} +│ +{task.description} +│ +{task.area}.*",
        r".*",
    ]

    out, err = run_report(
        "print_task_report",
        {
            "repo": repo,
            "config": config,
            "report_name": "open",
            "task_selector": task_selector,
        },
        capsys,
    )  # act

    assert report_prints_expected(out, expected_output, err)


def test_task_report_can_print_tags(
    repo: Repository, config: Config, capsys: CaptureFixture[Any]
) -> None:
    """Test that the open report prints the task tags."""
    # Generate the tasks
    task = factories.TaskFactory.create(
        description="Description", tags=["tag1", "tag2"]
    )
    repo.add(task)
    repo.commit()
    # Generate the output
    expected_output = [
        r".*",
        r" +ID.*│ Tags.*",
        r".*",
        r".* +│ tag1, tag2",
        r".*",
    ]

    out, err = run_report(
        "print_task_report",
        {"repo": repo, "config": config, "report_name": "open"},
        capsys,
    )  # act

    assert report_prints_expected(out, expected_output, err)


def test_areas_prints_only_counts_open_tasks(
    repo: Repository, config: Config, capsys: CaptureFixture[Any]
) -> None:
    """
    Given: Three tasks with the same area, one open, one completed, and other deleted
    When: Printing the areas report
    Then: Only the open task is shown
    """
    tasks = factories.TaskFactory.create_batch(3, area="Area 1")
    tasks[1].close("done")
    tasks[2].close("deleted")
    for task in tasks:
        repo.add(task)
    repo.commit()
    expected_output = [
        r".*",
        r" +Name +│ Open Tasks *",
        r".*",
        r" +Area 1 +│ +1",
        r".*",
    ]
    capsys.readouterr()

    out, err = run_report("areas", {"repo": repo}, capsys)  # act

    assert report_prints_expected(out, expected_output, err)


def test_areas_prints_only_areas_with_open_tasks(
    repo: Repository, config: Config, capsys: CaptureFixture[Any]
) -> None:
    """
    Given: Three tasks with different areas, where only one is open
    When: Printing the areas report
    Then: Only the area with the open task is shown
    """
    tasks = factories.TaskFactory.create_batch(3)
    tasks[1].close("done")
    tasks[2].close("deleted")
    for task in tasks:
        repo.add(task)
    repo.commit()
    expected_output = [
        r".*",
        r" +Name +│ Open Tasks *",
        r".*",
        fr" +{tasks[0].area} +│ +1",
        r".*",
    ]
    capsys.readouterr()

    out, err = run_report("areas", {"repo": repo}, capsys)  # act

    assert report_prints_expected(out, expected_output, err)


def test_areas_shows_open_tasks_without_area(
    repo: Repository, config: Config, capsys: CaptureFixture[Any]
) -> None:
    """
    Given: A task with no area
    When: Printing the areas report
    Then: the area with the open task is shown
    """
    task = factories.TaskFactory.create(area=None)
    repo.add(task)
    repo.commit()
    expected_output = [
        r".*",
        r" +Name +│ Open Tasks *",
        r".*",
        r" +None +│ +1",
        r".*",
    ]
    capsys.readouterr()

    out, err = run_report("areas", {"repo": repo}, capsys)  # act

    assert report_prints_expected(out, expected_output, err)


def test_tags_prints_only_counts_open_tasks(
    repo: Repository, config: Config, capsys: CaptureFixture[Any]
) -> None:
    """
    Given: Two tasks with the same tags, only one open
    When: Printing the tags report
    Then: Only the open task is shown in the report
    """
    tasks = factories.TaskFactory.create_batch(2)
    tasks[0].tags = ["tag_1", "tag_2"]
    tasks[1].tags = ["tag_1", "tag_2"]
    tasks[1].close("done")
    for task in tasks:
        repo.add(task)
    repo.commit()
    expected_output = [
        r".*",
        r" +Name +│ Open Tasks *",
        r".*",
        r" +tag_1 +│ +1",
        r" +tag_2 +│ +1",
        r".*",
    ]
    capsys.readouterr()

    out, err = run_report("tags", {"repo": repo}, capsys)  # act

    assert report_prints_expected(out, expected_output, err)


def test_tags_prints_only_tags_with_open_tasks(
    repo: Repository, config: Config, capsys: CaptureFixture[Any]
) -> None:
    """
    Given: Two tasks with different tags, only one open
    When: Printing the tags report
    Then: Only the open task is shown in the report
    """
    tasks = factories.TaskFactory.create_batch(2)
    tasks[0].tags = ["tag_1"]
    tasks[1].tags = ["tag_2"]
    tasks[1].close("done")
    for task in tasks:
        repo.add(task)
    repo.commit()
    expected_output = [
        r".*",
        r" +Name +│ Open Tasks *",
        r".*",
        r" +tag_1 +│ +1",
        r".*",
    ]
    capsys.readouterr()

    out, err = run_report("tags", {"repo": repo}, capsys)  # act

    assert report_prints_expected(out, expected_output, err)


def test_tags_shows_open_tasks_without_tag(
    repo: Repository, config: Config, capsys: CaptureFixture[Any]
) -> None:
    """
    Given: Two tasks with no tags, only one open
    When: Printing the tags report
    Then: Only the open task is shown in the report
    """
    tasks = factories.TaskFactory.create_batch(2)
    tasks[1].close("done")
    for task in tasks:
        repo.add(task)
    repo.commit()
    expected_output = [
        r".*",
        r" +Name +│ Open Tasks *",
        r".*",
        r" +None +│ +1",
        r".*",
    ]
    capsys.readouterr()

    out, err = run_report("tags", {"repo": repo}, capsys)  # act

    assert report_prints_expected(out, expected_output, err)


def test_report_print_returns_an_error_if_no_data() -> None:
    """
    Given: An empty repository
    When: printing it's data
    Then: returns an error as there is no data
    """
    with pytest.raises(
        EntityNotFoundError, match="The report doesn't have any data to print"
    ):
        Report(labels=["ID"]).print()


@pytest.mark.parametrize(
    ("config_key", "error"),
    [
        (
            "reports.task_attribute_labels",
            "The labels configuration of the reports is not a dictionary.",
        ),
        (
            "reports.task_reports.open.filter",
            "The filter configuration of the open report is not a dictionary.",
        ),
        (
            "reports.task_reports.open.columns",
            "The columns configuration of the open report is not a list.",
        ),
        (
            "reports.task_reports.open.sort",
            "The sort configuration of the open report is not a list.",
        ),
    ],
)
def test_print_report_raises_error_on_bad_report_configuration(
    repo: Repository, config: Config, config_key: str, error: str
) -> None:
    """
    Given: A wrong configured report
    When: print_task_report is called
    Then: An error is shown
    """
    config.set(config_key, 1)
    config.save()

    with pytest.raises(ValueError, match=error):
        print_task_report(repo, config, "open")


class TestSorting:
    """Test the sorting of tasks."""

    def test_sort_accepts_one_argument(self) -> None:
        """
        Given: Three tasks with different priority
        When: sort is called with +priority
        Then: The tasks are returned ordered by increasing priority order
        """
        tasks = [
            Task(id_=0, priority=4),
            Task(id_=1, priority=1),
            Task(id_=2, priority=5),
        ]

        result = views.sort_tasks(tasks.copy(), ["+priority"])

        assert result == [tasks[1], tasks[0], tasks[2]]

    def test_sort_accepts_one_argument_in_descending(self) -> None:
        """
        Given: Three tasks with different priority
        When: sort is called with -priority
        Then: The tasks are returned ordered by decreasing priority order
        """
        tasks = [
            Task(id_=0, priority=4),
            Task(id_=1, priority=1),
            Task(id_=2, priority=5),
        ]

        result = views.sort_tasks(tasks.copy(), ["-priority"])

        assert result == [tasks[2], tasks[0], tasks[1]]

    def test_sort_accepts_one_argument_defaults_ascending(self) -> None:
        """
        Given: Three tasks with different priority
        When: sort is called with priority
        Then: The tasks are returned ordered by ascending priority order
        """
        tasks = [
            Task(id_=0, priority=4),
            Task(id_=1, priority=1),
            Task(id_=2, priority=5),
        ]

        result = views.sort_tasks(tasks.copy(), ["priority"])

        assert result == [tasks[1], tasks[0], tasks[2]]

    def test_sort_accepts_two_argument(self) -> None:
        """
        Given: Three tasks with different priority and id
        When: sort is called with +priority, +id_
        Then: The tasks are returned ordered by increasing priority order, and then by
            increasing id_
        """
        tasks = [
            Task(id_=2, priority=4),
            Task(id_=0, priority=4),
            Task(id_=1, priority=1),
        ]

        result = views.sort_tasks(tasks.copy(), ["priority", "id_"])

        assert result == [tasks[2], tasks[1], tasks[0]]

    def test_sort_accepts_two_argument_one_ascending_other_descending(self) -> None:
        """
        Given: Three tasks with different priority and id
        When: sort is called with +priority, -id_
        Then: The tasks are returned ordered by increasing priority order, and then by
            decreasing id_
        """
        tasks = [
            Task(id_=2, priority=4),
            Task(id_=0, priority=4),
            Task(id_=1, priority=1),
        ]

        result = views.sort_tasks(tasks.copy(), ["priority", "-id_"])

        assert result == [tasks[2], tasks[0], tasks[1]]
