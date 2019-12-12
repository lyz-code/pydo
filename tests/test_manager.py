# from sqlalchemy import create_engine
from alembic.command import upgrade
from alembic.config import Config
from pydo.manager import TaskManager
from pydo.models import engine
from sqlalchemy.orm import sessionmaker
from tests.factories import TaskFactory

import pytest

Session = sessionmaker()


@pytest.fixture(scope='module')
def connection():
    '''
    Fixture to set up the connection to the temporal database, the path is
    stablished at conftest.py
    '''

    # Create database connection
    connection = engine.connect()

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
    session = Session(bind=connection)

    TaskFactory._meta.sqlalchemy_session = session

    yield session

    # Close session and rollback transaction
    session.close()
    transaction.rollback()


class TestTaskManager():

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.tm = TaskManager(session)
        self.session = session

    def test_session_attribute_exists(self):
        assert self.tm.session is self.session
