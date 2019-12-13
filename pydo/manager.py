"""
Module to store the main class of pydo

Classes:
    TaskManager: Class to manipulate the tasks data
"""
from pydo.models import Task

import datetime
import ulid


class TaskManager():
    """
    Class to manipulate the tasks data.

    Arguments:
        session: Database session

    Public methods:
        add: Creates a new task.
        delete: Deletes a task.
        done: Completes a task.

    Internal methods:
        _close: Closes a task.

    Public attributes:
        session: Database session
    """

    def __init__(self, session):
        self.session = session

    def add(self, description, project=None):
        """
        Method to create a new task

        Arguments:
            description (str): Description of the task
            project (str): Task project
        """

        task = Task(
            ulid=ulid.new().str,
            description=description,
            state='open',
            project=project,
        )
        self.session.add(task)
        self.session.commit()

    def _close(self, id, state):
        """
        Method to close a task

        Arguments:
            id (str): Ulid of the task
            state (str): State of the task once it's closed
        """

        task = self.session.query(Task).get(id)

        task.state = state
        task.closed_utc = datetime.datetime.now()

        self.session.commit()

    def delete(self, id):
        """
        Method to delete a task

        Arguments:
            id (str): Ulid of the task
        """

        self._close(id, 'deleted')

    def complete(self, id):
        """
        Method to complete a task

        Arguments:
            id (str): Ulid of the task
        """

        self._close(id, 'done')
