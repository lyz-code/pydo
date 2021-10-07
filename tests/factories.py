"""Define the factories for the tests."""

from datetime import datetime
from random import SystemRandom
from typing import Optional

import factory
from faker import Faker
from faker_enum import EnumProvider

from pydo.model.task import RecurrenceType, RecurrentTask, Task, TaskState

factory.Faker.add_provider(EnumProvider)

faker = Faker()  # type: ignore


class TaskFactory(factory.Factory):  # type: ignore
    """Generate a fake task."""

    id_ = factory.Faker("pyint")
    state = factory.Faker("enum", enum_cls=TaskState)
    subtype = "task"
    active = True
    area = factory.Faker("word")
    priority = factory.Faker("random_number")
    description = factory.Faker("sentence")

    # Let half the tasks have a due date

    @factory.lazy_attribute
    def due(self) -> Optional[datetime]:
        """Generate the due date for half of the tasks."""
        if SystemRandom().random() > 0.5:
            return faker.date_time()
        return None

    @factory.lazy_attribute
    def closed(self) -> factory.Faker:
        """Generate the closed date for the tasks with completed or deleted state."""
        if self.state == "completed" or self.state == "deleted":
            return faker.date_time()
        return None

    class Meta:
        """Configure factoryboy class."""

        model = Task


class RecurrentTaskFactory(TaskFactory):
    """Generate a fake recurrent task."""

    recurrence = factory.Faker("word", ext_word_list=["1d", "1rmo", "1y2mo30s"])
    recurrence_type = factory.Faker("enum", enum_cls=RecurrenceType)
    due = factory.Faker("date_time")
    subtype = "recurrent_task"

    class Meta:
        """Configure factoryboy class."""

        model = RecurrentTask
