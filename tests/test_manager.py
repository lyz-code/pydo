from faker import Faker
from pydo.fulids import fulid
from pydo.manager import TaskManager, ConfigManager, DateManager
from pydo.manager import pydo_default_config
from pydo.models import Task, Config, Project, Tag
from tests.factories import \
    ConfigFactory, \
    ProjectFactory, \
    PydoConfigFactory, \
    TagFactory, \
    TaskFactory
from unittest.mock import patch

import datetime
import pytest


class ManagerBaseTest:
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
class TestTaskManager(ManagerBaseTest):
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

    def test_parse_arguments_extracts_tags_to_remove(self):
        title = self.fake.sentence()
        tags = [self.fake.word(), self.fake.word()]

        add_arguments = [
            title,
            '-{}'.format(tags[0]),
            '-{}'.format(tags[1]),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['title'] == title
        assert attributes['tags_rm'] == tags

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

    @patch('pydo.manager.DateManager')
    def test_parse_arguments_extracts_due(self, dateMock):
        self.manager = TaskManager(self.session)
        title = self.fake.sentence()
        due = '1d'
        add_arguments = [
            title,
            'due:{}'.format(due),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['due'] == dateMock.return_value.convert.return_value

    @patch('pydo.manager.DateManager')
    def test_parse_arguments_extracts_due_with_hour(self, dateMock):
        self.manager = TaskManager(self.session)
        title = self.fake.sentence()
        due = '2020-04-05T12:30'
        add_arguments = [
            title,
            'due:{}'.format(due),
        ]

        attributes = self.manager._parse_arguments(add_arguments)

        assert attributes['due'] == dateMock.return_value.convert.return_value

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

    def test_add_task_assigns_due_if_exist(self):
        title = self.fake.sentence()
        due = self.fake.date_time()

        self.manager.add(title=title, due=due)

        generated_task = self.session.query(Task).one()
        assert generated_task.due == due

    def test_modify_task_modifies_project(self):
        old_project = ProjectFactory.create()
        new_project = ProjectFactory.create()
        task = self.factory.create(state='open')
        task.project = old_project

        self.manager.modify(
            fulid().fulid_to_sulid(task.id, [task.id]),
            project_id=new_project.id
        )

        modified_task = self.session.query(Task).get(task.id)

        assert modified_task.project is new_project

    def test_modify_task_generates_project_if_doesnt_exist(self):
        task = self.factory.create(state='open')

        self.manager.modify(
            fulid().fulid_to_sulid(task.id, [task.id]),
            project_id='non_existent')

        modified_task = self.session.query(Task).get(task.id)
        project = self.session.query(Project).get('non_existent')

        assert modified_task.project is project
        assert isinstance(project, Project)

    def test_modify_task_adds_tags(self):
        tag_1 = TagFactory.create()
        tag_2 = TagFactory.create()
        task = self.factory.create(state='open')
        task.tags = [tag_1]

        self.manager.modify(
            fulid().fulid_to_sulid(task.id, [task.id]),
            tags=[tag_2.id])

        modified_task = self.session.query(Task).get(task.id)
        assert modified_task.tags == [tag_1, tag_2]

    def test_modify_task_removes_tags(self):
        tag = TagFactory.create()
        task = self.factory.create(state='open')
        task.tags = [tag]

        self.manager.modify(
            fulid().fulid_to_sulid(task.id, [task.id]),
            tags_rm=[tag.id])

        modified_task = self.session.query(Task).get(task.id)
        assert modified_task.tags == []

    def test_modify_task_generates_tag_if_doesnt_exist(self):
        task = self.factory.create(state='open')

        self.manager.modify(
            fulid().fulid_to_sulid(task.id, [task.id]),
            tags=['non_existent'])

        modified_task = self.session.query(Task).get(task.id)
        tag = self.session.query(Tag).get('non_existent')

        assert modified_task.tags == [tag]
        assert isinstance(tag, Tag)

    def test_modify_task_modifies_priority(self):
        priority = self.fake.random_number()
        task = self.factory.create(state='open')

        self.manager.modify(
            fulid().fulid_to_sulid(task.id, [task.id]),
            priority=priority)

        modified_task = self.session.query(Task).get(task.id)

        assert modified_task.priority == priority

    def test_modify_task_modifies_value(self):
        value = self.fake.random_number()
        task = self.factory.create(state='open')

        self.manager.modify(
            fulid().fulid_to_sulid(task.id, [task.id]),
            value=value)

        modified_task = self.session.query(Task).get(task.id)

        assert modified_task.value == value

    def test_modify_task_modifies_willpower(self):
        willpower = self.fake.random_number()
        task = self.factory.create(state='open')

        self.manager.modify(
            fulid().fulid_to_sulid(task.id, [task.id]),
            willpower=willpower)

        modified_task = self.session.query(Task).get(task.id)

        assert modified_task.willpower == willpower

    def test_modify_task_modifies_fun(self):
        fun = self.fake.random_number()
        task = self.factory.create(state='open')

        self.manager.modify(
            fulid().fulid_to_sulid(task.id, [task.id]),
            fun=fun)

        modified_task = self.session.query(Task).get(task.id)

        assert modified_task.fun == fun

    def test_modify_task_modifies_estimate(self):
        estimate = self.fake.random_number()
        task = self.factory.create(state='open')

        self.manager.modify(
            fulid().fulid_to_sulid(task.id, [task.id]),
            estimate=estimate)

        modified_task = self.session.query(Task).get(task.id)

        assert modified_task.estimate == estimate

    def test_modify_task_modifies_body(self):
        body = self.fake.sentence()
        task = self.factory.create(state='open')

        self.manager.modify(
            fulid().fulid_to_sulid(task.id, [task.id]),
            body=body)

        modified_task = self.session.query(Task).get(task.id)

        assert modified_task.body == body

    def test_raise_error_if_add_task_modifies_unvalid_agile_state(self):
        task = self.factory.create(state='open')
        agile = self.fake.word()

        with pytest.raises(ValueError):
            self.manager.modify(
                fulid().fulid_to_sulid(task.id, [task.id]),
                agile=agile)

    def test_add_task_modifies_agile(self):
        agile = 'todo'
        task = self.factory.create(state='open')

        self.manager.modify(
            fulid().fulid_to_sulid(task.id, [task.id]),
            agile=agile)

        modified_task = self.session.query(Task).get(task.id)

        assert modified_task.agile == agile

    def test_add_task_modifies_due(self):
        due = self.fake.date_time()
        task = self.factory.create(state='open')

        self.manager.modify(
            fulid().fulid_to_sulid(task.id, [task.id]),
            due=due)

        modified_task = self.session.query(Task).get(task.id)

        assert modified_task.due == due

    def test_delete_task_by_sulid(self):
        task = self.factory.create(state='open')
        closed = self.fake.date_time()
        self.datetime.datetime.now.return_value = closed

        assert self.session.query(Task).one()

        self.manager.delete(
            fulid().fulid_to_sulid(task.id, [task.id]),
        )

        modified_task = self.session.query(Task).get(task.id)
        assert modified_task.closed == closed
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
        closed = self.fake.date_time()
        self.datetime.datetime.now.return_value = closed

        assert self.session.query(Task).one()

        self.manager.delete(task.id)

        modified_task = self.session.query(Task).get(task.id)
        assert modified_task.closed == closed
        assert modified_task.title == task.title
        assert modified_task.state == 'deleted'
        self.log_debug.assert_called_with(
            'Deleted task {}: {}'.format(
                modified_task.id,
                modified_task.title,
            )
        )

    def test_complete_task_by_sulid(self):
        closed = self.fake.date_time()
        self.datetime.datetime.now.return_value = closed
        task = TaskFactory.create(state='open')

        assert self.session.query(Task).one()

        self.manager.complete(
            fulid().fulid_to_sulid(task.id, [task.id]),
        )

        modified_task = self.session.query(Task).get(task.id)
        assert modified_task.closed == closed
        assert modified_task.title == task.title
        assert modified_task.state == 'completed'
        self.log_debug.assert_called_with(
            'Completed task {}: {}'.format(
                modified_task.id,
                modified_task.title,
            )
        )

    def test_complete_task_by_fulid(self):
        closed = self.fake.date_time()
        self.datetime.datetime.now.return_value = closed
        task = TaskFactory.create(state='open')

        assert self.session.query(Task).one()

        self.manager.complete(task.id)

        modified_task = self.session.query(Task).get(task.id)
        assert modified_task.closed == closed
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

    def test_date_manager_loaded_in_attribute(self):
        assert isinstance(self.manager.date, DateManager)


class TestDateManager:
    """
    Class to test the DateManager class.

    Public attributes:
        manager (DateManager object): DateManager object to test
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.manager = DateManager()
        self.now = datetime.datetime.now()

        yield 'setup'

    def test_next_weekday_if_starting_weekday_is_smaller(self):
        # Monday
        starting_date = datetime.date(2020, 1, 6)
        next_weekday = self.manager._next_weekday(1, starting_date)
        assert next_weekday == datetime.date(2020, 1, 7)

    def test_next_weekday_if_starting_weekday_is_greater(self):
        # Wednesday
        starting_date = datetime.date(2020, 1, 8)
        next_weekday = self.manager._next_weekday(1, starting_date)
        assert next_weekday == datetime.date(2020, 1, 14)

    def test_next_weekday_if_weekday_is_equal(self):
        # Monday
        starting_date = datetime.date(2020, 1, 6)
        next_weekday = self.manager._next_weekday(0, starting_date)
        assert next_weekday == datetime.date(2020, 1, 13)

    def test_next_monthday_first_day_of_month(self):
        # 1st tuesday of month
        starting_date = datetime.date(2020, 1, 7)
        expected_result = datetime.date(2020, 2, 4)
        assert self.manager._next_monthday(1, starting_date) == expected_result

    def test_next_monthday_second_day_of_month(self):
        # 2st wednesday of month
        starting_date = datetime.date(2020, 1, 8)
        expected_result = datetime.date(2020, 2, 12)
        assert self.manager._next_monthday(1, starting_date) == expected_result

    def test_next_monthday_if_5_monthday(self):
        # 5th monday of month, next month doesn't exist
        starting_date = datetime.date(2019, 12, 30)
        expected_result = datetime.date(2020, 2, 3)
        assert self.manager._next_monthday(1, starting_date) == expected_result

    def test_if_str2date_loads_seconds(self):
        expected_result = self.now + datetime.timedelta(seconds=1)
        assert self.manager._str2date('1s', self.now) == expected_result

    def test_if_str2date_loads_minutes(self):
        expected_result = self.now + datetime.timedelta(minutes=1)
        assert self.manager._str2date('1m', self.now) == expected_result

    def test_if_str2date_loads_hours(self):
        expected_result = self.now + datetime.timedelta(hours=1)
        assert self.manager._str2date('1h', self.now) == expected_result

    def test_if_str2date_loads_days(self):
        expected_result = self.now + datetime.timedelta(days=1)
        assert self.manager._str2date('1d', self.now) == expected_result

    def test_if_str2date_loads_months(self):
        starting_date = datetime.date(2020, 1, 12)
        expected_result = datetime.date(2020, 2, 12)
        assert self.manager._str2date('1mo', starting_date) == expected_result

    def test_if_str2date_loads_weeks(self):
        starting_date = datetime.date(2020, 1, 12)
        expected_result = datetime.date(2020, 1, 19)
        assert self.manager._str2date('1w', starting_date) == expected_result

    def test_if_str2date_loads_months_if_on_31(self):
        starting_date = datetime.date(2020, 1, 31)
        expected_result = datetime.date(2020, 2, 29)
        assert self.manager._str2date('1mo', starting_date) == expected_result

    def test_if_str2date_loads_years(self):
        starting_date = datetime.date(2020, 1, 12)
        expected_result = datetime.date(2021, 1, 12)
        assert self.manager._str2date('1y', starting_date) == expected_result

    def test_if_str2date_loads_relative_months(self):
        # A month is not equal to 30d, it depends on the days of the month,
        # use this in case you want for example the 3rd friday of the month
        starting_date = datetime.datetime(2020, 1, 7)
        expected_result = datetime.datetime(2020, 2, 4)
        assert self.manager._str2date('1rmo', starting_date) == expected_result

    def test_if_str2date_loads_combination_of_strings(self):
        starting_date = datetime.datetime(2020, 1, 7)
        expected_result = datetime.datetime(2021, 2, 8)
        assert self.manager._str2date('1d 1mo 1y', starting_date) == \
            expected_result

    def test_convert_date_accepts_date_year_month_day(self):
        assert self.manager.convert('2019-05-05') == \
            datetime.datetime.strptime('2019-05-05', '%Y-%m-%d')

    def test_convert_date_accepts_date_year_month_day_hour_min(self):
        assert self.manager.convert('2019-05-05T10:00') == \
            datetime.datetime.strptime('2019-05-05T10:00', '%Y-%m-%dT%H:%M')

    def test_convert_date_accepts_monday(self):
        starting_date = datetime.date(2020, 1, 6)
        assert self.manager.convert('monday', starting_date) == \
            datetime.date(2020, 1, 13)

    def test_convert_date_accepts_mon(self):
        starting_date = datetime.date(2020, 1, 6)
        assert self.manager.convert('mon', starting_date) == \
            datetime.date(2020, 1, 13)

    def test_convert_date_accepts_tuesday(self):
        starting_date = datetime.date(2020, 1, 7)
        assert self.manager.convert('tuesday', starting_date) == \
            datetime.date(2020, 1, 14)

    def test_convert_date_accepts_tue(self):
        starting_date = datetime.date(2020, 1, 7)
        assert self.manager.convert('tue', starting_date) == \
            datetime.date(2020, 1, 14)

    def test_convert_date_accepts_wednesday(self):
        starting_date = datetime.date(2020, 1, 8)
        assert self.manager.convert('wednesday', starting_date) == \
            datetime.date(2020, 1, 15)

    def test_convert_date_accepts_wed(self):
        starting_date = datetime.date(2020, 1, 8)
        assert self.manager.convert('wed', starting_date) == \
            datetime.date(2020, 1, 15)

    def test_convert_date_accepts_thursdday(self):
        starting_date = datetime.date(2020, 1, 9)
        assert self.manager.convert('thursdday', starting_date) == \
            datetime.date(2020, 1, 16)

    def test_convert_date_accepts_thu(self):
        starting_date = datetime.date(2020, 1, 9)
        assert self.manager.convert('thu', starting_date) == \
            datetime.date(2020, 1, 16)

    def test_convert_date_accepts_friday(self):
        starting_date = datetime.date(2020, 1, 10)
        assert self.manager.convert('friday', starting_date) == \
            datetime.date(2020, 1, 17)

    def test_convert_date_accepts_fri(self):
        starting_date = datetime.date(2020, 1, 10)
        assert self.manager.convert('fri', starting_date) == \
            datetime.date(2020, 1, 17)

    def test_convert_date_accepts_saturday(self):
        starting_date = datetime.date(2020, 1, 11)
        assert self.manager.convert('saturday', starting_date) == \
            datetime.date(2020, 1, 18)

    def test_convert_date_accepts_sat(self):
        starting_date = datetime.date(2020, 1, 11)
        assert self.manager.convert('sat', starting_date) == \
            datetime.date(2020, 1, 18)

    def test_convert_date_accepts_sunday(self):
        starting_date = datetime.date(2020, 1, 12)
        assert self.manager.convert('sunday', starting_date) == \
            datetime.date(2020, 1, 19)

    def test_convert_date_accepts_sun(self):
        starting_date = datetime.date(2020, 1, 12)
        assert self.manager.convert('sun', starting_date) == \
            datetime.date(2020, 1, 19)

    def test_convert_date_accepts_1d(self):
        starting_date = datetime.date(2020, 1, 12)
        assert self.manager.convert('1d', starting_date) == \
            datetime.date(2020, 1, 13)

    def test_convert_date_accepts_1mo(self):
        starting_date = datetime.date(2020, 1, 12)
        assert self.manager.convert('1mo', starting_date) == \
            datetime.date(2020, 2, 12)

    def test_convert_date_accepts_1rmo(self):
        starting_date = datetime.date(2020, 1, 12)
        assert self.manager.convert('1rmo', starting_date) == \
            datetime.date(2020, 2, 9)

    def test_convert_date_accepts_now(self):
        assert self.manager.convert('now').day == \
            self.now.day

    def test_convert_date_accepts_tomorrow(self):
        starting_date = datetime.date(2020, 1, 12)
        assert self.manager.convert('tomorrow', starting_date) == \
            datetime.date(2020, 1, 13)

    def test_convert_date_accepts_yesterday(self):
        starting_date = datetime.date(2020, 1, 12)
        assert self.manager.convert('yesterday', starting_date) == \
            datetime.date(2020, 1, 11)


@pytest.mark.usefixtures('base_setup')
class TestConfigManager(ManagerBaseTest):
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
