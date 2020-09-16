"""
Module to map the business model to the SQLAlchemy ORM objects.

Functions:
    start_mappers: Function to translate the domain model relationships into
        SQLAlchemy ones.
"""

from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, MetaData,
                        String, Table, Text)
from sqlalchemy.orm import mapper, relationship

from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import RecurrentTask, Task

metadata = MetaData()

# Tables

task = Table(
    "task",
    metadata,
    Column("id", String(64), primary_key=True, doc="Task fulid"),
    Column("agile", String(64), doc="Task agile state"),
    Column("body", Text),
    Column("closed", DateTime),
    Column("created", DateTime),
    Column("due", DateTime),
    Column("estimate", Float, doc="Task estimate size"),
    Column("fun", Integer),
    Column("parent_id", String(64), ForeignKey("task.id")),
    Column("priority", Integer),
    Column("project_id", Integer, ForeignKey("project.id")),
    Column("state", String(64), nullable=False),
    Column("description", String(255), nullable=False),
    Column("type", String(64), nullable=False),
    Column("value", Integer, doc="Task value"),
    Column("wait", DateTime, doc="Wait datetime"),
    Column("willpower", Integer, doc="Task willpower size"),
)

#     project = relationship('Project', back_populates='tasks')
#
#
#     # tags = relationship(
#     #     'Tag',
#     #     back_populates='tasks',
#     #     secondary=task_tag_association_table
#     # )

recurrent_task = Table(
    "recurrent_task",
    metadata,
    Column("id", String(64), ForeignKey("task.id"), primary_key=True),
    Column(
        "recurrence_type", String(64), doc="Recurrence type: ['repeating', 'recurring']"
    ),
    Column("recurrence", String(64), doc="task recurrence in pydo date format"),
)

project = Table(
    "project",
    metadata,
    Column("id", String(64), primary_key=True, doc="Project name"),
    Column("description", String(255), nullable=True),
    Column("state", String(64), nullable=False),
    Column("closed", DateTime),
    Column("created", DateTime),
)

tag = Table(
    "tag",
    metadata,
    Column("id", String(64), primary_key=True, doc="Tag name"),
    Column("description", String(255), nullable=True),
    Column("state", String(64), nullable=False),
    Column("closed", DateTime),
    Column("created", DateTime),
    # tasks = relationship(
    #     'Task',
    #     back_populates='tags',
    #     secondary=task_tag_association_table
    # )
)


# Relationships


def start_mappers():
    """
    Function to translate the domain model relationships into SQLAlchemy ones.
    """

    mapper(Project, project)
    mapper(Tag, tag)
    mapper(
        Task,
        task,
        polymorphic_on=task.c.type,
        polymorphic_identity="task",
        exclude_properties={"recurrence", "recurrence_type"},
        properties={
            "parent": relationship(Task, remote_side=[task.c.id], backref="children"),
            "project": relationship(
                Project, primaryjoin=task.c.project_id == project.c.id, backref="tasks",
            ),
        },
    )
    mapper(RecurrentTask, inherits=Task, polymorphic_identity="recurrent_task")

    # mapper(Batch, batches, properties={
    #     '_allocations': relationship(
    #         lines_mapper,
    #         secondary=allocations,
    #         collection_class=set,
    #     )
    # })


# task_tag_association_table = Table(
#     'task_tag_association',
#     Base.metadata,
#     Column('task_id', Integer, ForeignKey('task.id')),
#     Column('tag_id', Integer, ForeignKey('tag.id'))
# )
