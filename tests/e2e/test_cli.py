import logging
import os
import re
from shutil import copyfile

import alembic.command
import pytest
from alembic.config import Config as AlembicConfig
from click.testing import CliRunner

from pydo import services
from pydo.config import Config
from pydo.entrypoints import load_repository, load_session
from pydo.entrypoints.cli import cli
from tests import factories


@pytest.fixture
def config_e2e(tmpdir_factory):
    data = tmpdir_factory.mktemp("data")
    config_file = str(data.join("config.yaml"))
    copyfile("assets/config.yaml", config_file)

    config = Config(config_file)
    sqlite_file = str(data.join("sqlite.db"))
    config.set("storage.sqlite.path", sqlite_file)
    os.environ["PYDO_DATABASE_URL"] = f"sqlite:///{sqlite_file}"
    config.save()

    yield config


@pytest.fixture
def runner(config_e2e):
    alembic_config = AlembicConfig("pydo/migrations/alembic.ini")
    alembic_config.attributes["configure_logger"] = False
    alembic.command.upgrade(alembic_config, "head")

    yield CliRunner(mix_stderr=False, env={"PYDO_CONFIG_PATH": config_e2e.config_path})


class TestCli:
    def test_load_config_handles_wrong_file_format(self, runner, tmpdir, caplog):
        config_file = tmpdir.join("config.yaml")
        config_file.write("[ invalid yaml")

        result = runner.invoke(cli, ["-c", str(config_file), "null"])

        assert result.exit_code == 1
        assert (
            "pydo.entrypoints",
            logging.ERROR,
            f"Error parsing yaml of configuration file {config_file}: expected ',' or"
            " ']', but got '<stream end>'",
        ) in caplog.record_tuples

    def test_load_handles_file_not_found(self, runner, tmpdir, caplog):
        config_file = tmpdir.join("unexistent_config.yaml")

        result = runner.invoke(cli, ["-c", str(config_file), "null"])

        assert result.exit_code == 1
        assert (
            "pydo.entrypoints",
            logging.ERROR,
            f"Error opening configuration file {config_file}",
        ) in caplog.record_tuples

    def test_migrations_are_run_if_database_is_empty(self, config, caplog, tmpdir):
        sqlite_file = str(tmpdir.join("sqlite.db"))
        runner = CliRunner(
            mix_stderr=False,
            env={
                "PYDO_CONFIG_PATH": config.config_path,
                "PYDO_DATABASE_URL": f"sqlite:///{sqlite_file}",
            },
        )
        caplog.set_level(logging.INFO, logger="alembic")

        result = runner.invoke(cli, ["null"])

        assert result.exit_code == 0
        assert re.match("Running .s", caplog.records[2].msg)


