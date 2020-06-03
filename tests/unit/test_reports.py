from faker import Faker
from pydo import config
from pydo.models import RecurrentTask, Task
from pydo.reports import TaskReport, Projects, Tags
from tests.factories import \
    ProjectFactory, \
    RecurrentTaskFactory, \
    TagFactory, \
    TaskFactory
from unittest.mock import patch

import pytest


class BaseReport:
    """
    Abstract base test class to ensure that all the reporst have the same
    interface.

    The Children classes must define the following attributes:
        self.report: The report class to test.

    Public attributes:
        print (mock): print mock.
        fake (Faker object): Faker object.
        tabulate (mock): tabulate mock.
        session (Session object): Database session.
    """

    @pytest.fixture(autouse=True)
    def base_setup(self, session):
        self.print_patch = patch('pydo.reports.print', autospect=True)
        self.print = self.print_patch.start()
        self.fake = Faker()
        self.tabulate_patch = patch(
            'pydo.reports.tabulate',
            autospect=True
        )
        self.tabulate = self.tabulate_patch.start()
        self.session = session

        yield 'base_setup'

        self.print_patch.stop()
        self.tabulate_patch.stop()

    def test_session_attribute_exists(self):
        assert self.report.session is self.session

    def test_date_to_string_converts_with_desired_format(self):
        date = self.fake.date_time()
        assert self.report._date2str(date) == date.strftime(
            config.get('report.date_format')
        )

    def test_date_to_string_converts_None_to_None(self):
        assert self.report._date2str(None) is None


