"""Test the command line interface."""

import logging
import re
import shutil
from datetime import datetime
from typing import List, Tuple

import pytest
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner
from faker import Faker
from py._path.local import LocalPath
from repository_orm import Repository

from pydo.config import Config
from pydo.entrypoints.cli import cli
from pydo.model.task import RecurrentTask, Task, TaskState
from pydo.version import __version__

from ..factories import RecurrentTaskFactory
from ..unit.test_views import report_prints_expected

log = logging.getLogger(__name__)


@pytest.fixture(name="runner")
def fixture_runner(config: Config) -> CliRunner:
    """Configure the Click cli test runner."""
    return CliRunner(mix_stderr=False, env={"PYDO_CONFIG_PATH": config.config_path})


class TestCli:
    """Test the general cli implementation."""

    def test_version(self, runner: CliRunner) -> None:
        """Prints program version when called with --version."""
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert re.match(
            fr" *pydo version: {__version__}\n" r" *python version: .*\n *platform: .*",
            result.stdout,
        )

    def test_load_config_handles_wrong_file_format(
        self, runner: CliRunner, tmpdir: LocalPath, caplog: LogCaptureFixture
    ) -> None:
        """
        Given: A wrong config file.
        When: Running the command line.
        Then: An error is returned.
        """
        config_file = tmpdir.join("config.yaml")  # type: ignore
        config_file.write("[ invalid yaml")

        result = runner.invoke(cli, ["-c", str(config_file), "null"])

        assert result.exit_code == 1
        assert (
            "pydo.entrypoints.utils",
            logging.ERROR,
            f"Error parsing yaml of configuration file {config_file}: "
            f'while parsing a flow sequence\n  in "{config_file}", '
            "line 1, column 1\nexpected ',' or ']', but got '<stream end>'\n  in"
            f' "{config_file}", line 1, column 15',
        ) in caplog.record_tuples

    def test_load_handles_directory_not_found(
        self, runner: CliRunner, tmpdir: LocalPath, caplog: LogCaptureFixture
    ) -> None:
        """
        Given: A missing config directory.
        When: Running the command line.
        Then: The config directory is created and the default configuration is populated
        """
        shutil.rmtree(tmpdir)
        config_file = tmpdir.join("unexistent_config.yaml")  # type: ignore

        result = runner.invoke(cli, ["-c", str(config_file), "null"])

        assert result.exit_code == 0
        assert (
            "pydo.entrypoints.utils",
            logging.INFO,
            f"Data directory {tmpdir} created",
        ) in caplog.record_tuples
        assert (
            "pydo.entrypoints.utils",
            logging.INFO,
            "Copied default configuration template",
        ) in caplog.record_tuples

    def test_load_handles_file_not_found(
        self, runner: CliRunner, tmpdir: LocalPath, caplog: LogCaptureFixture
    ) -> None:
        """
        Given: A missing config file.
        When: Running the command line.
        Then: The default configuration is populated
        """
        config_file = tmpdir.join("unexistent_config.yaml")  # type: ignore

        result = runner.invoke(cli, ["-c", str(config_file), "null"])

        assert result.exit_code == 0
        assert (
            "pydo.entrypoints.utils",
            logging.INFO,
            f"Data directory {tmpdir} created",
        ) not in caplog.record_tuples
        assert (
            "pydo.entrypoints.utils",
            logging.INFO,
            "Copied default configuration template",
        ) in caplog.record_tuples


# ---------------------------------------------------------------
#                   Actions over tasks
# ---------------------------------------------------------------


