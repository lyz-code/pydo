from faker import Faker
from pydo.cli import load_parser, load_logger
from unittest.mock import patch, call


import logging
import pytest
import ulid


class TestArgparse:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.fake = Faker()
        self.parser = load_parser()

    def test_can_specify_install_subcommand(self):
        parsed = self.parser.parse_args(['install'])
        assert parsed.subcommand == 'install'

    def test_can_specify_add_subcommand(self):
        arguments = [
            'add',
            self.fake.sentence(),
        ]
        parsed = self.parser.parse_args(arguments)
        assert parsed.subcommand == arguments[0]
        assert parsed.add_argument == [arguments[1]]

    def test_can_specify_project_in_add_subcommand(self):
        description = self.fake.sentence()
        project_id = self.fake.word()
        arguments = [
            'add',
            description,
            'pro:{}'.format(project_id),
        ]
        parsed = self.parser.parse_args(arguments)
        assert parsed.subcommand == arguments[0]
        assert parsed.add_argument == arguments[1:3]

    def test_can_specify_modify_subcommand(self):
        arguments = [
            'mod',
            self.fake.word(),
            self.fake.sentence(),
        ]
        parsed = self.parser.parse_args(arguments)
        assert parsed.subcommand == arguments[0]
        assert parsed.ulid == arguments[1]
        assert parsed.modify_argument == [arguments[2]]

    def test_can_specify_project_in_modify_subcommand(self):
        description = self.fake.sentence()
        project_id = self.fake.word()
        arguments = [
            'mod',
            self.fake.word(),
            description,
            'pro:{}'.format(project_id),
        ]
        parsed = self.parser.parse_args(arguments)
        assert parsed.subcommand == arguments[0]
        assert parsed.ulid == arguments[1]
        assert parsed.modify_argument == arguments[2:4]

    def test_can_specify_done_subcommand(self):
        arguments = [
            'done',
            ulid.new().str
        ]
        parsed = self.parser.parse_args(arguments)
        assert parsed.subcommand == arguments[0]
        assert parsed.ulid == arguments[1]

    def test_can_specify_delete_subcommand(self):
        arguments = [
            'del',
            ulid.new().str
        ]
        parsed = self.parser.parse_args(arguments)
        assert parsed.subcommand == arguments[0]
        assert parsed.ulid == arguments[1]

    def test_can_specify_list_subcommand(self):
        parsed = self.parser.parse_args(['list'])
        assert parsed.subcommand == 'list'

    def test_can_specify_projects_subcommand(self):
        parsed = self.parser.parse_args(['projects'])
        assert parsed.subcommand == 'projects'

    def test_can_specify_tags_subcommand(self):
        parsed = self.parser.parse_args(['tags'])
        assert parsed.subcommand == 'tags'


class TestLogger:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.logging_patch = patch('pydo.cli.logging', autospect=True)
        self.logging = self.logging_patch.start()

        self.logging.DEBUG = 10
        self.logging.INFO = 20
        self.logging.WARNING = 30
        self.logging.ERROR = 40

        yield 'setup'

        self.logging_patch.stop()

    def test_logger_is_configured_by_default(self):
        load_logger()
        self.logging.addLevelName.assert_has_calls(
                [
                    call(logging.INFO, '[\033[36mINFO\033[0m]'),
                    call(logging.ERROR, '[\033[31mERROR\033[0m]'),
                    call(logging.DEBUG, '[\033[32mDEBUG\033[0m]'),
                    call(logging.WARNING, '[\033[33mWARNING\033[0m]'),
                ]
        )
        self.logging.basicConfig.assert_called_with(
                level=logging.INFO,
                format="  %(levelname)s %(message)s",
        )
