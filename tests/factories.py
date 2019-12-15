from pydo.models import Task, Config, possible_task_states

import factory
import ulid

# XXX If you add new Factories remember to add the session in conftest.py


class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = factory.LazyFunction(lambda: ulid.new().str)

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
    Class to generate a fake config.
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
