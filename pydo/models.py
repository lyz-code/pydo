"""
Module to store the models.

Classes:
    Task:
"""

from sqlalchemy import Column, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

import os


db_path = os.path.expanduser('~/.local/share/pydo/main.db')
engine = create_engine(
    os.environ.get('PYDO_DATABASE_URL') or 'sqlite:///' + db_path
)

Base = declarative_base(bind=engine)


class Task(Base):
    __tablename__ = 'task'
    ulid = Column(String, primary_key=True)
    description = Column(String, nullable=False)
    state = Column(String, nullable=False)

    def __init__(self, ulid, description, state):
        self.ulid = ulid
        self.description = description
        self.state = state


class TaskState(Base):
    __tablename__ = 'task_state'
    id = Column(String, primary_key=True)

    def __init__(self, id):
        self.id = id
