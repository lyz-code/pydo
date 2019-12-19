from faker import Faker
from pydo.fulids import fulid
from pydo.manager import TaskManager, ConfigManager
from pydo.manager import pydo_default_config
from pydo.models import Task, Config
from tests.factories import TaskFactory, ConfigFactory, PydoConfigFactory
from unittest.mock import patch

import pytest


class TableManagerBaseTest:
    """
    Abstract base test class to ensure that all the managers have the same
    interface.

    The Children classes must define the following attributes:
        self.manager: the manager class to test.
        self.model: the sqlalchemy model to test.
        self.factory: a factory_boy object to create dummy objects.

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
        self.log.getLogger.assert_called_with('main')
        assert self.manager.log == self.log.getLogger.return_value

    def test_add_table_element_method_exists(self):
        assert 'add' in dir(self.manager)

    def test_get_element(self):
        element = self.factory.create()
        assert self.manager._get(element.id) == element

    def test_get_raises_valueerror_if_property_doesnt_exist(self):
        with pytest.raises(ValueError):
            self.manager._get('unexistent_property')


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
        PydoConfigFactory(session).create()
        self.session = session

        self.manager = TaskManager(session)
        self.model = Task
        self.factory = TaskFactory

        yield 'setup'

    @patch('pydo.manager.fulid')
    def test_manager_has_fulid_attribute_set(self, fulidMock):
        TaskManager(self.session)

        fulidMock.assert_called_with(
            pydo_default_config['fulid_characters']['default'],
            pydo_default_config['fulid_forbidden_characters']['default'],
        )
        assert isinstance(self.manager.fulid, fulid)

    def test_add_task(self):
        description = self.fake.sentence()

        self.manager.add(description=description)

        generated_task = self.session.query(Task).one()
        assert isinstance(fulid().from_str(generated_task.id), fulid)
        assert generated_task.description == description
        assert generated_task.state == 'open'
        assert generated_task.project is None
        self.log_debug.assert_called_with(
            'Added task {}: {}'.format(
                generated_task.id,
                generated_task.description,
            )
        )

    def test_add_task_generates_secuential_fulid_for_tasks(self):
        existent_task = self.factory.create(state='open')
        existent_task_fulid_id_number = fulid()._decode_id(existent_task.id)

        first_description = 'first task description'
        self.manager.add(description=first_description)

        first_generated_task = self.session.query(Task).filter_by(
            description=first_description
        ).first()
        first_generated_task_fulid_id_number = \
            fulid()._decode_id(first_generated_task.id)

        second_description = 'second task description'
        self.manager.add(description=second_description)

        second_generated_task = self.session.query(Task).filter_by(
            description=second_description
        ).first()
        second_generated_task_fulid_id_number = \
            fulid()._decode_id(second_generated_task.id)

        assert first_generated_task_fulid_id_number - \
            existent_task_fulid_id_number == 1
        assert second_generated_task_fulid_id_number - \
            first_generated_task_fulid_id_number == 1

    def test_delete_task_by_sulid(self):
        task = self.factory.create(state='open')
        closed_utc = self.fake.date_time()
        self.datetime.datetime.now.return_value = closed_utc

        assert self.session.query(Task).one()

        self.manager.delete(
            fulid().fulid_to_sulid(task.id, [task.id]),
        )

        modified_task = self.session.query(Task).get(task.id)
        assert modified_task.closed_utc == closed_utc
        assert modified_task.description == task.description
        assert modified_task.state == 'deleted'
        self.log_debug.assert_called_with(
            'Deleted task {}: {}'.format(
                modified_task.id,
                modified_task.description,
            )
        )

    def test_delete_task_by_fulid(self):
        task = self.factory.create(state='open')
        closed_utc = self.fake.date_time()
        self.datetime.datetime.now.return_value = closed_utc

        assert self.session.query(Task).one()

        self.manager.delete(task.id)

        modified_task = self.session.query(Task).get(task.id)
        assert modified_task.closed_utc == closed_utc
        assert modified_task.description == task.description
        assert modified_task.state == 'deleted'
        self.log_debug.assert_called_with(
            'Deleted task {}: {}'.format(
                modified_task.id,
                modified_task.description,
            )
        )

    def test_complete_task_by_sulid(self):
        closed_utc = self.fake.date_time()
        self.datetime.datetime.now.return_value = closed_utc
        task = TaskFactory.create(state='open')

        assert self.session.query(Task).one()

        self.manager.complete(
            fulid().fulid_to_sulid(task.id, [task.id]),
        )

        modified_task = self.session.query(Task).get(task.id)
        assert modified_task.closed_utc == closed_utc
        assert modified_task.description == task.description
        assert modified_task.state == 'completed'
        self.log_debug.assert_called_with(
            'Completed task {}: {}'.format(
                modified_task.id,
                modified_task.description,
            )
        )

    def test_complete_task_by_fulid(self):
        closed_utc = self.fake.date_time()
        self.datetime.datetime.now.return_value = closed_utc
        task = TaskFactory.create(state='open')

        assert self.session.query(Task).one()

        self.manager.complete(task.id)

        modified_task = self.session.query(Task).get(task.id)
        assert modified_task.closed_utc == closed_utc
        assert modified_task.description == task.description
        assert modified_task.state == 'completed'
        self.log_debug.assert_called_with(
            'Completed task {}: {}'.format(
                modified_task.id,
                modified_task.description,
            )
        )

    def test_config_manager_loaded_in_attribute(self):
        assert isinstance(self.manager.config, ConfigManager)


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
        self.factory = ConfigFactory

        yield 'setup'

    def test_seed_populates_with_expected_values(self):
        self.manager.seed()

        for attribute_key, attribute_value in pydo_default_config.items():
            self.session.query(Config).get(attribute_key)

    def test_get_property_returns_default_value(self):
        config = self.factory.create(user=None)
        assert self.manager.get(config.id) == config.default

    def test_get_property_returns_user_defined_over_default(self):
        config = self.factory.create(user='user_value')
        assert self.manager.get(config.id) == 'user_value'
