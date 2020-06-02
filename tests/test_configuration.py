from pydo.configuration import Config
from unittest.mock import patch
from yaml.scanner import ScannerError

import os
import pytest
import shutil
import tempfile


class TestConfig:
    """
    Class to test the Config object.

    Public attributes:
        config (Config object): Config object to test
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.config_path = 'assets/config.yaml'
        self.log_patch = patch('pydo.configuration.log', autospect=True)
        self.log = self.log_patch.start()
        self.sys_patch = patch('pydo.configuration.sys', autospect=True)
        self.sys = self.sys_patch.start()

        self.config = Config(self.config_path)
        yield 'setup'

        self.log_patch.stop()
        self.sys_patch.stop()

    def test_config_load(self):
        self.config.load(self.config_path)
        assert len(self.config.data['task']) > 0

    @patch('pydo.configuration.yaml')
    def test_load_handles_wrong_file_format(self, yamlMock):
        yamlMock.safe_load.side_effect = ScannerError(
            'error',
            '',
            'problem',
            'mark',
        )

        self.config.load(self.config_path)
        self.log.error.assert_called_once_with(
            'Error parsing yaml of configuration file mark: problem'
        )
        self.sys.exit.assert_called_once_with(1)

    @patch('pydo.configuration.open')
    def test_load_handles_file_not_found(self, openMock):
        openMock.side_effect = FileNotFoundError()

        self.config.load(self.config_path)
        self.log.error.assert_called_once_with(
            'Error opening configuration file {}'.format(
                self.config_path
            )
        )
        self.sys.exit.assert_called_once_with(1)

    @patch('pydo.configuration.Config.load')
    def test_init_calls_config_load(self, loadMock):
        Config()
        loadMock.assert_called_once_with(
            os.path.expanduser('~/.local/share/pydo/config.yaml')
        )

    def test_save_config(self):
        tmp = tempfile.mkdtemp()
        save_file = os.path.join(tmp, 'yaml_save_test.yaml')
        self.config.save(save_file)
        with open(save_file, 'r') as f:
            assert "task:" in f.read()

        shutil.rmtree(tmp)
