import unittest
from unittest.mock import patch

from pydo import main

class TestMain(unittest.TestCase):

    def setUp(self):
        self.parser_patch = patch('pydo.load_parser', autospect=True)
        self.parser = self.parser_patch.start()
        self.parser_args = self.parser.return_value.parse_args.return_value

    def tearDown(self):
        self.parser_patch.stop()

    def test_main_loads_parser(self):
        self.parser.parse_args = True
        main()
        self.assertTrue(self.parser.called)

    @patch('pydo.load_logger')
    def test_main_loads_logger(self, loggerMock):
        self.parser.parse_args = True
        main()
        self.assertTrue(loggerMock.called)
