
import factory
import ulid

from pydo.models import Task, possible_task_states


class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    ulid = factory.LazyFunction(lambda: ulid.new().str)

    description = factory.Faker('sentence')
    state = factory.Faker('word', ext_word_list=possible_task_states)

    if state == 'done' or state == 'deleted':
        closed_utc = factory.Faker('DateTime')

    class Meta:
        model = Task
        sqlalchemy_session_persistence = 'commit'
