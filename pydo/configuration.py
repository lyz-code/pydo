"""
Module to define the configuration of the main program.

Classes:
    Config: Class to manipulate the configuration of the program.
"""

from collections import UserDict
from yaml.scanner import ScannerError

import logging
import os
import yaml
import sys

log = logging.getLogger(__name__)


class Config(UserDict):
    """
    Class to manipulate the configuration of the program.

    Arguments:
        config_path (str): Path to the configuration file.
            Default: ~/.local/share/pydo/config.yaml

    Public methods:
        load: Loads configuration from configuration YAML file.
        save: Saves configuration in the configuration YAML file.

    Attributes and properties:
        data(dict): Program configuration.
    """

    def __init__(self, config_path='~/.local/share/pydo/config.yaml'):
        self.load(os.path.expanduser(config_path))

    def load(self, yaml_path):
        """
        Loads configuration from configuration YAML file.

        Arguments:
            yaml_path(str): Path to the file to open.
        """
        try:
            with open(os.path.expanduser(yaml_path), 'r') as f:
                try:
                    self.data = yaml.safe_load(f)
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
                'Error opening configuration file {}'.format(yaml_path)
            )
            sys.exit(1)

    def save(self, yaml_path):
        """
        Saves configuration in the configuration YAML file.

        Arguments:
            yaml_path(str): Path to the file to save.
        """

        with open(os.path.expanduser(yaml_path), 'w+') as f:
            yaml.dump(self.data, f, default_flow_style=False)
