"""
Module to store the operations functions needed to maintain the program.

Functions:
    install: Function to create the environment for pydo.
"""

import alembic.config
import os


def install():
    '''
    Function to create the environment for pydo.
    '''

    # Create data directory
    data_directory = os.path.expanduser('~/.local/share/pydo')
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    # Install the database
    pydo_dir = os.path.dirname(os.path.abspath(__file__))

    alembic_args = [
        '-c',
        os.path.join(pydo_dir, 'migrations/alembic.ini'),
        'upgrade',
        'head',
    ]
    alembic.config.main(argv=alembic_args)
