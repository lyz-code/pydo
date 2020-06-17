"""
Module to store the models.

Classes:
    Task: task model
"""

# from pydo import engine
from sqlalchemy import \
    create_engine, \
    Column, \
    DateTime, \
    Float, \
    ForeignKey, \
    Integer, \
    String, \
    Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from pydo import config

import os

db_path = os.path.expanduser('~/.local/share/pydo/main.db')
engine = create_engine(
    os.environ.get('PYDO_DATABASE_URL') or 'sqlite:///' + db_path
)

Base = declarative_base(bind=engine)

# Association tables

task_tag_association_table = Table(
    'task_tag_association',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('task.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)

# Tables


class Task(Base):
    """
    Class to define the task model.
    """
    __tablename__ = 'task'
    id = Column(String, primary_key=True, doc='fulid of creation')
    agile = Column(String, doc='Task agile state')
    body = Column(String, doc='Task description')
    due = Column(DateTime, doc='Due datetime')
    closed = Column(DateTime, doc='Closed datetime')
    wait = Column(DateTime, doc='Wait datetime')
    title = Column(String, nullable=False, doc='Task title')
    state = Column(
        String,
        nullable=False,
        doc='Possible states of the task:{}'.format(
            str(config['task']['allowed_states'])
        )
    )
    project_id = Column(
        Integer,
        ForeignKey('project.id'),
        doc='Task project id'
    )
    priority = Column(Integer, doc='Task priority')
    estimate = Column(Float, doc='Task estimate size')
    willpower = Column(Integer, doc='Task willpower size')
    value = Column(Integer, doc='Task value')
    fun = Column(Integer, doc='Task fun')
    project = relationship('Project', back_populates='tasks')

    parent_id = Column(String, ForeignKey('task.id'))
    parent = relationship('Task', remote_side=[id], backref='children')

    type = Column(
        String,
        nullable=False,
        doc='Task type: {}'.format(str(config['task']['allowed_types']))
    )
    __mapper_args__ = {
        'polymorphic_identity': 'task',
        'polymorphic_on': type
    }

    tags = relationship(
        'Tag',
        back_populates='tasks',
        secondary=task_tag_association_table
    )


class RecurrentTask(Task):
    __tablename__ = 'recurrent_task'
    id = Column(String, ForeignKey('task.id'), primary_key=True)
    recurrence_type = Column(
        String,
        doc="Recurrence type: ['repeating', 'recurring']"
    )
    recurrence = Column(String, doc='task recurrence in pydo date format')

    __mapper_args__ = {
        'polymorphic_identity': 'recurrent_task',
    }


class Project(Base):
    """
    Class to define the project model.
    """
    __tablename__ = 'project'
    id = Column(String, primary_key=True, doc='Project name')
    description = Column(String, doc='Project description')
    tasks = relationship('Task', back_populates='project')


class Tag(Base):
    """
    Class to define the tag model.
    """

    __tablename__ = 'tag'
    id = Column(String, primary_key=True, doc='Tag name')
    description = Column(String, doc='Tag description')
    tasks = relationship(
        'Task',
        back_populates='tags',
        secondary=task_tag_association_table
    )
