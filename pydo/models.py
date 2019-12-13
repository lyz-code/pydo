"""
Module to store the models.

Classes:
    Task:
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

import os

possible_task_states = [
    'open',
    'deleted',
    'done',
]

db_path = os.path.expanduser('~/.local/share/pydo/main.db')
engine = create_engine(
    os.environ.get('PYDO_DATABASE_URL') or 'sqlite:///' + db_path
)

Base = declarative_base(bind=engine)


class Task(Base):
    __tablename__ = 'task'
    ulid = Column(String, primary_key=True)
    closed_utc = Column(DateTime)
    description = Column(String, nullable=False)
    state = Column(String, nullable=False)
    project = Column(String)

    def __init__(self, ulid, description, project, state):
        self.ulid = ulid
        self.description = description
        self.project = project
        self.state = state


# class Config(Base):
#     __tablename__ = 'config'
#     property = Column(String, primary_key=True)
#     value = Column(String, nullable=False)
