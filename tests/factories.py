from pydo.fulids import fulid
from pydo.manager import ConfigManager
from pydo.models import Task, Config, possible_task_states

import factory

# XXX If you add new Factories remember to add the session in conftest.py


class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = factory.LazyFunction(lambda: fulid().new().str)

    description = factory.Faker('sentence')
    state = factory.Faker('word', ext_word_list=possible_task_states)
    project = factory.Faker('word', ext_word_list=[None, 'music', 'clean'])

    if state == 'done' or state == 'deleted':
        closed_utc = factory.Faker('DateTime')

    class Meta:
        model = Task
        sqlalchemy_session_persistence = 'commit'


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
        model = Config
        sqlalchemy_session_persistence = 'commit'


class PydoConfigFactory:
    """
    Class to generate a pydo fake config.
    """
    def __init__(self, session):
        self.config = ConfigManager(session)

    def create(self):
        self.config.seed()
