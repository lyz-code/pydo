"""
Module to store the main class of pydo

Classes:
    TaskManager: Class to manipulate the tasks data
"""
from pydo.models import Task


class TaskManager():
    """
    Class to manipulate the tasks data.

    Arguments:

    Public methods:

    Internal methods:

    Public attributes:
    """

    def __init__(self, session):
        self.session = session

    def seed(self):
        pass
