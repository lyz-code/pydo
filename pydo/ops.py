"""
Module to store the operations functions needed to maintain the program.

Functions:
    install: Function to create the environment for pydo.
    export: Function to export the database to json to stdout.
"""

from pydo.manager import ConfigManager
from pydo.models import engine
from sqlalchemy import MetaData

import alembic.config
import json
import os


def install(session, log):
    '''
    Function to create the environment for pydo.

    Arguments:
        session (session object): Database session
        log (logging object): log handler

    Returns:
        None
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


def export(session, log):
    '''
    Function to export the database to json to stdout.

    Arguments:
        engine (engine object): Database session

    Returns:
        stdout: json database dump.
    '''

    meta = MetaData()
    meta.reflect(bind=engine)
    data = {}
    for table in meta.sorted_tables:
        data[table.name] = [
            dict(row)
            for row in engine.execute(table.select())
        ]

    print(json.dumps(data))
