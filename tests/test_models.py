from pydo.models import Config, RecurrentTask, Project, Tag, Task
from tests.factories import \
    ConfigFactory, \
    RecurrentTaskFactory, \
    ProjectFactory, \
    TagFactory, \
    TaskFactory

import pytest


class BaseModelTest:
    """
    Abstract base test class to refactor model tests.

    The Children classes must define the following attributes:
        self.model: The model object to test.
        self.dummy_instance: A factory object of the model to test.
        self.model_attributes: List of model attributes to test

    Public attributes:
        dummy_instance (Factory_boy object): Dummy instance of the model.
    """

    @pytest.fixture(autouse=True)
    def base_setup(self, session):
        self.session = session

    def test_attributes_defined(self):
        for attribute in self.model_attributes:
            assert getattr(self.model, attribute) == \
                getattr(self.dummy_instance, attribute)


@pytest.mark.usefixtures('base_setup')
class TestTask(BaseModelTest):

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.factory = TaskFactory
        self.dummy_instance = TaskFactory.create()
        self.model = Task(
            id=self.dummy_instance.id,
            agile=self.dummy_instance.agile,
            title=self.dummy_instance.title,
            state=self.dummy_instance.state,
            due=self.dummy_instance.due,
            priority=self.dummy_instance.priority,
        )
        self.model_attributes = [
            'agile',
            'body',
            'estimate',
            'due',
            'fun',
            'id',
            'priority',
            'state',
            'title',
            'value',
            'wait',
            'willpower',
        ]


@pytest.mark.usefixtures('base_setup')
class TestRecurrentTask(BaseModelTest):

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.factory = RecurrentTaskFactory
        self.dummy_instance = RecurrentTaskFactory.create()
        self.model = RecurrentTask(
            id=self.dummy_instance.id,
            agile=self.dummy_instance.agile,
            title=self.dummy_instance.title,
            state=self.dummy_instance.state,
            due=self.dummy_instance.due,
            priority=self.dummy_instance.priority,
            recurrence=self.dummy_instance.recurrence,
            recurrence_type=self.dummy_instance.recurrence_type,
        )
        self.model_attributes = [
            'agile',
            'body',
            'estimate',
            'due',
            'fun',
            'id',
            'priority',
            'recurrence',
            'recurrence_type',
            'state',
            'title',
            'value',
            'wait',
            'willpower',
        ]


@pytest.mark.usefixtures('base_setup')
class TestProject(BaseModelTest):

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.dummy_instance = ProjectFactory.create()
        self.model = Project(
            id=self.dummy_instance.id,
            description=self.dummy_instance.description,
        )
        self.model_attributes = ['id', 'description']


@pytest.mark.usefixtures('base_setup')
class TestConfig(BaseModelTest):

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.dummy_instance = ConfigFactory.create()
        self.model = Config(
            id=self.dummy_instance.id,
            default=self.dummy_instance.default,
            user=self.dummy_instance.user,
            description=self.dummy_instance.description,
            choices=self.dummy_instance.choices,
        )
        self.model_attributes = [
            'id',
            'default',
            'user',
            'description',
            'choices',
        ]


@pytest.mark.usefixtures('base_setup')
class TestTag(BaseModelTest):

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.dummy_instance = TagFactory.create()
        self.model = Tag(
            id=self.dummy_instance.id,
            description=self.dummy_instance.description,
        )
        self.model_attributes = ['id', 'description']