class TestCliAdd:
    def test_add_simple_task(self, runner, faker, caplog):
        description = faker.sentence()
        result = runner.invoke(cli, ["add", description])
        assert result.exit_code == 0
        assert re.match(f"Added task .*: {description}", caplog.records[0].msg)

    def test_add_complex_tasks(self, runner, faker, caplog):
        description = faker.sentence()
        result = runner.invoke(
            cli,
            [
                "add",
                description,
                "due:1mo",
                "pri:5",
                "agile:doing",
                "est:3",
                'body:"{faker.text()}"',
            ],
        )
        assert result.exit_code == 0
        assert re.match(f"Added task .*: {description}", caplog.records[0].msg)

    def test_add_a_task_with_an_inexistent_project(self, runner, faker, caplog):
        description = faker.sentence()
        project = faker.word()
        result = runner.invoke(cli, ["add", description, f"pro:{project}"])
        assert result.exit_code == 0
        assert re.match(f"Added project {project}", caplog.records[0].msg)
        assert re.match(f"Added task .*: {description}", caplog.records[1].msg)

    def test_add_a_task_with_an_inexistent_tag(self, runner, faker, caplog):
        description = faker.sentence()
        tag = faker.word()
        result = runner.invoke(cli, ["add", description, f"+{tag}"])
        assert result.exit_code == 0
        assert re.match(f"Added tag {tag}", caplog.records[0].msg)
        assert re.match(f"Added task .*: {description}", caplog.records[1].msg)

    def test_add_handles_DateParseError(self, runner, faker, caplog):
        result = runner.invoke(cli, ["add", faker.sentence(), "due:invalid_date"])
        assert result.exit_code == 1
        assert (
            "pydo.entrypoints.cli",
            logging.ERROR,
            "Unable to parse the date string invalid_date, please enter a valid one",
        ) in caplog.record_tuples

    def test_add_repeating_task(self, runner, faker, caplog):
        description = faker.sentence()
        result = runner.invoke(cli, ["add", description, "due:1st", "rep:1mo"])
        assert result.exit_code == 0
        assert re.match(
            f"Added repeating task .*: {description}", caplog.records[0].msg
        )
        assert re.match("Added first child task with id.*", caplog.records[1].msg)

    def test_add_recurring_task(self, runner, faker, caplog):
        description = faker.sentence()
        result = runner.invoke(cli, ["add", description, "due:1st", "rec:1mo"])
        assert result.exit_code == 0
        assert re.match(
            f"Added recurring task .*: {description}", caplog.records[0].msg
        )
        assert re.match("Added first child task with id.*", caplog.records[1].msg)

    def test_add_recurrent_task_fails_gently_if_no_due(self, runner, faker, caplog):
        description = faker.sentence()
        result = runner.invoke(cli, ["add", description, "rec:1mo"])
        assert result.exit_code == 1
        assert re.match(
            "You need to specify a due date for recurring tasks", caplog.records[0].msg
        )


@pytest.fixture
def repo_e2e(config_e2e):
    session = load_session(config_e2e)
    yield load_repository(config_e2e, session)


@pytest.fixture
def insert_task_e2e(repo_e2e):
    task = factories.TaskFactory.create(state="open")
    repo_e2e.add(task)
    repo_e2e.commit()
    yield task


@pytest.fixture
def insert_parent_task_e2e(repo_e2e):
    """
    Fixture to insert a RecurrentTask and it's children Task in the
    SQLAlchemyRepository.
    """

    parent_task = factories.RecurrentTaskFactory.create(state="open")
    child_task = parent_task.breed_children(factories.create_fulid())

    parent_task.children = [child_task]
    child_task.parent = parent_task

    repo_e2e.add(parent_task)
    repo_e2e.add(child_task)
    repo_e2e.commit()

    return parent_task, child_task


@pytest.fixture
def insert_tasks_e2e(repo_e2e):
    tasks = factories.TaskFactory.create_batch(3, priority=3, state="open")
    different_task = factories.TaskFactory.create(priority=2, state="open")
    tasks.append(different_task)

    for task in tasks:
        repo_e2e.add(task)
        repo_e2e.commit()

    yield tasks


@pytest.fixture
def insert_project_e2e(repo_e2e):
    project = factories.ProjectFactory.create(state="open")
    repo_e2e.add(project)
    repo_e2e.commit()

    yield project


@pytest.fixture
def insert_tag_e2e(repo_e2e):
    tag = factories.TagFactory.create(state="open")
    repo_e2e.add(tag)
    repo_e2e.commit()

    yield tag


