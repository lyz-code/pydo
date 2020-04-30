from pydo.fulids import fulid
from pydo.manager import ConfigManager
from pydo import models

import factory
import random

# XXX If you add new Factories remember to add the session in conftest.py


class ConfigFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Class to generate a fake config element.
    """

    id = factory.Faker('word')
    default = factory.Faker('word')
    user = factory.Faker('word', ext_word_list=[None, 'value_1', 'value_2'])
    description = factory.Faker('sentence')
    choices = factory.Faker(
        'word',
        ext_word_list=[
            None,
            "{['choice1', 'choice2']}",
            "{['choice3', 'choice4']}",
        ])

    class Meta:
        model = models.Config
        sqlalchemy_session_persistence = 'commit'


class PydoConfigFactory:
    """
    Class to generate a pydo fake config.
    """
    def __init__(self, session):
        self.config = ConfigManager(session)

    def create(self):
        self.config.seed()


class ProjectFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Class to generate a fake project.
    """
    id = factory.Sequence(lambda n: 'project_{}'.format(n))
    description = factory.Faker('sentence')

    class Meta:
        model = models.Project
        sqlalchemy_session_persistence = 'commit'


class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = factory.LazyFunction(lambda: fulid().new().str)
    title = factory.Faker('sentence')
    state = factory.Faker('word', ext_word_list=models.possible_task_states)
    agile = factory.Faker('word', ext_word_list=['backlog', 'todo', None])
    type = 'task'
    priority = factory.Faker('random_number')

    # Let half the tasks have a due date

    @factory.lazy_attribute
    def due(self):
        if random.random() > 0.5:
            return factory.Faker('date_time').generate({})

    @factory.lazy_attribute
    def closed(self):
        if self.state == 'completed' or self.state == 'deleted':
            return factory.Faker('date_time').generate({})

    class Meta:
        model = models.Task
        sqlalchemy_session_persistence = 'commit'


class RecurrentTaskFactory(TaskFactory):
    recurrence = factory.Faker(
        'word',
        ext_word_list=['1d', '1rmo', '1y2mo30s']
    )
    recurrence_type = factory.Faker(
        'word',
        ext_word_list=['repeating', 'recurring']
    )

    class Meta:
        model = models.RecurrentTask
        sqlalchemy_session_persistence = 'commit'


class TagFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Class to generate a fake tag.
    """
    id = factory.Sequence(lambda n: 'tag_{}'.format(n))
    description = factory.Faker('sentence')

    class Meta:
        model = models.Tag
        sqlalchemy_session_persistence = 'commit'
