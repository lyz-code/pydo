from faker import Faker
from pydo.models import Task, Config
from tests.factories import TaskFactory

import json
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


class TestConfig:

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.fake = Faker()
        self.dummy_config = {
            'property': self.fake.word(),
            'default': self.fake.pybool(),
            'user': self.fake.pybool(),
            'description': self.fake.sentence(),
            'choices': json.dumps(self.fake.pylist(5, True, 'str'))
        }
        self.config = Config(
            property=self.dummy_config['property'],
            default=self.dummy_config['default'],
            user=self.dummy_config['user'],
            description=self.dummy_config['description'],
            choices=self.dummy_config['choices']
        )

    def test_attributes_defined(self):
        assert self.config.property == self.dummy_config['property']
        assert self.config.default == self.dummy_config['default']
        assert self.config.user == self.dummy_config['user']
        assert self.config.description == self.dummy_config['description']
        assert self.config.choices == self.dummy_config['choices']