@pytest.mark.parametrize("action,state", (("do", "completed"), ("rm", "deleted")))
class TestCliDoAndDel:
    def test_close_task_by_short_id(
        self, action, state, runner, insert_task_e2e, caplog
    ):
        task = insert_task_e2e

        task_id = task.id
        task_description = task.description

        result = runner.invoke(cli, [action, "a"])

        assert result.exit_code == 0
        assert (
            "pydo.services",
            logging.INFO,
            f"Closed task {task_id}: {task_description} with state {state}",
        ) in caplog.record_tuples

    def test_close_task_with_complete_date(
        self, action, state, runner, insert_task_e2e, caplog
    ):
        task = insert_task_e2e

        task_id = task.id
        task_description = task.description

        result = runner.invoke(cli, [action, "-d", "1d", "a"])

        assert result.exit_code == 0
        assert (
            "pydo.services",
            logging.INFO,
            f"Closed task {task_id}: {task_description} with state {state}",
        ) in caplog.record_tuples

    def test_close_accepts_filter_of_tasks(
        self, action, state, runner, insert_tasks_e2e, caplog
    ):
        tasks = insert_tasks_e2e

        tasks_to_delete = [
            (task.id, task.description) for task in tasks if task.priority == 3
        ]

        result = runner.invoke(cli, [action, "pri:3"])

        assert result.exit_code == 0
        for task_id, task_description in tasks_to_delete:
            assert (
                "pydo.services",
                logging.INFO,
                f"Closed task {task_id}: {task_description} with state {state}",
            ) in caplog.record_tuples

    def test_close_task_with_delete_parent(
        self, action, state, runner, insert_parent_task_e2e, caplog
    ):
        parent, child = insert_parent_task_e2e

        parent_id = parent.id
        parent_description = parent.description
        child_id = child.id
        child_description = child.description

        result = runner.invoke(cli, [action, "-p", child_id])

        assert result.exit_code == 0
        for task_id, task_type, task_description in [
            (parent_id, "parent", parent_description),
            (child_id, "child", child_description),
        ]:
            assert (
                "pydo.services",
                logging.INFO,
                f"Closed {task_type} task {task_id}: {task_description} with state"
                f" {state}",
            ) in caplog.record_tuples

    def test_close_task_fails_gracefully_if_none_found(
        self, action, state, runner, insert_task_e2e, caplog
    ):
        result = runner.invoke(cli, [action, "unexistent_task"])

        assert result.exit_code == 1
        assert (
            "pydo.entrypoints.cli",
            logging.ERROR,
            "No Task found with id unexistent_task",
        ) in caplog.record_tuples


class TestCliMod:
    def test_modify_task(self, runner, insert_tasks_e2e, faker, caplog):
        task = insert_tasks_e2e[0]
        description = faker.sentence()

        result = runner.invoke(cli, ["mod", task.id, description])
        assert result.exit_code == 0
        assert re.match(f"Modified task {task.id}", caplog.records[0].msg)

    def test_modify_parent_task(self, runner, insert_parent_task_e2e, faker, caplog):
        parent, child = insert_parent_task_e2e

        parent_id = parent.id
        child_id = child.id
        description = faker.sentence()

        result = runner.invoke(cli, ["mod", "-p", child.id, description])

        assert result.exit_code == 0
        assert re.match(f"Modified task {child_id}.", caplog.records[0].msg)
        assert re.match(f"Modified task {parent_id}.", caplog.records[1].msg)

    def test_modify_task_fails_gracefully_if_none_found(
        self, faker, runner, insert_task_e2e, caplog
    ):
        description = faker.sentence()

        result = runner.invoke(cli, ["mod", "unexistent_task", description])

        assert result.exit_code == 1
        assert (
            "pydo.entrypoints.cli",
            logging.ERROR,
            "No Task found with id unexistent_task",
        ) in caplog.record_tuples


class TestCliOpen:
    def test_print_open_report(self, runner, insert_tasks_e2e):
        result = runner.invoke(cli, ["open"])

        assert result.exit_code == 0
        assert re.match(r"ID +Description", result.output)

    def test_print_open_report_if_no_arguments(self, runner, insert_tasks_e2e):
        result = runner.invoke(cli, [""])

        assert result.exit_code == 0
        assert re.match(r"ID +Description", result.output)

    def test_print_open_report_can_specify_filter(self, runner, insert_tasks_e2e):
        result = runner.invoke(cli, ["open", f"pri:{insert_tasks_e2e[0].priority}"])

        assert result.exit_code == 0
        assert re.match(r"ID +Description", result.output)

    def test_print_open_handles_no_tasks(self, runner, caplog):
        result = runner.invoke(cli, ["open"])

        assert result.exit_code == 0
        assert (
            "pydo.entrypoints.cli",
            logging.INFO,
            "No open tasks found that match the filter criteria",
        ) in caplog.record_tuples

    def test_print_open_handles_wrong_date(self, runner, caplog):
        result = runner.invoke(cli, ["open", "due:invalid_due"])

        assert result.exit_code == 1
        assert (
            "pydo.entrypoints.cli",
            logging.ERROR,
            "Unable to parse the date string invalid_due, please enter a valid one",
        ) in caplog.record_tuples


