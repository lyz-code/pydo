import unittest
import logging
from unittest.mock import patch, call
from pydo.cli import load_parser, load_logger


class TestArgparse(unittest.TestCase):
    def setUp(self):
        self.parser = load_parser()

    def test_can_specify_install_subcommand(self):
        parsed = self.parser.parse_args(['install'])
        self.assertEqual(parsed.subcommand, 'install')


class TestLogger(unittest.TestCase):

    def setUp(self):
        self.logging_patch = patch('pydo.cli.logging', autospect=True)
        self.logging = self.logging_patch.start()

        self.logging.DEBUG = 10
        self.logging.INFO = 20
        self.logging.WARNING = 30
        self.logging.ERROR = 40

    def tearDown(self):
        self.logging_patch.stop()

    def test_logger_is_configured_by_default(self):
        load_logger()
        self.assertEqual(
            self.logging.addLevelName.assert_has_calls(
                [
                    call(logging.INFO, '[\033[36mINFO\033[0m]'),
                    call(logging.ERROR, '[\033[31mERROR\033[0m]'),
                    call(logging.DEBUG, '[\033[32mDEBUG\033[0m]'),
                    call(logging.WARNING, '[\033[33mWARNING\033[0m]'),
                ]
            ),
            None
        )
        self.assertEqual(
            self.logging.basicConfig.assert_called_with(
                level=logging.INFO,
                format="  %(levelname)s %(message)s",
            ),
            None
        )
