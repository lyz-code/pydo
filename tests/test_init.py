from faker import Faker
from pydo import main
from pydo import models
from pydo.manager import ConfigManager
from tests import factories
from unittest.mock import call, patch

import pytest
import ulid


class TestMain:

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.engine_patch = patch('pydo.models.engine', autospect=True)
        self.engine = self.engine_patch.start()

        self.fake = Faker()

        self.task_report_patch = patch('pydo.TaskReport', autospect=True)
        self.task_report = self.task_report_patch.start()

        self.parser_patch = patch('pydo.load_parser', autospect=True)
        self.parser = self.parser_patch.start()
        self.parser_args = self.parser.return_value.parse_args.return_value

        self.session = session
        self.sessionmaker_patch = patch(
            'pydo.sessionmaker',
            autospect=True
        )
        self.sessionmaker = self.sessionmaker_patch.start()
        self.sessionmaker.return_value.return_value = self.session

        self.tm_patch = patch('pydo.TaskManager', autospect=True)
        self.tm = self.tm_patch.start()

        self.config = ConfigManager(session)
        factories.PydoConfigFactory(session).create()

        yield 'setup'

        self.engine_patch.stop()
        self.task_report_patch.stop()
        self.parser_patch.stop()
        self.sessionmaker_patch.stop()
        self.tm_patch.stop()

    def test_main_loads_parser(self):
        self.parser.parse_args = True
        main()
        assert self.parser.called

    @patch('pydo.load_logger')
    def test_main_loads_logger(self, loggerMock):
        self.parser.parse_args = True
        main()
        assert loggerMock.called

    @patch('pydo.install')
    def test_install_subcommand_calls_install(self, installMock):
        self.parser_args.subcommand = 'install'
        main()
        assert installMock.called

    @pytest.mark.parametrize(
        'subcommand',
        [
            'add',
            'done',
            'del',
            'install',
            'open',
            None
        ]
    )
    def test_session_is_initialized_when_needed(
        self,
        session,
        subcommand
    ):
        self.parser_args.subcommand = subcommand

        main()

        self.sessionmaker.return_value.assert_called_once_with(
            bind=self.engine.connect.return_value
        )

    @pytest.mark.parametrize(
        'subcommand',
        [
            'add',
            'done',
            'del'
        ]
    )
    def test_task_manager_is_initialized_when_needed(
        self,
        session,
        subcommand
    ):
        self.parser_args.subcommand = subcommand

        main()

        self.tm.assert_called_once_with(self.session)

    def test_add_subcomand_creates_task(self):
        title = self.fake.sentence()
        description = self.fake.sentence()
        self.parser_args.subcommand = 'add'
        self.tm.return_value._parse_arguments.return_value = {
            'title': title,
            'description': description,
        }

        main()

        self.tm.return_value.add.assert_called_once_with(
            title=title,
            description=description,
        )

    def test_add_subcomand_creates_task_with_project(self):
        title = self.fake.sentence()
        description = self.fake.sentence()
        project_id = self.fake.word()

        self.parser_args.subcommand = 'add'
        self.tm.return_value._parse_arguments.return_value = {
            'title': title,
            'description': description,
            'project_id': project_id,
        }

        main()

        self.tm.return_value.add.assert_called_once_with(
            title=title,
            description=description,
            project_id=project_id,
        )

    def test_add_subcomand_creates_task_with_tags(self):
        title = self.fake.sentence()
        description = self.fake.sentence()
        tag = self.fake.word()

        self.parser_args.subcommand = 'add'
        self.tm.return_value._parse_arguments.return_value = {
            'title': title,
            'description': description,
            'tags': [tag],
        }

        main()

        self.tm.return_value.add.assert_called_once_with(
            title=title,
            description=description,
            tags=[tag],
        )

    def test_add_subcomand_creates_task_with_priority(self):
        title = self.fake.sentence()
        description = self.fake.sentence()
        priority = self.fake.random_number()

        self.parser_args.subcommand = 'add'
        self.tm.return_value._parse_arguments.return_value = {
            'title': title,
            'description': description,
            'priority': priority,
        }

        main()

        self.tm.return_value.add.assert_called_once_with(
            title=title,
            description=description,
            priority=priority,
        )

    def test_add_subcomand_raises_error_if_no_title(self):
        self.parser_args.subcommand = 'add'
        self.tm.return_value._parse_arguments.return_value = {}

        with pytest.raises(ValueError):
            main()

    def test_done_subcommand_completes_task(self):
        arguments = [
            'done',
            ulid.new().str
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.ulid = arguments[1]
        self.parser_args.parent = False

        main()

        self.tm.return_value.complete.assert_called_once_with(
            id=arguments[1],
            parent=False,
        )

    def test_done_parent_subcommand_completes_parent_task(self):
        arguments = [
            'done',
            '-p',
            ulid.new().str
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.ulid = arguments[1]
        self.parser_args.parent = True

        main()

        self.tm.return_value.complete.assert_called_once_with(
            id=arguments[1],
            parent=True,
        )

    def test_delete_subcommand_deletes_task(self):
        arguments = [
            'del',
            ulid.new().str
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.ulid = arguments[1]
        self.parser_args.parent = False

        main()

        self.tm.return_value.delete.assert_called_once_with(
            id=arguments[1],
            parent=False,
        )

    def test_delete_parent_subcommand_deletes_parent_task(self):
        arguments = [
            'del',
            '-p',
            ulid.new().str
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.ulid = arguments[1]
        self.parser_args.parent = True

        main()

        self.tm.return_value.delete.assert_called_once_with(
            id=arguments[1],
            parent=True,
        )

    @pytest.mark.parametrize(
        'subcommand',
        [
            'open',
            None,
        ]
    )
    @patch('pydo.sessionmaker.return_value.return_value.query')
    def test_open_subcommand_prints_report_by_default(self, mock, subcommand):
        self.parser_args.subcommand = subcommand

        main()

        assert call(models.Task) in mock.mock_calls
        assert call(state='open', type='task') \
            in mock.return_value.filter_by.mock_calls

        self.task_report.assert_called_once_with(self.session)
        self.task_report.return_value.print.assert_called_once_with(
            tasks=mock.return_value.filter_by.return_value,
            columns=self.config.get('report.open.columns').split(', '),
            labels=self.config.get('report.open.labels').split(', '),
        )

    @patch('pydo.Projects')
    def test_projects_subcommand_prints_report(self, projectMock):
        arguments = [
            'projects',
        ]
        self.parser_args.subcommand = arguments[0]

        main()

        projectMock.assert_called_once_with(self.session)

        projectMock.return_value.print.assert_called_once_with(
            columns=self.config.get('report.projects.columns').split(', '),
            labels=self.config.get('report.projects.labels').split(', ')
        )

    @patch('pydo.Tags')
    def test_tags_subcommand_prints_report(self, tagsMock):
        arguments = [
            'tags',
        ]
        self.parser_args.subcommand = arguments[0]

        main()

        tagsMock.assert_called_once_with(self.session)

        tagsMock.return_value.print.assert_called_once_with(
            columns=self.config.get('report.tags.columns').split(', '),
            labels=self.config.get('report.tags.labels').split(', ')
        )

    def test_modify_subcommand_modifies_task(self):
        arguments = [
            'mod',
            ulid.new().str,
            'pro:test',
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.parent = False
        self.parser_args.ulid = arguments[1]
        self.parser_args.modify_argument = arguments[2]
        self.tm.return_value._parse_arguments.return_value = {
            'project': 'test',
        }

        main()

        self.tm.return_value.modify.assert_called_once_with(
            arguments[1],
            project='test',
        )

    def test_modify_parent_subcommand_modifies_parent_task(self):
        arguments = [
            'mod',
            '-p',
            ulid.new().str,
            'pro:test',
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.parent = True
        self.parser_args.ulid = arguments[2]
        self.parser_args.modify_argument = arguments[3]
        self.tm.return_value._parse_arguments.return_value = {
            'project': 'test',
        }

        main()

        self.tm.return_value.modify_parent.assert_called_once_with(
            arguments[2],
            project='test',
        )

    @patch('pydo.export')
    def test_export_subcommand_calls_export(self, exportMock):
        self.parser_args.subcommand = 'export'
        main()
        assert exportMock.called

    def test_freeze_subcommand_freezes_task(self):
        arguments = [
            'freeze',
            ulid.new().str
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.ulid = arguments[1]
        self.parser_args.parent = False

        main()

        self.tm.return_value.freeze.assert_called_once_with(
            id=arguments[1],
            parent=False,
        )

    def test_freeze_parent_subcommand_freezes_parent_task(self):
        arguments = [
            'freeze',
            '-p',
            ulid.new().str
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.ulid = arguments[1]
        self.parser_args.parent = True

        main()

        self.tm.return_value.freeze.assert_called_once_with(
            id=arguments[1],
            parent=True,
        )

    def test_unfreeze_subcommand_unfreezes_task(self):
        arguments = [
            'unfreeze',
            ulid.new().str
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.ulid = arguments[1]
        self.parser_args.parent = False

        main()

        self.tm.return_value.unfreeze.assert_called_once_with(
            id=arguments[1],
            parent=False,
        )

    def test_unfreeze_parent_subcommand_unfreezes_task(self):
        arguments = [
            'unfreeze',
            '-p',
            ulid.new().str
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.ulid = arguments[1]
        self.parser_args.parent = True

        main()

        self.tm.return_value.unfreeze.assert_called_once_with(
            id=arguments[1],
            parent=True,
        )

    @patch('pydo.sessionmaker.return_value.return_value.query')
    def test_repeating_subcommand_prints_repeating_parent_tasks(self, mock):
        self.parser_args.subcommand = 'repeating'

        main()

        assert call(models.RecurrentTask) in mock.mock_calls
        assert call(state='open', recurrence_type='repeating') \
            in mock.return_value.filter_by.mock_calls

        self.task_report.assert_called_once_with(
            self.session,
            models.RecurrentTask
        )
        self.task_report.return_value.print.assert_called_once_with(
            tasks=mock.return_value.filter_by.return_value,
            columns=self.config.get('report.repeating.columns').split(', '),
            labels=self.config.get('report.repeating.labels').split(', '),
        )

    @patch('pydo.sessionmaker.return_value.return_value.query')
    def test_recurring_subcommand_prints_recurring_parent_tasks(self, mock):
        self.parser_args.subcommand = 'recurring'

        main()

        assert call(models.RecurrentTask) in mock.mock_calls
        assert call(state='open', recurrence_type='recurring') \
            in mock.return_value.filter_by.mock_calls

        self.task_report.assert_called_once_with(
            self.session,
            models.RecurrentTask
        )
        self.task_report.return_value.print.assert_called_once_with(
            tasks=mock.return_value.filter_by.return_value,
            columns=self.config.get('report.recurring.columns').split(', '),
            labels=self.config.get('report.recurring.labels').split(', '),
        )

    @patch('pydo.sessionmaker.return_value.return_value.query')
    def test_frozen_subcommand_prints_frozen_parent_tasks(self, mock):
        self.parser_args.subcommand = 'frozen'

        main()

        assert call(models.Task) in mock.mock_calls
        assert call(state='frozen') in mock.return_value.filter_by.mock_calls

        self.task_report.assert_called_once_with(
            self.session,
            models.RecurrentTask
        )
        self.task_report.return_value.print.assert_called_once_with(
            tasks=mock.return_value.filter_by.return_value,
            columns=self.config.get('report.frozen.columns').split(', '),
            labels=self.config.get('report.frozen.labels').split(', '),
        )
