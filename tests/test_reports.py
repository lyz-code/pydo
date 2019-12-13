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
            'pydo.reports.tabulate.tabulate',
            autospect=True
        )
        self.tabulate = self.tabulate_patch.start()

        self.fake = Faker()
        self.ls = List(session)
        self.session = session
        self.tasks = TaskFactory.create_batch(20)
        self.open_tasks = [task for task in self.tasks if task.state == 'open']
        self.complete_tasks = [
            task for task in self.tasks if task.state == 'done'
        ]
        self.deleted_tasks = [
            task for task in self.tasks if task.state == 'deleted'
        ]

        yield 'setup'

        self.print_patch.stop()
        self.tabulate_patch.stop()

    def test_session_attribute_exists(self):
        assert self.ls.session is self.session

    def test_list_open(self):
        columns = ('ulid', 'description')
        labels = ('ID', 'Description')

        self.ls.print(columns=columns, labels=labels)

        self.tabulate.assert_called_once_with(
            [
                [task.ulid, task.description]
                for task in sorted(
                    self.open_tasks,
                    key=lambda k: k.state,
                    reverse=True,
                )
            ],
            headers=labels,
            tablefmt='simple'
        )
        self.print.assert_called_once_with(self.tabulate.return_value)
