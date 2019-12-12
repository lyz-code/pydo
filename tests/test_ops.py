from unittest.mock import patch
from pydo.ops import install

import os
import pytest


class TestInstall:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.homedir = os.path.expanduser('~')
        self.os_patch = patch('pydo.ops.os', autospect=True)
        self.os = self.os_patch.start()
        self.os.path.expanduser.side_effect = os.path.expanduser
        self.os.path.join.side_effect = os.path.join
        self.os.path.dirname.return_value = '/home/test/.venv/pydo/pydo'

        self.alembic_patch = patch('pydo.ops.alembic', autospect=True)
        self.alembic = self.alembic_patch.start()

        yield 'setup'

        self.os_patch.stop()
        self.alembic_patch.stop()

    def test_creates_the_data_directory_if_it_doesnt_exist(self):
        self.os.path.exists.return_value = False

        install()
        assert self.os.makedirs.assert_called_with(
                os.path.join(self.homedir, '.local/share/pydo')
            ) is None

    def test_doesnt_create_data_directory_if_exist(self):
        self.os.path.exists.return_value = True

        install()
        assert self.os.makedirs.called is False

    def test_initializes_database(self):
        alembic_args = [
            '-c',
            '/home/test/.venv/pydo/pydo/migrations/alembic.ini',
            'upgrade',
            'head',
        ]

        install()

        assert self.alembic.config.main.assert_called_with(argv=alembic_args) \
            is None
