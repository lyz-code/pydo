from faker import Faker
from pydo.fulids import fulid
from pydo.manager import TaskManager, ConfigManager
from pydo.manager import pydo_default_config
from pydo.models import Task, Config, Project, Tag
from tests.factories import \
    ConfigFactory, \
    ProjectFactory, \
    PydoConfigFactory, \
    TagFactory, \
    TaskFactory
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
            pydo_default_config['fulid.characters']['default'],
            pydo_default_config['fulid.forbidden_characters']['default'],
        )
        assert isinstance(self.manager.fulid, fulid)

    def test_parse_arguments_extracts_title_without_quotes(self):
        title = self.fake.sentence()
        add_arguments = title.split(' ')

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title

    def test_parse_arguments_extracts_project_in_short_representation(self):
        title = self.fake.sentence()
        project = self.fake.word()
        add_arguments = [
            title,
            'pro:{}'.format(project),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['project_id'] == project

    def test_parse_arguments_extracts_project_in_long_representation(self):
        title = self.fake.sentence()
        project = self.fake.word()
        add_arguments = [
            title,
            'project:{}'.format(project),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['project_id'] == project

    def test_parse_arguments_extracts_tags(self):
        title = self.fake.sentence()
        tags = [self.fake.word(), self.fake.word()]

        add_arguments = [
            title,
            '+{}'.format(tags[0]),
            '+{}'.format(tags[1]),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['tags'] == tags

    def test_parse_arguments_extracts_priority_in_short_representation(self):
        title = self.fake.sentence()
        priority = self.fake.random_number()
        add_arguments = [
            title,
            'pri:{}'.format(priority),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['priority'] == priority

    def test_parse_arguments_extracts_priority_in_long_representation(self):
        title = self.fake.sentence()
        priority = self.fake.random_number()
        add_arguments = [
            title,
            'priority:{}'.format(priority),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['priority'] == priority

    def test_parse_arguments_extracts_estimate_in_short_representation(self):
        title = self.fake.sentence()
        estimate = self.fake.random_number()
        add_arguments = [
            title,
            'est:{}'.format(estimate),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['estimate'] == estimate

    def test_parse_arguments_extracts_estimate_in_long_representation(self):
        title = self.fake.sentence()
        estimate = self.fake.random_number()
        add_arguments = [
            title,
            'estimate:{}'.format(estimate),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['estimate'] == estimate

    def test_parse_arguments_extracts_willpower_in_short_representation(self):
        title = self.fake.sentence()
        willpower = self.fake.random_number()
        add_arguments = [
            title,
            'wp:{}'.format(willpower),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['willpower'] == willpower

    def test_parse_arguments_extracts_willpower_in_long_representation(self):
        title = self.fake.sentence()
        willpower = self.fake.random_number()
        add_arguments = [
            title,
            'willpower:{}'.format(willpower),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['willpower'] == willpower

    def test_parse_arguments_extracts_value_in_short_representation(self):
        title = self.fake.sentence()
        value = self.fake.random_number()
        add_arguments = [
            title,
            'vl:{}'.format(value),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['value'] == value

    def test_parse_arguments_extracts_value_in_long_representation(self):
        title = self.fake.sentence()
        value = self.fake.random_number()
        add_arguments = [
            title,
            'value:{}'.format(value),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['value'] == value

    def test_parse_arguments_extracts_fun_in_long_representation(self):
        title = self.fake.sentence()
        fun = self.fake.random_number()
        add_arguments = [
            title,
            'fun:{}'.format(fun),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['fun'] == fun

    def test_parse_arguments_extracts_body_in_long_representation(self):
        title = self.fake.sentence()
        body = self.fake.sentence()
        add_arguments = [
            title,
            'body:{}'.format(body),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['body'] == body

    def test_parse_arguments_extracts_agile_in_short_representation(self):
        title = self.fake.sentence()
        agile = self.fake.word()
        add_arguments = [
            title,
            'ag:{}'.format(agile),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['agile'] == agile

    def test_parse_arguments_extracts_agile_in_long_representation(self):
        title = self.fake.sentence()
        agile = self.fake.word()
        add_arguments = [
            title,
            'agile:{}'.format(agile),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['agile'] == agile

    def test_add_task(self):
        title = self.fake.sentence()

        self.manager.add(title=title)

        generated_task = self.session.query(Task).one()
        assert isinstance(fulid().from_str(generated_task.id), fulid)
        assert generated_task.title == title
        assert generated_task.state == 'open'
        assert generated_task.project is None
        self.log_debug.assert_called_with(
            'Added task {}: {}'.format(
                generated_task.id,
                generated_task.title,
            )
        )

    def test_add_task_generates_secuential_fulid_for_tasks(self):
        existent_task = self.factory.create(state='open')
        existent_task_fulid_id_number = fulid()._decode_id(existent_task.id)

        first_title = 'first task title'
        self.manager.add(title=first_title)

        first_generated_task = self.session.query(Task).filter_by(
            title=first_title
        ).first()
        first_generated_task_fulid_id_number = \
            fulid()._decode_id(first_generated_task.id)

        second_title = 'second task title'
        self.manager.add(title=second_title)

        second_generated_task = self.session.query(Task).filter_by(
            title=second_title
        ).first()
        second_generated_task_fulid_id_number = \
            fulid()._decode_id(second_generated_task.id)

        assert first_generated_task_fulid_id_number - \
            existent_task_fulid_id_number == 1
        assert second_generated_task_fulid_id_number - \
            first_generated_task_fulid_id_number == 1

    def test_add_task_assigns_project_if_exist(self):
        project = ProjectFactory.create()
        title = self.fake.sentence()

        self.manager.add(title=title, project_id=project.id)

        generated_task = self.session.query(Task).one()
        assert generated_task.project is project

    def test_add_task_generates_project_if_doesnt_exist(self):
        title = self.fake.sentence()

        self.manager.add(title=title, project_id='non_existent')

        generated_task = self.session.query(Task).one()
        project = self.session.query(Project).get('non_existent')

        assert generated_task.project is project
        assert isinstance(project, Project)

    def test_add_task_assigns_tag_if_exist(self):
        tag = TagFactory.create()
        title = self.fake.sentence()

        self.manager.add(title=title, tags=[tag.id])

        generated_task = self.session.query(Task).one()
        assert generated_task.tags == [tag]

    def test_add_task_generates_tag_if_doesnt_exist(self):
        title = self.fake.sentence()

        self.manager.add(title=title, tags=['non_existent'])

        generated_task = self.session.query(Task).one()
        tag = self.session.query(Tag).get('non_existent')

        assert generated_task.tags == [tag]
        assert isinstance(tag, Tag)

    def test_add_task_assigns_priority_if_exist(self):
        title = self.fake.sentence()
        priority = self.fake.random_number()

        self.manager.add(title=title, priority=priority)

        generated_task = self.session.query(Task).one()
        assert generated_task.priority == priority

    def test_add_task_assigns_value_if_exist(self):
        title = self.fake.sentence()
        value = self.fake.random_number()

        self.manager.add(title=title, value=value)

        generated_task = self.session.query(Task).one()
        assert generated_task.value == value

    def test_add_task_assigns_willpower_if_exist(self):
        title = self.fake.sentence()
        willpower = self.fake.random_number()

        self.manager.add(title=title, willpower=willpower)

        generated_task = self.session.query(Task).one()
        assert generated_task.willpower == willpower

    def test_add_task_assigns_fun_if_exist(self):
        title = self.fake.sentence()
        fun = self.fake.random_number()

        self.manager.add(title=title, fun=fun)

        generated_task = self.session.query(Task).one()
        assert generated_task.fun == fun

    def test_add_task_assigns_estimate_if_exist(self):
        title = self.fake.sentence()
        estimate = self.fake.random_number()

        self.manager.add(title=title, estimate=estimate)

        generated_task = self.session.query(Task).one()
        assert generated_task.estimate == estimate

    def test_add_task_assigns_body_if_exist(self):
        title = self.fake.sentence()
        body = self.fake.sentence()

        self.manager.add(title=title, body=body)

        generated_task = self.session.query(Task).one()
        assert generated_task.body == body

    def test_add_task_assigns_default_agile_state_if_not_specified(self):
        title = self.fake.sentence()

        self.manager.add(title=title)

        generated_task = self.session.query(Task).one()
        assert generated_task.agile == \
            pydo_default_config['task.default.agile']['default']

    def test_raise_error_if_add_task_assigns_unvalid_agile_state(self):
        title = self.fake.sentence()
        agile = self.fake.word()

        with pytest.raises(ValueError):
            self.manager.add(title=title, agile=agile)

    def test_add_task_assigns_agile_if_exist(self):
        title = self.fake.sentence()
        agile = 'todo'

        self.manager.add(title=title, agile=agile)

        generated_task = self.session.query(Task).one()
        assert generated_task.agile == agile

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
        assert modified_task.title == task.title
        assert modified_task.state == 'deleted'
        self.log_debug.assert_called_with(
            'Deleted task {}: {}'.format(
                modified_task.id,
                modified_task.title,
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
        assert modified_task.title == task.title
        assert modified_task.state == 'deleted'
        self.log_debug.assert_called_with(
            'Deleted task {}: {}'.format(
                modified_task.id,
                modified_task.title,
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
        assert modified_task.title == task.title
        assert modified_task.state == 'completed'
        self.log_debug.assert_called_with(
            'Completed task {}: {}'.format(
                modified_task.id,
                modified_task.title,
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
        assert modified_task.title == task.title
        assert modified_task.state == 'completed'
        self.log_debug.assert_called_with(
            'Completed task {}: {}'.format(
                modified_task.id,
                modified_task.title,
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
