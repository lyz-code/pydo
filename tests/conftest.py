from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
import pytest
import tempfile

os.environ['PYDO_CONFIG'] = 'assets/config.yaml'

temp_ddbb = tempfile.mkstemp()[1]
sqlalchemy_url = 'sqlite:///{}'.format(temp_ddbb)
os.environ['PYDO_DATABASE_URL'] = sqlalchemy_url

# It needs to be after the environmental variable
from tests import factories


@pytest.fixture(scope='module')
def connection():
    '''
    Fixture to set up the connection to the temporal database, the path is
    stablished at conftest.py
    '''

    # Create database connection
    connection = create_engine(sqlalchemy_url).connect()

    # Applies all alembic migrations.
    config = Config('pydo/migrations/alembic.ini')
    upgrade(config, 'head')

    # End of setUp

    yield connection

    # Start of tearDown
    connection.close()


@pytest.fixture(scope='function')
def session(connection):
    '''
    Fixture to set up the sqlalchemy session of the database.
    '''

    # Begin a non-ORM transaction and bind session
    transaction = connection.begin()
    session = sessionmaker()(bind=connection)

    factories.ProjectFactory._meta.sqlalchemy_session = session
    factories.TagFactory._meta.sqlalchemy_session = session
    factories.TaskFactory._meta.sqlalchemy_session = session
    factories.RecurrentTaskFactory._meta.sqlalchemy_session = session

    yield session

    # Close session and rollback transaction
    session.close()
    transaction.rollback()