class TestAdd:
    """Test the addition of new tasks."""

    def test_add_simple_task(
        self, runner: CliRunner, faker: Faker, caplog: LogCaptureFixture
    ) -> None:
        """Test the insertion of a new task."""
        description = faker.sentence()

        result = runner.invoke(cli, ["add", description])

        assert result.exit_code == 0
        assert re.match(f"Added task .*: {description}", caplog.records[0].msg)

    def test_add_complex_tasks(
        self, runner: CliRunner, faker: Faker, caplog: LogCaptureFixture
    ) -> None:
        """Test the insertion of a new complex task."""
        description = faker.sentence()

        result = runner.invoke(
            cli,
            [
                "add",
                description,
                "due:1mo",
                "pri:5",
                "state:doing",
                "area:health",
                "est:3",
                'body:"{faker.text()}"',
            ],
        )

        assert result.exit_code == 0
        assert re.match(f"Added task .*: {description}", caplog.records[0].msg)

    def test_add_a_task_with_an_inexistent_tag(
        self,
        runner: CliRunner,
        faker: Faker,
        caplog: LogCaptureFixture,
        repo_e2e: Repository,
    ) -> None:
        """Test the insertion of a task with a tag."""
        description = faker.sentence()
        tag = faker.word()

        result = runner.invoke(cli, ["add", description, f"+{tag}"])

        task = repo_e2e.get(0, [Task])
        assert result.exit_code == 0
        assert re.match(f"Added task .*: {description}", caplog.records[0].msg)
        assert tag in task.tags

    def test_add_handles_dateparseerror(
        self, runner: CliRunner, faker: Faker, caplog: LogCaptureFixture
    ) -> None:
        """
        Given: Nothing
        When: adding a new task with an invalid date
        Then: an error is returned.
        """
        result = runner.invoke(cli, ["add", faker.sentence(), "due:invalid_date"])

        assert result.exit_code == 1
        assert (
            "pydo.entrypoints.utils",
            logging.ERROR,
            "Unable to parse the date string invalid_date, please enter a valid one",
        ) in caplog.record_tuples

    def test_add_repeating_task(
        self, runner: CliRunner, faker: Faker, caplog: LogCaptureFixture
    ) -> None:
        """Test adding a repeating task."""
        description = faker.sentence()

        result = runner.invoke(cli, ["add", description, "due:1st", "rep:1mo"])

        assert result.exit_code == 0
        assert re.match(
            f"Added repeating task .*: {description}", caplog.records[0].msg
        )
        assert re.match("Added first child task with id.*", caplog.records[1].msg)

    def test_add_recurring_task(
        self, runner: CliRunner, faker: Faker, caplog: LogCaptureFixture
    ) -> None:
        """Test adding a recurring task."""
        description = faker.sentence()

        result = runner.invoke(cli, ["add", description, "due:1st", "rec:1mo"])

        assert result.exit_code == 0
        assert re.match(
            f"Added recurring task .*: {description}", caplog.records[0].msg
        )
        assert re.match("Added first child task with id.*", caplog.records[1].msg)

    def test_add_recurrent_task_fails_gently_if_no_due(
        self, runner: CliRunner, faker: Faker, caplog: LogCaptureFixture
    ) -> None:
        """Test the error return if a recurring task is created without due date."""
        description = faker.sentence()

        result = runner.invoke(cli, ["add", description, "rec:1mo"])

        assert result.exit_code == 1
        assert re.search("field required", caplog.records[0].msg)


