from faker import Faker
from pydo.manager import TaskManager, ConfigManager, pydo_default_config
from pydo.models import Task, Config
from tests.factories import TaskFactory
from unittest.mock import patch

import pytest
import ulid


class TableManagerBaseTest:
    """
    Abstract base test class to ensure that all the managers have the same
    interface.

    The Children classes must define the following attributes:
        self.manager: the manager class to test.
        self.model: the sqlalchemy model to test.

    Public attributes:
        datetime (mock): datetime mock.
        fake (Faker object): Faker object.
        log (mock): logging mock
        log_debug (mock): log.debug mock
        session (Session object): Database session.
    """

    @pytest.fixture(autouse=True)
    def base_setup(self, session):
        self.datetime_patch = patch('pydo.manager.datetime', autospect=True)
        self.datetime = self.datetime_patch.start()
        self.fake = Faker()
        self.log_patch = patch('pydo.manager.logging', autospect=True)
        self.log = self.log_patch.start()
        self.log_debug = self.log.getLogger.return_value.debug
        self.session = session

        yield 'base_setup'

        self.datetime_patch.stop()
        self.log_patch.stop()

    def test_session_attribute_exists(self):
        assert self.manager.session is self.session

    def test_log_attribute_exists(self):
        self.log.getLogger.assert_called_once_with('main')
        assert self.manager.log == self.log.getLogger.return_value

    def test_add_table_element_method_exists(self):
        assert 'add' in dir(self.manager)


@pytest.mark.usefixtures('base_setup')
class TestTaskManager(TableManagerBaseTest):
    """
    Class to test the TaskManager object.

    Public attributes:
        datetime (mock): datetime mock.
        fake (Faker object): Faker object.
        log (mock): logging mock
        log_debug (mock): log.debug mock
        session (Session object): Database session.
        manager (TaskManager object): TaskManager object to test
    """

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.manager = TaskManager(session)
        self.model = Task

        yield 'setup'

    def test_add_task(self):
        description = self.fake.sentence()

        self.manager.add(description=description)

        generated_task = self.session.query(Task).one()
        assert isinstance(ulid.from_str(generated_task.ulid), ulid.ulid.ULID)
        assert generated_task.description == description
        assert generated_task.state == 'open'
        assert generated_task.project is None
        self.log_debug.assert_called_with(
            'Added task {}: {}'.format(
                generated_task.ulid,
                generated_task.description,
            )
        )

    def test_delete_task(self):
        closed_utc = self.fake.date_time()
        self.datetime.datetime.now.return_value = closed_utc
        task = TaskFactory.create()

        assert self.session.query(Task).one()

        self.manager.delete(task.ulid)

        modified_task = self.session.query(Task).get(task.ulid)
        assert modified_task.closed_utc == closed_utc
        assert modified_task.description == task.description
        assert modified_task.state == 'deleted'
        self.log_debug.assert_called_with(
            'Deleted task {}: {}'.format(
                modified_task.ulid,
                modified_task.description,
            )
        )

    def test_complete_task(self):
        closed_utc = self.fake.date_time()
        self.datetime.datetime.now.return_value = closed_utc
        task = TaskFactory.create()

        assert self.session.query(Task).one()

        self.manager.complete(task.ulid)

        modified_task = self.session.query(Task).get(task.ulid)
        assert modified_task.closed_utc == closed_utc
        assert modified_task.description == task.description
        assert modified_task.state == 'completed'
        self.log_debug.assert_called_with(
            'Completed task {}: {}'.format(
                modified_task.ulid,
                modified_task.description,
            )
        )


@pytest.mark.usefixtures('base_setup')
class TestConfigManager(TableManagerBaseTest):
    """
    Class to test the ConfigManager object.

    Public attributes:
        datetime (mock): datetime mock.
        fake (Faker object): Faker object.
        log (mock): logging mock
        log_debug (mock): log.debug mock
        session (Session object): Database session.
        manager (ConfigManager object): ConfigManager object to test
    """

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.manager = ConfigManager(session)
        self.model = Config

        yield 'setup'

    def test_seed_populates_with_expected_values(self):
        self.manager.seed()

        for attribute_key, attribute_value in pydo_default_config.items():
            self.session.query(Config).get(attribute_key)
