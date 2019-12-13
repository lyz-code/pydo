from faker import Faker
from pydo.models import Task, possible_task_states

import pytest
import ulid


class TestTask:

    @pytest.fixture(autouse=True)
    def setup(self):
        fake = Faker()
        self.task_attributes = {
            'ulid': ulid.new(),
            'description': fake.sentence(),
            'state': fake.word(ext_word_list=possible_task_states),
        }
        self.task = Task(
            ulid=self.task_attributes['ulid'],
            description=self.task_attributes['description'],
            state=self.task_attributes['state'],
        )

    def test_attributes_defined(self):
        assert self.task.ulid == self.task_attributes['ulid']
        assert self.task.description == self.task_attributes['description']
        assert self.task.state == self.task_attributes['state']
