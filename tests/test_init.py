from pydo import main
from unittest.mock import patch

import pytest


class TestMain:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.parser_patch = patch('pydo.load_parser', autospect=True)
        self.parser = self.parser_patch.start()
        self.parser_args = self.parser.return_value.parse_args.return_value

        yield 'setup'

        self.parser_patch.stop()

    def test_main_loads_parser(self):
        self.parser.parse_args = True
        main()
        assert self.parser.called is True

    @patch('pydo.load_logger')
    def test_main_loads_logger(self, loggerMock):
        self.parser.parse_args = True
        main()
        assert loggerMock.called is True
