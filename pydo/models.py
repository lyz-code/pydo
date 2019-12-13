"""
Module to store the models.

Classes:
    Task: task model
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

import os

possible_task_states = [
    'open',
    'deleted',
    'completed',
]

db_path = os.path.expanduser('~/.local/share/pydo/main.db')
engine = create_engine(
    os.environ.get('PYDO_DATABASE_URL') or 'sqlite:///' + db_path
)

Base = declarative_base(bind=engine)


class Task(Base):
    """
    Class to define the task model.
    """
    __tablename__ = 'task'
    ulid = Column(String, primary_key=True, doc='ULID of creation')
    closed_utc = Column(DateTime, doc='Closed datetime')
    description = Column(String, nullable=False, doc='Task description')
    state = Column(
        String,
        nullable=False,
        doc='Possible states of the task:{}'.format(str(possible_task_states))
    )
    project = Column(String, doc='Task project')

    def __init__(self, ulid, description, project=None, state=None):
        self.ulid = ulid
        self.description = description
        self.project = project
        self.state = state


class Config(Base):
    """
    Class to define the pydo configuration model.
    """
    __tablename__ = 'config'
    property = Column(String, primary_key=True, doc="Property identifier")
    default = Column(
        String,
        nullable=False,
        doc="Default value of the property"
    )

    description = Column(
        String,
        doc="Property description"
    )

    user = Column(
        String,
        doc="User defined value of the property"
    )

    choices = Column(
        String,
        doc="JSON list of possible values"
    )

    def __init__(
        self,
        property,
        default,
        description=None,
        user=None,
        choices=None
    ):
        self.property = property
        self.default = default
        self.description = description
        self.user = user
        self.choices = choices
