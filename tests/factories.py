from pydo.fulids import fulid
from pydo.manager import ConfigManager
from pydo.models import Project, Tag, Task, Config, possible_task_states

import factory

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


class ProjectFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Class to generate a fake project.
    """
    id = factory.Sequence(lambda n: 'project_{}'.format(n))
    description = factory.Faker('sentence')

    class Meta:
        model = Project
        sqlalchemy_session_persistence = 'commit'


class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = factory.LazyFunction(lambda: fulid().new().str)

    title = factory.Faker('sentence')
    state = factory.Faker('word', ext_word_list=possible_task_states)
    agile = factory.Faker('word', ext_word_list=['backlog', 'todo', None])
    priority = factory.Faker('random_number')

    if state == 'completed' or state == 'deleted':
        closed_utc = factory.Faker('DateTime')

    class Meta:
        model = Task
        sqlalchemy_session_persistence = 'commit'


class TagFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Class to generate a fake tag.
    """
    id = factory.Sequence(lambda n: 'tag_{}'.format(n))
    description = factory.Faker('sentence')

    class Meta:
        model = Tag
        sqlalchemy_session_persistence = 'commit'