class TestCliProjects:
    def test_print_projects_report(
        self, runner, repo_e2e, insert_tasks_e2e, insert_project_e2e
    ):
        tasks = insert_tasks_e2e
        project = insert_project_e2e
        services.modify_tasks(repo_e2e, tasks[0].id, {"project_id": project.id})

        result = runner.invoke(cli, ["projects"])

        assert result.exit_code == 0
        assert re.match(r"Name +Open Tasks +Description", result.output)

    def test_print_projects_handles_no_projects(self, runner, caplog):
        result = runner.invoke(cli, ["projects"])

        assert result.exit_code == 0
        assert (
            "pydo.entrypoints.cli",
            logging.INFO,
            "No projects found with any open tasks.",
        ) in caplog.record_tuples


#     @patch("pydo.Tags")
#     def test_tags_subcommand_prints_report(self, tagsMock):
#         arguments = [
#             "tags",
#         ]
#         self.parser_args.subcommand = arguments[0]
#
#         main()
#
#         tagsMock.assert_called_once_with(self.session)
#
#         tagsMock.return_value.print.assert_called_once_with(
#             columns=self.config.get("report.tags.columns"),
#             labels=self.config.get("report.tags.labels"),
#         )
#
#     @patch("pydo.export")
#     def test_export_subcommand_calls_export(self, exportMock):
#         self.parser_args.subcommand = "export"
#         main()
#         assert exportMock.called
#
#     def test_freeze_subcommand_freezes_task(self):
#         arguments = ["freeze", ulid.new().str]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.ulid = arguments[1]
#         self.parser_args.parent = False
#
#         main()
#
#         self.tm.return_value.freeze.assert_called_once_with(
#             id=arguments[1], parent=False,
#         )
#
#     def test_freeze_parent_subcommand_freezes_parent_task(self):
#         arguments = ["freeze", "-p", ulid.new().str]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.ulid = arguments[1]
#         self.parser_args.parent = True
#
#         main()
#
#         self.tm.return_value.freeze.assert_called_once_with(
#             id=arguments[1], parent=True,
#         )
#
#     def test_unfreeze_subcommand_unfreezes_task(self):
#         arguments = ["unfreeze", ulid.new().str]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.ulid = arguments[1]
#         self.parser_args.parent = False
#
#         main()
#
#         self.tm.return_value.unfreeze.assert_called_once_with(
#             id=arguments[1], parent=False,
#         )
#
#     def test_unfreeze_parent_subcommand_unfreezes_task(self):
#         arguments = ["unfreeze", "-p", ulid.new().str]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.ulid = arguments[1]
#         self.parser_args.parent = True
#
#         main()
#
#         self.tm.return_value.unfreeze.assert_called_once_with(
#             id=arguments[1], parent=True,
#         )
#
#     @patch("pydo.sessionmaker.return_value.return_value.query")
#     def test_repeating_subcommand_prints_repeating_parent_tasks(self, mock):
#         self.parser_args.subcommand = "repeating"
#
#         main()
#
#         assert call(model.RecurrentTask) in mock.mock_calls
#         assert (
#             call(state="open", recurrence_type="repeating")
#             in mock.return_value.filter_by.mock_calls
#         )
#
#         self.task_report.assert_called_once_with(self.session, model.RecurrentTask)
#         self.task_report.return_value.print.assert_called_once_with(
#             tasks=mock.return_value.filter_by.return_value,
#             columns=self.config.get("report.repeating.columns"),
#             labels=self.config.get("report.repeating.labels"),
#         )
#
#     @patch("pydo.sessionmaker.return_value.return_value.query")
#     def test_recurring_subcommand_prints_recurring_parent_tasks(self, mock):
#         self.parser_args.subcommand = "recurring"
#
#         main()
#
#         assert call(model.RecurrentTask) in mock.mock_calls
#         assert (
#             call(state="open", recurrence_type="recurring")
#             in mock.return_value.filter_by.mock_calls
#         )
#
#         self.task_report.assert_called_once_with(self.session, model.RecurrentTask)
#         self.task_report.return_value.print.assert_called_once_with(
#             tasks=mock.return_value.filter_by.return_value,
#             columns=self.config.get("report.recurring.columns"),
#             labels=self.config.get("report.recurring.labels"),
#         )
#
#     @patch("pydo.sessionmaker.return_value.return_value.query")
#     def test_frozen_subcommand_prints_frozen_parent_tasks(self, mock):
#         self.parser_args.subcommand = "frozen"
#
#         main()
#
#         assert call(model.Task) in mock.mock_calls
#         assert call(state="frozen") in mock.return_value.filter_by.mock_calls
#
#         self.task_report.assert_called_once_with(self.session, model.RecurrentTask)
#         self.task_report.return_value.print.assert_called_once_with(
#             tasks=mock.return_value.filter_by.return_value,
#             columns=self.config.get("report.frozen.columns"),
#             labels=self.config.get("report.frozen.labels"),
#         )
#     @patch("pydo.install")
#     def test_install_subcommand_calls_install(self, installMock):
#         self.parser_args.subcommand = "install"
#         main()
#         assert installMock.called


