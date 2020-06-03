"""
Module to define the configuration of the main program.

Classes:
    Config: Class to manipulate the configuration of the program.
"""

from collections import UserDict
from ruamel.yaml import YAML
from ruamel.yaml.scanner import ScannerError

import logging
import os
import sys

log = logging.getLogger(__name__)


class Config(UserDict):
    """
    Class to manipulate the configuration of the program.

    Arguments:
        config_path (str): Path to the configuration file.
            Default: ~/.local/share/pydo/config.yaml

    Public methods:
        get: Fetch the configuration value of the specified key.
            If there are nested dictionaries, a dot notation can be used.
        load: Loads configuration from configuration YAML file.
        save: Saves configuration in the configuration YAML file.

    Attributes and properties:
        config_path (str): Path to the configuration file.
        data(dict): Program configuration.
    """

    def __init__(self, config_path='~/.local/share/pydo/config.yaml'):
        self.config_path = os.path.expanduser(config_path)
        self.load()

    def get(self, key):
        """
        Fetch the configuration value of the specified key. If there are nested
        dictionaries, a dot notation can be used.

        So if the configuration contents are:

        self.data = {
            'first': {
                'second': 'value'
            },
        }

        self.data.get('first.second') == 'value'

        Arguments:
            key(str): Configuration key to fetch
        """
        keys = key.split('.')
        value = self.data.copy()

        for key in keys:
            value = value[key]

        return value

    def load(self):
        """
        Loads configuration from configuration YAML file.
        """

        try:
            with open(os.path.expanduser(self.config_path), 'r') as f:
                try:
                    self.data = YAML().load(f)
                except ScannerError as e:
                    log.error(
                        'Error parsing yaml of configuration file '
                        '{}: {}'.format(
                            e.problem_mark,
                            e.problem,
                        )
                    )
                    sys.exit(1)
        except FileNotFoundError:
            log.error(
                'Error opening configuration file {}'.format(self.config_path)
            )
            sys.exit(1)

    def save(self):
        """
        Saves configuration in the configuration YAML file.
        """

        with open(os.path.expanduser(self.config_path), 'w+') as f:
            yaml = YAML()
            yaml.default_flow_style = False
            yaml.dump(self.data, f)
