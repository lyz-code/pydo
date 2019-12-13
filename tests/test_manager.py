from faker import Faker
from pydo.manager import TaskManager
from pydo.models import Task
from tests.factories import TaskFactory
from unittest.mock import patch

import pytest
import ulid


class TestTaskManager:

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.datetime_patch = patch('pydo.manager.datetime', autospect=True)
        self.datetime = self.datetime_patch.start()
        self.fake = Faker()
        self.tm = TaskManager(session)
        self.session = session

        yield 'setup'

        self.datetime_patch.stop()

    def test_session_attribute_exists(self):
        assert self.tm.session is self.session

    def test_add_task(self):
        description = self.fake.sentence()

        self.tm.add(description=description)

        generated_task = self.session.query(Task).one()
        assert isinstance(ulid.from_str(generated_task.ulid), ulid.ulid.ULID)
        assert generated_task.description == description
        assert generated_task.state == 'open'

    def test_delete_task(self):
        closed_utc = self.fake.date_time()
        self.datetime.datetime.now.return_value = closed_utc
        task = TaskFactory.create()

        assert self.session.query(Task).one()

        self.tm.delete(task.ulid)

        modified_task = self.session.query(Task).get(task.ulid)
        assert modified_task.closed_utc == closed_utc
        assert modified_task.description == task.description
        assert modified_task.state == 'deleted'

    def test_complete_task(self):
        closed_utc = self.fake.date_time()
        self.datetime.datetime.now.return_value = closed_utc
        task = TaskFactory.create()

        assert self.session.query(Task).one()

        self.tm.complete(task.ulid)

        modified_task = self.session.query(Task).get(task.ulid)
        assert modified_task.closed_utc == closed_utc
        assert modified_task.description == task.description
        assert modified_task.state == 'done'