@pytest.mark.usefixtures('base_setup')
class TestTaskReport(BaseReport):
    """
    Class to test the TaskReport report.

    Public attributes:
        print (mock): print mock.
        fake (Faker object): Faker object.
        tabulate (mock): tabulate mock.
        session (Session object): Database session.
    """

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.report = TaskReport(session)
        self.columns = config.get('report.open.columns').copy()
        self.labels = config.get('report.open.labels').copy()

        yield 'setup'

    def test_task_report_has_desired_default_columns(self):
        assert 'id' in self.columns
        assert 'title' in self.columns
        assert 'priority' in self.columns
        assert 'due' in self.columns
        assert 'project_id' in self.columns
        assert 'tags' in self.columns

    def test_remove_null_columns_removes_columns_if_all_nulls(
        self,
        session
    ):
        # If we don't assign a project and tags to the tasks they are all
        # going to be null.
        desired_columns = self.columns.copy()
        desired_labels = self.labels.copy()

        project_index = desired_columns.index('project_id')
        desired_columns.pop(project_index)
        desired_labels.pop(project_index)

        tags_index = desired_columns.index('tags')
        desired_columns.pop(tags_index)
        desired_labels.pop(tags_index)

        due_index = desired_columns.index('due')
        desired_columns.pop(due_index)
        desired_labels.pop(due_index)

        TaskFactory.create_batch(100, due=None)

        tasks = session.query(Task).filter_by(state='open')

        columns, labels = self.report._remove_null_columns(
            tasks,
            self.columns,
            self.labels
        )

        assert desired_columns == columns
        assert desired_labels == labels

    def test_remove_null_columns_doesnt_fail_if_column_doesnt_exist(
        self,
        session
    ):
        desired_columns = ['id', 'title']
        columns = desired_columns.copy()
        columns.append('unexistent_column')
        desired_labels = ['Id', 'Title']
        labels = desired_labels.copy()
        labels.append('unexistent_label')

        TaskFactory.create_batch(100, due=None)

        tasks = session.query(Task).filter_by(state='open')

        result_columns, result_labels = self.report._remove_null_columns(
            tasks,
            columns,
            labels
        )

        assert result_columns == desired_columns
        assert result_labels == desired_labels

    def test_task_report_prints_id_title_and_project_if_project_existent(self):
        project = ProjectFactory.create()
        tasks = TaskFactory.create_batch(2, state='open')
        tasks[0].project = project
        self.session.commit()

        id_index = self.columns.index('id')
        project_index = self.columns.index('project_id')

        columns = [
            self.columns[id_index],
            self.columns[project_index],
        ]
        labels = [
            self.labels[id_index],
            self.labels[project_index],
        ]
        tasks_query = self.session.query(Task).filter_by(state='open')

        self.report.print(tasks=tasks_query, columns=columns, labels=labels)

        # Prepare desired report
        report_data = []
        for task in sorted(tasks, key=lambda k: k.id, reverse=True):
            task_report = []
            for attribute in columns:
                if attribute == 'id':
                    task_report.append(task.sulid)
                else:
                    task_report.append(task.__getattribute__(attribute))
            report_data.append(task_report)

        self.tabulate.assert_called_once_with(
            report_data,
            headers=labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_task_report_print_id_title_and_tags_if_present(self):
        tasks = TaskFactory.create_batch(4, state='open')
        tags = TagFactory.create_batch(2)

        # Add tags to task
        tasks[0].tags = tags
        self.session.commit()

        # Select columns to print
        id_index = self.columns.index('id')
        tags_index = self.columns.index('tags')
        columns = [
            self.columns[id_index],
            self.columns[tags_index],
        ]
        labels = [
            self.labels[id_index],
            self.labels[tags_index],
        ]
        tasks_query = self.session.query(Task).filter_by(state='open')

        self.report.print(tasks=tasks_query, columns=columns, labels=labels)

        # Prepare desired report
        report_data = []
        for task in sorted(tasks, key=lambda k: k.id, reverse=True):
            task_report = []
            for attribute in columns:
                if attribute == 'id':
                    task_report.append(task.sulid)
                elif attribute == 'tags':
                    if len(task.tags) > 0:
                        task_report.append(
                            ', '.join([tag.id for tag in tags])
                        )
                    else:
                        task_report.append('')
            report_data.append(task_report)

        self.tabulate.assert_called_once_with(
            report_data,
            headers=labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_task_report_print_id_and_due_if_present(self):
        tasks = TaskFactory.create_batch(10, state='open')

        id_index = self.columns.index('id')
        due_index = self.columns.index('due')

        columns = [
            self.columns[id_index],
            self.columns[due_index],
        ]
        labels = [
            self.labels[id_index],
            self.labels[due_index],
        ]
        tasks_query = self.session.query(Task).filter_by(state='open')

        self.report.print(tasks=tasks_query, columns=columns, labels=labels)

        # Prepare desired report
        report_data = []
        for task in sorted(tasks, key=lambda k: k.id, reverse=True):
            task_report = []
            for attribute in columns:
                if attribute == 'id':
                    task_report.append(task.sulid)
                else:
                    task_report.append(self.report._date2str(task.due))
            report_data.append(task_report)

        self.tabulate.assert_called_once_with(
            report_data,
            headers=labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_task_report_print_doesnt_fail_if_some_tasks_doesnt_have_attr(
        self,
        session
    ):
        # The Task tasks don't have `recurrence` attribute

        columns = ['id', 'recurrence']
        labels = ['Id', 'Recurrence']

        self.report = TaskReport(session, RecurrentTask)
        TaskFactory.create_batch(10, state='open')
        RecurrentTaskFactory.create_batch(10, state='open')

        tasks = session.query(Task).filter_by(state='open')

        self.report.print(tasks, columns, labels)

    def test_task_report_print_fills_empty_if_task_doesnt_have_attr(
        self,
        session
    ):
        # If it doesn't get filled by an empty value, it will get filled with
        # the next attribute data.

        # The Task tasks don't have `recurrence` attribute

        columns = ['id', 'recurrence']
        labels = ['Id', 'Recurrence']

        self.report = TaskReport(session, RecurrentTask)
        TaskFactory.create_batch(1, state='open')
        # RecurrentTaskFactory.create_batch(1, state='open')

        tasks = session.query(Task).filter_by(state='open')

        self.report.print(tasks, columns, labels)
        self.tabulate.assert_called_once_with(
            [['a', '']],
            headers=labels,
            tablefmt='simple',
        )


@pytest.mark.usefixtures('base_setup')
class TestProjects(BaseReport):
    """
    Class to test the Projects report.

    Public attributes:
        print (mock): print mock.
        fake (Faker object): Faker object.
        tabulate (mock): tabulate mock.
        session (Session object): Database session.
    """

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.report = Projects(session)
        self.columns = config.get('report.projects.columns')
        self.labels = config.get('report.projects.labels')
        self.tasks = TaskFactory.create_batch(20, state='open')

        yield 'setup'

    def test_report_prints_projects_with_tasks(self):
        project = ProjectFactory.create()

        # Project assignment
        for task in self.tasks:
            task.project = project
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [
                [project.id, 20, project.description],
            ],
            headers=self.labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_print_projects_without_tasks(self):
        project = ProjectFactory.create()

        # empty project
        ProjectFactory.create()

        # Project assignment
        for task in self.tasks:
            task.project = project
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [
                [project.id, 20, project.description],
            ],
            headers=self.labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_print_projects_without_open_tasks(self):
        project = ProjectFactory.create()
        project_with_closed_tasks = ProjectFactory.create()

        completed_task = TaskFactory.create(state='completed')
        completed_task.project = project_with_closed_tasks
        deleted_task = TaskFactory.create(state='deleted')
        deleted_task.project = project_with_closed_tasks

        # Project assignment
        for task in self.tasks:
            task.project = project
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [
                [project.id, 20, project.description],
            ],
            headers=self.labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_count_completed_tasks_in_projects(self):
        project = ProjectFactory.create()

        # Project assignment
        for task in self.tasks:
            task.project = project

        # Complete one task
        self.tasks[0].state = 'completed'
        self.tasks[1].state = 'deleted'
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [
                [project.id, 18, project.description],
            ],
            headers=self.labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_prints_tasks_without_project(self):
        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [
                ['None', 20, 'Tasks without project'],
            ],
            headers=self.labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)


@pytest.mark.usefixtures('base_setup')
class TestTags(BaseReport):
    """
    Class to test the Tags report.

    Public attributes:
        print (mock): print mock.
        fake (Faker object): Faker object.
        tabulate (mock): tabulate mock.
        session (Session object): Database session.
    """

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.report = Tags(session)
        self.columns = config.get('report.tags.columns')
        self.labels = config.get('report.tags.labels')
        self.tasks = TaskFactory.create_batch(20, state='open')

        yield 'setup'

    def test_report_prints_tags_with_tasks(self):
        tag = TagFactory.create()

        # Tag assignment
        for task in self.tasks:
            task.tags = [tag]
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [
                [tag.id, 20, tag.description],
            ],
            headers=self.labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_print_tags_without_tasks(self):
        tag = TagFactory.create()

        # empty Tag
        TagFactory.create()

        # Tag assignment
        for task in self.tasks:
            task.tags = [tag]
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [
                [tag.id, 20, tag.description],
            ],
            headers=self.labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_print_tags_without_open_tasks(self):
        tag = TagFactory.create()
        tag_with_closed_tasks = TagFactory.create()

        completed_task = TaskFactory.create(state='completed')
        completed_task.tags = [tag_with_closed_tasks]
        deleted_task = TaskFactory.create(state='deleted')
        deleted_task.tags = [tag_with_closed_tasks]

        # Tag assignment
        for task in self.tasks:
            task.tags = [tag]
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [
                [tag.id, 20, tag.description],
            ],
            headers=self.labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_count_completed_tasks_in_tags(self):
        tag = TagFactory.create()

        # Tag assignment
        for task in self.tasks:
            task.tags = [tag]

        # Complete one task
        self.tasks[0].state = 'completed'
        self.tasks[1].state = 'deleted'
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [
                [tag.id, 18, tag.description],
            ],
            headers=self.labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_print_tasks_without_tag(self):
        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [],
            headers=self.labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)
