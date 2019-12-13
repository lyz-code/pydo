from unittest.mock import patch, call, Mock
from pydo.ops import install

import os
import pytest


class TestInstall:
    """
    Test class to ensure that the install process works as expected
    interface.

    Public attributes:
        alembic (mock): alembic mock.
        homedir (string): User home directory path
        log (mock): logging mock
        log_info (mock): log.info mock
        os (mock): os mock
    """

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.alembic_patch = patch('pydo.ops.alembic', autospect=True)
        self.alembic = self.alembic_patch.start()
        self.config_patch = patch('pydo.ops.ConfigManager', autospect=True)
        self.config = self.config_patch.start()
        self.homedir = os.path.expanduser('~')
        self.log = Mock()
        self.log_info = self.log.info
        self.os_patch = patch('pydo.ops.os', autospect=True)
        self.os = self.os_patch.start()
        self.os.path.expanduser.side_effect = os.path.expanduser
        self.os.path.join.side_effect = os.path.join
        self.os.path.dirname.return_value = '/home/test/.venv/pydo/pydo'
        self.session = session

        yield 'setup'

        self.alembic_patch.stop()
        self.config_patch.stop()
        self.os_patch.stop()

    def test_creates_the_data_directory_if_it_doesnt_exist(self):
        self.os.path.exists.return_value = False

        install(self.session, self.log)
        self.os.makedirs.assert_called_with(
                os.path.join(self.homedir, '.local/share/pydo')
        )
        assert call('Data directory created') in self.log_info.mock_calls

    def test_doesnt_create_data_directory_if_exist(self):
        self.os.path.exists.return_value = True

        install(self.session, self.log)
        assert self.os.makedirs.called is False

    def test_initializes_database(self):
        alembic_args = [
            '-c',
            '/home/test/.venv/pydo/pydo/migrations/alembic.ini',
            'upgrade',
            'head',
        ]

        install(self.session, self.log)

        self.alembic.config.main.assert_called_with(argv=alembic_args)
        assert call('Database initialized') in self.log_info.mock_calls

    def test_seed_config_table(self):
        install(self.session, self.log)

        assert self.config.return_value.seed.called
        assert call('Configuration initialized') in self.log_info.mock_calls
