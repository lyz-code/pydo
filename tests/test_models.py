from tests.factories import TaskFactory
from pydo.models import Task

import pytest


class TestTask:

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.dummy_task = TaskFactory.create()
        self.task = Task(
            ulid=self.dummy_task.ulid,
            description=self.dummy_task.description,
            state=self.dummy_task.state,
            project=self.dummy_task.project,
        )

    def test_attributes_defined(self):
        assert self.task.ulid == self.dummy_task.ulid
        assert self.task.description == self.dummy_task.description
        assert self.task.state == self.dummy_task.state
        assert self.task.project == self.dummy_task.project
