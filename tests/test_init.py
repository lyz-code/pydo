from faker import Faker
from pydo import main
from unittest.mock import patch

import pytest
import ulid


class TestMain:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.engine_patch = patch('pydo.engine', autospect=True)
        self.engine = self.engine_patch.start()

        self.fake = Faker()

        self.ls_patch = patch('pydo.List', autospect=True)
        self.ls = self.ls_patch.start()

        self.parser_patch = patch('pydo.load_parser', autospect=True)
        self.parser = self.parser_patch.start()
        self.parser_args = self.parser.return_value.parse_args.return_value

        self.sessionmaker_patch = patch(
            'pydo.sessionmaker',
            autospect=True
        )
        self.sessionmaker = self.sessionmaker_patch.start()

        self.tm_patch = patch('pydo.TaskManager', autospect=True)
        self.tm = self.tm_patch.start()

        yield 'setup'

        self.engine_patch.stop()
        self.ls_patch.stop()
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
    def test_install_subcomand_calls_install(self, installMock):
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
            'list',
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

        self.tm.assert_called_once_with(
            self.sessionmaker.return_value.return_value
        )

    def test_add_subcomand_creates_task(self):
        arguments = [
            'add',
            self.fake.sentence(),
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.description = arguments[1]
        self.parser_args.project = None

        main()

        self.tm.return_value.add.assert_called_once_with(
            description=arguments[1],
            project=None,
        )

    def test_add_subcomand_creates_task_with_project(self):
        arguments = [
            'add',
            self.fake.sentence(),
            '-p',
            self.fake.word(),
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.description = arguments[1]
        self.parser_args.project = arguments[3]

        main()

        self.tm.return_value.add.assert_called_once_with(
            description=arguments[1],
            project=arguments[3],
        )

    def test_done_subcomand_completes_task(self):
        arguments = [
            'done',
            ulid.new().str
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.ulid = arguments[1]

        main()

        self.tm.return_value.complete.assert_called_once_with(
            id=arguments[1]
        )

    def test_delete_subcomand_deletes_task(self):
        arguments = [
            'del',
            ulid.new().str
        ]
        self.parser_args.subcommand = arguments[0]
        self.parser_args.ulid = arguments[1]

        main()

        self.tm.return_value.delete.assert_called_once_with(
            id=arguments[1]
        )

    @pytest.mark.parametrize(
        'subcommand',
        [
            'list',
            None,
        ]
    )
    def test_list_subcomand_prints_report_and_by_default(self, subcommand):
        self.parser_args.subcommand = subcommand

        main()

        self.ls.assert_called_once_with(
            self.sessionmaker.return_value.return_value
        )
        self.ls.return_value.print.assert_called_once_with(
            columns=['id', 'description', 'project'],
            labels=['ID', 'Description', 'Project']
        )
