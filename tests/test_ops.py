import os
import unittest

from unittest.mock import patch
from pydo.ops import install


class TestInstall(unittest.TestCase):

    def setUp(self):
        self.homedir = os.path.expanduser('~')
        self.os_patch = patch('pydo.ops.os', autospect=True)
        self.os = self.os_patch.start()
        self.os.path.expanduser.side_effect = os.path.expanduser
        self.os.path.join.side_effect = os.path.join
        self.os.path.dirname.return_value = '/home/test/.venv/pydo/pydo'

        self.alembic_patch = patch('pydo.ops.alembic', autospect=True)
        self.alembic = self.alembic_patch.start()

    def tearDown(self):
        self.os_patch.stop()
        self.alembic_patch.stop()

    def test_creates_the_data_directory_if_it_doesnt_exist(self):

        self.os.path.exists.return_value = False

        install()
        self.assertEqual(
            self.os.makedirs.assert_called_with(
                os.path.join(self.homedir, '.local/share/pydo')
            ),
            None
        )

    def test_doesnt_create_data_directory_if_exist(self):

        self.os.path.exists.return_value = True

        install()
        self.assertFalse(self.os.makedirs.called)

    def test_initializes_database(self):

        alembic_args = [
            '-c',
            '/home/test/.venv/pydo/pydo/migrations/alembic.ini',
            'upgrade',
            'head',
        ]

        install()

        self.assertEqual(
            self.alembic.config.main.assert_called_with(argv=alembic_args),
            None
        )