# @pytest.mark.skip("Not yet")
# class TestArgparse:
#     def test_can_specify_modify_subcommand(self):
#         arguments = [
#             "mod",
#             self.fake.word(),
#             self.fake.sentence(),
#         ]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[1]
#         assert parsed.modify_argument == [arguments[2]]
#
#     def test_can_specify_project_in_modify_subcommand(self):
#         description = self.fake.sentence()
#         project_id = self.fake.word()
#         arguments = [
#             "mod",
#             self.fake.word(),
#             description,
#             "pro:{}".format(project_id),
#         ]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[1]
#         assert parsed.modify_argument == arguments[2:4]
#         assert parsed.parent is False
#
#     def test_can_specify_parent_in_modify_subcommand(self):
#         description = self.fake.sentence()
#         arguments = [
#             "mod",
#             "-p",
#             self.fake.word(),
#             description,
#         ]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.parent is True
#         assert parsed.ulid == arguments[2]
#         assert parsed.modify_argument == [arguments[3]]
#
#     def test_can_specify_delete_subcommand(self):
#         arguments = ["del", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[1]
#         assert parsed.parent is False
#
#     def test_can_specify_parent_in_delete_subcommand(self):
#         arguments = ["del", "-p", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.parent is True
#         assert parsed.ulid == arguments[2]
#
#     def test_can_specify_open_subcommand(self):
#         parsed = self.parser.parse_args(["open"])
#         assert parsed.subcommand == "open"
#
#     def test_can_specify_recurring_subcommand(self):
#         parsed = self.parser.parse_args(["recurring"])
#         assert parsed.subcommand == "recurring"
#
#     def test_can_specify_repeating_subcommand(self):
#         parsed = self.parser.parse_args(["repeating"])
#         assert parsed.subcommand == "repeating"
#
#     def test_can_specify_projects_subcommand(self):
#         parsed = self.parser.parse_args(["projects"])
#         assert parsed.subcommand == "projects"
#
#     def test_can_specify_tags_subcommand(self):
#         parsed = self.parser.parse_args(["tags"])
#         assert parsed.subcommand == "tags"
#
#     def test_can_specify_export_subcommand(self):
#         parsed = self.parser.parse_args(["export"])
#         assert parsed.subcommand == "export"
#
#     def test_can_specify_freeze_subcommand(self):
#         arguments = ["freeze", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[1]
#         assert parsed.parent is False
#
#     def test_can_specify_freeze_parent_subcommand(self):
#         arguments = ["freeze", "-p", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[2]
#         assert parsed.parent is True
#
#     def test_can_specify_unfreeze_subcommand(self):
#         arguments = ["unfreeze", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[1]
#         assert parsed.parent is False
#
#     def test_can_specify_unfreeze_parent_subcommand(self):
#         arguments = ["unfreeze", "-p", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[2]
#         assert parsed.parent is True
#
#     def test_can_specify_frozen_subcommand(self):
#         parsed = self.parser.parse_args(["frozen"])
#         assert parsed.subcommand == "frozen"
#
#     @pytest.mark.skip("Not yet")
#     def test_can_specify_install_subcommand(self):
#         parsed = self.parser.parse_args(["install"])
#         assert parsed.subcommand == "install"