@pytest.mark.parametrize(("action", "state"), [("do", "done"), ("rm", "deleted")])
class TestCliDoAndDel:
    """Test the completion of tasks implementation."""

    def test_close_task_by_id(
        self,
        action: str,
        state: str,
        runner: CliRunner,
        insert_task_e2e: Task,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test completing a task by it's ID."""
        task = insert_task_e2e

        result = runner.invoke(cli, [action, str(task.id_)])

        assert result.exit_code == 0
        assert (
            "pydo.services",
            logging.INFO,
            f"Closing task {task.id_}: {task.description} with state {state}",
        ) in caplog.record_tuples

    def test_close_task_fails_gracefully_if_none_found(
        self,
        action: str,
        state: str,
        runner: CliRunner,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test completing an inexistent task fails gracefully."""
        result = runner.invoke(cli, [action, "9999"])

        assert result.exit_code == 1
        assert (
            "pydo.entrypoints.cli",
            logging.ERROR,
            "There are no entities of type Task in the repository with id 9999.",
        ) in caplog.record_tuples

    def test_close_task_with_complete_date(
        self,
        action: str,
        state: str,
        runner: CliRunner,
        insert_task_e2e: Task,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test completing a task on a specific date."""
        task = insert_task_e2e

        result = runner.invoke(cli, [action, "-d", "1d", str(task.id_)])

        assert result.exit_code == 0
        assert (
            "pydo.services",
            logging.INFO,
            f"Closing task {task.id_}: {task.description} with state {state}",
        ) in caplog.record_tuples

    def test_close_accepts_filter_of_tasks(
        self,
        action: str,
        state: str,
        runner: CliRunner,
        insert_tasks_e2e: List[Task],
        caplog: LogCaptureFixture,
    ) -> None:
        """Test completing a task accepts a task filter."""
        tasks = insert_tasks_e2e
        tasks_to_delete = [task for task in tasks if task.priority == 3]

        result = runner.invoke(cli, [action, "pri:3"])

        assert result.exit_code == 0
        for task in tasks_to_delete:
            assert (
                "pydo.services",
                logging.INFO,
                f"Closing task {task.id_}: {task.description} with state {state}",
            ) in caplog.record_tuples

    def test_close_task_with_delete_parent(
        self,
        action: str,
        state: str,
        runner: CliRunner,
        insert_parent_task_e2e: Tuple[RecurrentTask, Task],
        caplog: LogCaptureFixture,
    ) -> None:
        """Test completing a task accepts a completing the parent."""
        parent, child = insert_parent_task_e2e

        result = runner.invoke(cli, [action, "-p", str(child.id_)])

        assert result.exit_code == 0
        for task_id, task_type, task_description in [
            (parent.id_, "parent", parent.description),
            (child.id_, "child", child.description),
        ]:
            assert (
                "pydo.services",
                logging.INFO,
                f"Closing {task_type} task {task_id}: {task_description} with state"
                f" {state}",
            ) in caplog.record_tuples


class TestMod:
    """Test the task change implementation."""

    def test_modify_task(
        self,
        runner: CliRunner,
        insert_tasks_e2e: List[Task],
        faker: Faker,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test the change of a task by it's ID."""
        task = insert_tasks_e2e[0]
        description = faker.sentence()

        result = runner.invoke(cli, ["mod", str(task.id_), description])

        assert result.exit_code == 0
        assert re.match(f"Modified task {task.id_}", caplog.records[0].msg)

    def test_modify_parent_task(
        self,
        runner: CliRunner,
        insert_parent_task_e2e: Tuple[RecurrentTask, Task],
        faker: Faker,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test the change of a task accepts the change of the parent too."""
        parent, child = insert_parent_task_e2e
        description = faker.sentence()

        result = runner.invoke(cli, ["mod", "--parent", str(child.id_), description])

        assert result.exit_code == 0
        assert re.match(f"Modified task {child.id_}.", caplog.records[0].msg)
        assert re.match(f"Modified recurrent task {parent.id_}.", caplog.records[1].msg)

    def test_modify_task_fails_gracefully_if_none_found(
        self, faker: Faker, runner: CliRunner, caplog: LogCaptureFixture
    ) -> None:
        """Test the change of a task fails gracefully if none found."""
        description = faker.sentence()

        result = runner.invoke(cli, ["mod", "9999999", description])

        assert result.exit_code == 1
        assert (
            "pydo.entrypoints.cli",
            logging.ERROR,
            "There are no entities of type Task in the repository with id 9999999.",
        ) in caplog.record_tuples

    def test_modify_task_can_unset_attribute(
        self,
        runner: CliRunner,
        insert_tasks_e2e: List[Task],
        faker: Faker,
        repo_e2e: Repository,
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: A task with the priority attribute set
        When: setting the attribute to none
        Then: the priority is set to None
        """
        task = insert_tasks_e2e[0]
        task.priority = 3
        repo_e2e.add(task)
        repo_e2e.commit()

        result = runner.invoke(cli, ["mod", str(task.id_), "pri:"])

        modified_task = repo_e2e.get(task.id_, [Task])
        assert result.exit_code == 0
        assert modified_task.priority is None

    def test_modify_task_can_remove_tag_that_starts_with_p(
        self,
        runner: CliRunner,
        insert_tasks_e2e: List[Task],
        faker: Faker,
        repo_e2e: Repository,
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: A task with a tag that starts with a p
        When: removing the tag
        Then: the tag is removed

        It's necessary in case we start using the `--parent` flag as `-p`, in that case
        when using `pydo mod 0 -python`, it interprets that the parent flag is set
        and that the tag is ython.
        """
        task = insert_tasks_e2e[0]
        task.tags = ["python"]
        repo_e2e.add(task)
        repo_e2e.commit()

        result = runner.invoke(cli, ["mod", str(task.id_), "-python"])

        modified_task = repo_e2e.get(task.id_, [Task])
        assert result.exit_code == 0
        assert re.match(f"Modified task {task.id_}", caplog.records[0].msg)
        assert modified_task.tags == []
        assert modified_task.description == task.description


class TestFreeze:
    """Test the implementation of the freeze command."""

    def test_freeze_task_by_id(
        self,
        runner: CliRunner,
        insert_parent_tasks_e2e: Tuple[List[RecurrentTask], List[Task]],
        caplog: LogCaptureFixture,
    ) -> None:
        """Test the freezing of a task by it's ID."""
        parent_tasks, child_tasks = insert_parent_tasks_e2e
        parent_task = parent_tasks[0]
        child_task = child_tasks[0]

        result = runner.invoke(cli, ["freeze", "--parent", str(child_task.id_)])

        assert result.exit_code == 0
        assert (
            "pydo.services",
            logging.INFO,
            f"Frozen recurrent task {parent_task.id_}: {parent_task.description} and "
            f"deleted it's last child {child_task.id_}",
        ) in caplog.record_tuples

    def test_freeze_task_by_parent_id(
        self,
        runner: CliRunner,
        insert_parent_tasks_e2e: Tuple[List[RecurrentTask], List[Task]],
        caplog: LogCaptureFixture,
    ) -> None:
        """Test the freezing of a task by a parent's ID."""
        parent_tasks, child_tasks = insert_parent_tasks_e2e
        parent_task = parent_tasks[0]
        child_task = child_tasks[0]

        result = runner.invoke(cli, ["freeze", str(parent_task.id_)])

        assert result.exit_code == 0
        assert (
            "pydo.services",
            logging.INFO,
            f"Frozen recurrent task {parent_task.id_}: {parent_task.description} and "
            f"deleted it's last child {child_task.id_}",
        ) in caplog.record_tuples

    def test_freeze_accepts_filter_of_tasks(
        self,
        runner: CliRunner,
        insert_parent_tasks_e2e: Tuple[List[RecurrentTask], List[Task]],
        caplog: LogCaptureFixture,
    ) -> None:
        """Test the freezing accepts a filter of tasks."""
        parent_tasks, child_tasks = insert_parent_tasks_e2e
        tasks_to_freeze = [
            task for task in child_tasks if task.state == TaskState.BACKLOG
        ]

        result = runner.invoke(cli, ["freeze", "state:backlog"])

        assert result.exit_code == 0
        for task in tasks_to_freeze:
            assert (
                "pydo.services",
                logging.INFO,
                f"Frozen recurrent task {task.parent_id}: {task.description} and "
                f"deleted it's last child {task.id_}",
            ) in caplog.record_tuples

    def test_freeze_returns_error_if_freezing_a_non_recurring_child_task(
        self,
        runner: CliRunner,
        insert_task_e2e: Task,
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: A normal task
        When: we try to freeze it
        Then: an error is returned as it's not a child of a recurrent task, and
            therefore can't be frozen
        """
        task = insert_task_e2e

        result = runner.invoke(cli, ["freeze", "--parent", str(task.id_)])

        assert result.exit_code == 1
        assert (
            "pydo.entrypoints.cli",
            logging.ERROR,
            f"Task {task.id_}: {task.description} is not the child of any "
            "recurrent task, so it can't be frozen",
        ) in caplog.record_tuples

    def test_freeze_returns_error_if_freezing_a_parent_without_children(
        self, runner: CliRunner, repo_e2e: Repository, caplog: LogCaptureFixture
    ) -> None:
        """
        Given: A parent without children
        When: Freeze called on the parent
        Then: An error is shown
        """
        parent_task = RecurrentTaskFactory.create()
        repo_e2e.add(parent_task)
        repo_e2e.commit()

        result = runner.invoke(cli, ["freeze", str(parent_task.id_)])

        assert result.exit_code == 1
        assert (
            "pydo.entrypoints.cli",
            logging.ERROR,
            f"The recurrent task {parent_task.id_}: {parent_task.description} has no "
            "active children",
        ) in caplog.record_tuples


class TestThaw:
    """Test the thawing of tasks."""

    def test_thaw_task_by_id(
        self,
        runner: CliRunner,
        insert_frozen_parent_task_e2e: RecurrentTask,
        repo_e2e: Repository,
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: A frozen recurrent task
        When: Thawed
        Then: The task is back active and it's next children is breed.
        """
        parent_task = insert_frozen_parent_task_e2e
        now = datetime.now()

        result = runner.invoke(cli, ["thaw", str(parent_task.id_)])

        parent_task = repo_e2e.get(parent_task.id_, [RecurrentTask])
        child_task = repo_e2e.search({"parent_id": parent_task.id_}, [Task])[0]
        assert result.exit_code == 0
        assert (
            "pydo.services",
            logging.INFO,
            f"Thawed task {parent_task.id_}: {parent_task.description}, and created "
            f"it's next child task with id {child_task.id_}",
        ) in caplog.record_tuples
        assert parent_task.state == TaskState.BACKLOG
        assert parent_task.active is True
        assert child_task.state == TaskState.BACKLOG
        assert child_task.active is True
        assert child_task.due is not None
        assert child_task.due > now

    def test_thaw_task_by_id_accepts_state(
        self,
        runner: CliRunner,
        insert_frozen_parent_task_e2e: RecurrentTask,
        repo_e2e: Repository,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test thawing accepts the thawing state of the tasks."""
        parent_task = insert_frozen_parent_task_e2e

        result = runner.invoke(cli, ["thaw", str(parent_task.id_), "-s", "todo"])

        parent_task = repo_e2e.get(parent_task.id_, [RecurrentTask])
        child_task = repo_e2e.search({"parent_id": parent_task.id_}, [Task])[0]
        assert result.exit_code == 0
        # T101: fixme found (T O D O). Lol, it's not a comment to fix something
        assert parent_task.state == TaskState.TODO  # noqa: T101
        assert child_task.state == TaskState.TODO  # noqa: T101

    def test_thaw_accepts_filter_of_tasks(
        self,
        runner: CliRunner,
        insert_frozen_parent_tasks_e2e: List[RecurrentTask],
        repo_e2e: Repository,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test thawing accepts a filter of tasks."""
        result = runner.invoke(cli, ["thaw", "state:frozen"])

        assert result.exit_code == 0
        for parent_task in insert_frozen_parent_tasks_e2e:
            child_task = repo_e2e.search({"parent_id": parent_task.id_}, [Task])[0]
            assert (
                "pydo.services",
                logging.INFO,
                f"Thawed task {parent_task.id_}: {parent_task.description}, and created"
                f" it's next child task with id {child_task.id_}",
            ) in caplog.record_tuples

    def test_thaw_returns_error_if_thawing_a_non_frozen_task(
        self,
        runner: CliRunner,
        insert_parent_task_e2e: Tuple[RecurrentTask, Task],
        caplog: LogCaptureFixture,
    ) -> None:
        """
        Given: A non frozen task
        When: we try to thaw it
        Then: an error is returned as it's not frozen.
        """
        parent_task, child_task = insert_parent_task_e2e

        result = runner.invoke(cli, ["thaw", str(parent_task.id_)])

        assert result.exit_code == 1
        assert (
            "pydo.entrypoints.cli",
            logging.ERROR,
            "No frozen tasks were found with that criteria",
        ) in caplog.record_tuples


# ---------------------------------------------------------------
#                   Reports
# ---------------------------------------------------------------


class TestReport:
    """Test the implementation of a generic report."""

    def test_print_core_reports(
        self, runner: CliRunner, repo_e2e: Repository, insert_tasks_e2e: List[Task]
    ) -> None:
        """Test that report is able to print the core reports.

        These reports come by default with pydo.
        """
        task = Task(description="Description", priority=3)
        task.close()
        repo_e2e.add(task)
        repo_e2e.commit()
        expected_output = [
            r".*",
            r" +ID +│ +Description +│ +Pri.*",
            r".*",
            fr" +{task.id_} +│ +{task.description} +│ +{task.priority}.*",
            r".*",
        ]

        result = runner.invoke(cli, ["report", "closed"])

        assert result.exit_code == 0
        assert report_prints_expected(result.stdout, expected_output, result.stderr)

    def test_print_report_can_specify_filter(
        self, runner: CliRunner, insert_tasks_e2e: List[Task], repo_e2e: Repository
    ) -> None:
        """Test that open report accepts a task filter."""
        task = insert_tasks_e2e[0]
        task.description = "description"
        task.area = "special"
        task.priority = 1
        repo_e2e.add(task)
        repo_e2e.commit()
        expected_output = [
            r".*",
            r" +ID +│ +Description +│ +Area .*",
            r".*",
            fr" +{task.id_} +│ +{task.description} +│ +{task.area}.*",
            r".*",
        ]

        result = runner.invoke(cli, ["report", "open", "area:special"])

        assert result.exit_code == 0
        assert report_prints_expected(result.stdout, expected_output, result.stderr)

    def test_print_report_handles_no_tasks(
        self, runner: CliRunner, caplog: LogCaptureFixture
    ) -> None:
        """Test open fails gracefully if there are no tasks to be shown."""
        result = runner.invoke(cli, ["report", "open"])

        assert result.exit_code == 0
        assert (
            "pydo.entrypoints.cli",
            logging.INFO,
            "There are no entities of type Task in the repository that match the "
            "search filter {'active': True}.",
        ) in caplog.record_tuples

    def test_print_report_handles_wrong_date(
        self, runner: CliRunner, caplog: LogCaptureFixture
    ) -> None:
        """Test open handles errors gracefully, such as an invalid date filter."""
        result = runner.invoke(cli, ["report", "open", "due:invalid_due"])

        assert result.exit_code == 1
        assert (
            "pydo.entrypoints.utils",
            logging.ERROR,
            "Unable to parse the date string invalid_due, please enter a valid one",
        ) in caplog.record_tuples

    def test_print_report_report_allows_sorting(
        self,
        runner: CliRunner,
        repo_e2e: Repository,
        faker: Faker,
    ) -> None:
        """
        Given: Three tasks
        When: printing the open report sorting first by ascending priority, and then
            by descending id.
        Then: The tasks are printed in the desired order
        """
        tasks = [
            Task(id_=0, description="Last", priority=3),
            Task(id_=1, description="Middle", priority=3),
            Task(id_=2, description="First", priority=1),
        ]
        for task in tasks:
            repo_e2e.add(task)
        repo_e2e.commit()
        expected_output = [
            r".*",
            r" +ID +│ +Description +│ +Pri.*",
            r".*",
            fr" +{tasks[2].id_} +│ +{tasks[2].description} +│ +{tasks[2].priority}.*",
            fr" +{tasks[1].id_} +│ +{tasks[1].description} +│ +{tasks[1].priority}.*",
            fr" +{tasks[0].id_} +│ +{tasks[0].description} +│ +{tasks[0].priority}.*",
            r".*",
        ]

        result = runner.invoke(cli, ["report", "open", "sort:+priority,-id_"])

        assert result.exit_code == 0
        assert report_prints_expected(result.stdout, expected_output, result.stderr)

    def test_print_report_report_allows_sorting_by_config(
        self,
        runner: CliRunner,
        repo_e2e: Repository,
        faker: Faker,
        config: Config,
    ) -> None:
        """
        Given: Three tasks and the configuration report with the sorting criteria of
            first sorting by ascending priority, and then by descending id.
        When: printing the open report
        Then: The tasks are printed in the desired order
        """
        tasks = [
            Task(id_=0, description="Last", priority=3),
            Task(id_=1, description="Middle", priority=3),
            Task(id_=2, description="First", priority=1),
        ]
        for task in tasks:
            repo_e2e.add(task)
        repo_e2e.commit()
        config.set("reports.task_reports.open.sort", ["+priority", "-id_"])
        config.save()
        expected_output = [
            r".*",
            r" +ID +│ +Description +│ +Pri.*",
            r".*",
            fr" +{tasks[2].id_} +│ +{tasks[2].description} +│ +{tasks[2].priority}.*",
            fr" +{tasks[1].id_} +│ +{tasks[1].description} +│ +{tasks[1].priority}.*",
            fr" +{tasks[0].id_} +│ +{tasks[0].description} +│ +{tasks[0].priority}.*",
            r".*",
        ]

        result = runner.invoke(cli, ["report", "open"])

        assert result.exit_code == 0
        assert report_prints_expected(result.stdout, expected_output, result.stderr)


class TestOpen:
    """Test the implementation of the open report.

    It's an alias to `report open`, so we only need to test that it works as expected
    by default and that it accepts a task filter.
    """

    def test_print_open_report(
        self,
        runner: CliRunner,
        repo_e2e: Repository,
        faker: Faker,
    ) -> None:
        """Test that open returns the expected output."""
        task = Task(description="Description", due=faker.date_time(), priority=3)
        repo_e2e.add(task)
        repo_e2e.commit()
        expected_output = [
            r".*",
            r" +ID +│ +Description +│ +Pri.*",
            r".*",
            fr" +{task.id_} +│ +{task.description} +│ +{task.priority}.*",
            r".*",
        ]

        result = runner.invoke(cli, ["open"])

        assert result.exit_code == 0
        assert report_prints_expected(result.stdout, expected_output, result.stderr)

    def test_print_open_report_if_no_arguments(
        self, runner: CliRunner, insert_tasks_e2e: List[Task]
    ) -> None:
        """Test that open is the default report if no subcommand is given."""
        result = runner.invoke(cli, [""])

        assert result.exit_code == 0
        assert re.search(r"ID.*Description", result.output)

    def test_print_open_report_can_specify_filter(
        self, runner: CliRunner, insert_tasks_e2e: List[Task], repo_e2e: Repository
    ) -> None:
        """Test that open report accepts a task filter."""
        task = insert_tasks_e2e[0]
        task.description = "description"
        task.area = "special"
        task.priority = 1
        repo_e2e.add(task)
        repo_e2e.commit()
        expected_output = [
            r".*",
            r" +ID +│ +Description +│ +Area .*",
            r".*",
            fr" +{task.id_} +│ +{task.description} +│ +{task.area}.*",
            r".*",
        ]

        result = runner.invoke(cli, ["open", "area:special"])

        assert result.exit_code == 0
        assert report_prints_expected(result.stdout, expected_output, result.stderr)


class TestClosed:
    """Test the implementation of the closed report.

    It's an alias to `report open`, so we only need to test that it works as expected
    by default and that it accepts a task filter.
    """

    def test_print_closed_report(
        self, runner: CliRunner, repo_e2e: Repository, insert_tasks_e2e: List[Task]
    ) -> None:
        """Test that closed returns the expected output."""
        task = Task(description="Description", priority=3)
        task.close()
        repo_e2e.add(task)
        repo_e2e.commit()
        expected_output = [
            r".*",
            r" +ID +│ +Description +│ +Pri.*",
            r".*",
            fr" +{task.id_} +│ +{task.description} +│ +{task.priority}.*",
            r".*",
        ]

        result = runner.invoke(cli, ["closed"])

        assert result.exit_code == 0
        assert report_prints_expected(result.stdout, expected_output, result.stderr)

    def test_print_closed_report_can_specify_filter(
        self, runner: CliRunner, insert_tasks_e2e: List[Task], repo_e2e: Repository
    ) -> None:
        """
        Given: Two closed tasks, one deleted and another done
        When: the closed report is called with the filter that matches only one of them
        Then: only that task is shown
        """
        task = insert_tasks_e2e[0]
        task.description = "description"
        task.area = "special"
        task.priority = 1
        task.close(TaskState.DELETED)
        repo_e2e.add(task)
        insert_tasks_e2e[1].close()
        repo_e2e.add(insert_tasks_e2e[1])
        repo_e2e.commit()
        expected_output = [
            r".*",
            r" +ID +│ +Description +│ +Area .*",
            r".*",
            fr" +{task.id_} +│ +{task.description} +│ +{task.area}.*",
            r".*",
        ]

        result = runner.invoke(cli, ["closed", "area:special"])

        assert result.exit_code == 0
        assert report_prints_expected(result.stdout, expected_output, result.stderr)


class TestRecurring:
    """Test the implementation of the recurring report.

    It's an alias to `report open`, so we only need to test that it works as expected
    by default and that it accepts a task filter.
    """

    def test_print_recurring_report(
        self, runner: CliRunner, repo_e2e: Repository
    ) -> None:
        """Test that recurring returns the expected output."""
        parent = RecurrentTaskFactory.create(description="D", priority=1, area="A")
        repo_e2e.add(parent)
        repo_e2e.commit()

        # ECE001: Expression is too complex. Life is tough
        expected_output = [  # noqa: ECE001
            r".*",
            r" +ID +│ +Descr.* +│ +Recur +│ +RecurType +│ +Area +| +Pri +│ +Due.*",
            r".*",
            fr" +{parent.id_} +│ +{parent.description} +│ +{parent.recurrence} +│ +"
            fr"{parent.recurrence_type.value.title()} +│ +{parent.area} +│ +"
            fr"{parent.priority} +│ +{parent.due.year}.*",
            r".*",
        ]

        result = runner.invoke(cli, ["recurring"])

        assert result.exit_code == 0
        assert report_prints_expected(result.stdout, expected_output, result.stderr)

    def test_print_recurring_report_can_specify_filter(
        self,
        runner: CliRunner,
        insert_parent_tasks_e2e: Tuple[List[RecurrentTask], List[Task]],
        repo_e2e: Repository,
    ) -> None:
        """Test that recurring report accepts a task filter."""
        parent = RecurrentTaskFactory.create(
            description="D", area="special", priority=1
        )
        repo_e2e.add(parent)
        repo_e2e.commit()
        # ECE001: Expression is too complex. Life is tough
        expected_output = [  # noqa: ECE001
            r".*",
            r" +ID +│ +Descri.* +│ +Recur +│ +RecurType +│ +Area +| +Pri +│ +Due.*",
            r".*",
            fr" +{parent.id_} +│ +{parent.description} +│ +{parent.recurrence} +│ +"
            fr"{parent.recurrence_type.value.title()} +│ +{parent.area} +│ +"
            fr"{parent.priority} +│ +{parent.due.year}.*",
            r".*",
        ]

        result = runner.invoke(cli, ["recurring", "area:special"])

        assert result.exit_code == 0
        assert report_prints_expected(result.stdout, expected_output, result.stderr)


class TestFrozen:
    """Test the implementation of the frozen report.

    It's an alias to `report open`, so we only need to test that it works as expected
    by default and that it accepts a task filter.
    """

    def test_print_frozen_report(
        self,
        runner: CliRunner,
        repo_e2e: Repository,
        insert_frozen_parent_task_e2e: RecurrentTask,
        faker: Faker,
    ) -> None:
        """Test that frozen returns the expected output."""
        task = insert_frozen_parent_task_e2e
        task.description = "d"
        task.priority = 1
        repo_e2e.add(task)
        repo_e2e.commit()
        # ECE001: Expression is too complex. Life is tough
        expected_output = [  # noqa: ECE001
            r".*",
            r" +ID +│ +Description +│ +Recur +│ +RecurType +│ +Area +| +Pri +│ +Due.*",
            r".*",
            fr" +{task.id_} +│ +{task.description} +│ +{task.recurrence} +│ +"
            fr"{task.recurrence_type.value.title()} +│ +{task.area} +│ +"
            fr"{task.priority} +│ +{task.due.year}.*",
            r".*",
        ]

        result = runner.invoke(cli, ["frozen"])

        assert result.exit_code == 0
        assert report_prints_expected(result.stdout, expected_output, result.stderr)

    def test_print_frozen_report_can_specify_filter(
        self,
        runner: CliRunner,
        insert_frozen_parent_task_e2e: RecurrentTask,
        repo_e2e: Repository,
    ) -> None:
        """Test that frozen accepts a task filter."""
        task = insert_frozen_parent_task_e2e
        task.description = "d"
        task.area = "special"
        task.priority = 1
        repo_e2e.add(task)
        repo_e2e.commit()
        # ECE001: Expression is too complex. Life is tough
        expected_output = [  # noqa: ECE001
            r".*",
            r" +ID +│ +Description +│ +Recur +│ +RecurType +│ +Area +| +Pri +│ +Due.*",
            r".*",
            fr" +{task.id_} +│ +{task.description} +│ +{task.recurrence} +│ +"
            fr"{task.recurrence_type.value.title()} +│ +{task.area} +│ +"
            fr"{task.priority} +│ +{task.due.year}.*",
            r".*",
        ]

        result = runner.invoke(cli, ["frozen", "area:special"])

        assert result.exit_code == 0
        assert report_prints_expected(result.stdout, expected_output, result.stderr)


class TestAreas:
    """Test the implementation of the areas report."""

    def test_print_areas_report(
        self,
        runner: CliRunner,
        repo_e2e: Repository,
        insert_tasks_e2e: List[Task],
        faker: Faker,
    ) -> None:
        """Test that areas returns the expected output."""
        result = runner.invoke(cli, ["areas"])

        assert result.exit_code == 0
        assert re.search(r" *Name.*Open Tasks.*", result.output)

    def test_print_projects_handles_no_areas(
        self, runner: CliRunner, caplog: LogCaptureFixture
    ) -> None:
        """Test areas fails gracefully if there are no areas to be shown."""
        result = runner.invoke(cli, ["areas"])

        assert result.exit_code == 0
        assert (
            "pydo.entrypoints.cli",
            logging.INFO,
            "No areas found with any open tasks.",
        ) in caplog.record_tuples


class TestTags:
    """Test the implementation of the tags report."""

    def test_print_tags_report(
        self, runner: CliRunner, repo_e2e: Repository, insert_tasks_e2e: List[Task]
    ) -> None:
        """Test that tags returns the expected output."""
        tasks = insert_tasks_e2e
        tasks[0].tags = ["tag1"]
        repo_e2e.add(tasks[0])
        repo_e2e.commit()

        result = runner.invoke(cli, ["tags"])

        assert result.exit_code == 0
        assert re.search(r" +Name.*Open Tasks", result.output)

    def test_print_tags_handles_no_tags(
        self, runner: CliRunner, caplog: LogCaptureFixture
    ) -> None:
        """Test tags fails gracefully if there are no tags to be shown."""
        result = runner.invoke(cli, ["tags"])

        assert result.exit_code == 0
        assert (
            "pydo.entrypoints.cli",
            logging.INFO,
            "No tags found with any open tasks.",
        ) in caplog.record_tuples
