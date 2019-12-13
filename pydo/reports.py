"""
Module to store the pydo reports

Classes:
    List: Class to print the list report.
"""
from pydo.models import Task
from tabulate import tabulate


class List():
    """
    Class to print the list report.

    Arguments:
        session: Database session.

    Public methods:
        print: Method to print the report.

    Internal methods:

    Public attributes:
        session: Database session.
    """

    def __init__(self, session):
        self.session = session

    def print(self, columns, labels):
        """
        Method to print the report

        Arguments:
            columns (tuple): Element attributes to print
            labels (tuple): Headers of the attributes
        """
        tasks = self.session.query(Task).filter_by(state='open')
        task_data = [
            [task.ulid, task.description]
            for task in sorted(
                tasks,
                key=lambda k: k.state,
                reverse=True,
            )
        ]
        print(
            tabulate(
                task_data,
                headers=labels,
                tablefmt='simple'
            )
        )
