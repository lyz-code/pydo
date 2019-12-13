"""
Module to store the operations functions needed to maintain the program.

Functions:
    install: Function to create the environment for pydo.
"""

from pydo.manager import ConfigManager

import alembic.config
import logging
import os

log = logging.getLogger('main')


def install(session):
    '''
    Function to create the environment for pydo.
    '''

    # Create data directory
    data_directory = os.path.expanduser('~/.local/share/pydo')
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
        log.info('Data directory created')

    # Install the database schema
    pydo_dir = os.path.dirname(os.path.abspath(__file__))

    alembic_args = [
        '-c',
        os.path.join(pydo_dir, 'migrations/alembic.ini'),
        'upgrade',
        'head',
    ]
    alembic.config.main(argv=alembic_args)
    log.info('Database initialized')

    # Initialize the config database
    configmanager = ConfigManager(session)
    configmanager.seed()
    log.info('Configuration initialized')
