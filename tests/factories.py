from faker import Faker
from pydo.models import Task, possible_task_states

import factory
import ulid


class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    ulid = factory.LazyFunction(lambda: ulid.new().str)

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

    We assume it's initialized

    Arguments:
        session (session object): Database session

    Public methods:
        create: Generates a user configuration in the database

    Public attributes:
        fake (Faker object): Faker object.
        session (Session object): Database session.
    """

    def __init__(self, session):
        self.session = session
        self.fake = Faker()

    def create(self):
        """
        Method to generate a user configuration in the database
        """

        user_config = {
            'verbose_level': self.fake.word(
                ext_word_list=['info', 'debug', 'quiet', None]
            )
        }
        for key, value in user_config.items():
            config = self.session.query.get(key)
            config.user = value
            self.session.add(config)
