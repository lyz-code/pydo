from faker import Faker
from pydo.reports import List
from tests.factories import TaskFactory
from unittest.mock import patch

import pytest


class TestList:

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.print_patch = patch('pydo.reports.print', autospect=True)
        self.print = self.print_patch.start()
        self.tabulate_patch = patch(
            'pydo.reports.tabulate',
            autospect=True
        )
        self.tabulate = self.tabulate_patch.start()

        self.fake = Faker()
        self.ls = List(session)
        self.session = session
        self.columns = ['id', 'description', 'project']
        self.labels = ['ID', 'Description', 'Project']

        yield 'setup'

        self.print_patch.stop()
        self.tabulate_patch.stop()

    def test_session_attribute_exists(self):
        assert self.ls.session is self.session

    def test_list_prints_columns(self):
        self.tasks = TaskFactory.create_batch(20)
        self.open_tasks = [task for task in self.tasks if task.state == 'open']

        self.ls.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [
                [
                    task.__getattribute__(attribute)
                    for attribute in self.columns
                ]
                for task in sorted(
                    self.open_tasks,
                    key=lambda k: k.id,
                    reverse=True,
                )
            ],
            headers=self.labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_list_dont_print_column_if_all_null_open(self):
        tasks = TaskFactory.create_batch(20, project=None)
        open_tasks = [task for task in tasks if task.state == 'open']
        final_columns = self.columns.copy()
        final_columns.remove('project')
        final_labels = self.labels.copy()
        final_labels.remove('Project')

        self.ls.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [
                [
                    task.__getattribute__(attribute)
                    for attribute in final_columns
                ]
                for task in sorted(
                    open_tasks,
                    key=lambda k: k.id,
                    reverse=True,
                )
            ],
            headers=final_labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)
