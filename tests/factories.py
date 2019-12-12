
import factory
import ulid

from pydo.models import Task

possible_states = [
    'open',
    'closed',
]


class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    ulid = factory.LazyFunction(lambda: ulid.new().str)

    description = factory.Faker('sentence')
    state = factory.Faker('word', ext_word_list=possible_states)

    class Meta:
        model = Task
        sqlalchemy_session_persistence = 'commit'
