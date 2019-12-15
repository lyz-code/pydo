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
            columns (list): Element attributes to print
            labels (list): Headers of the attributes
        """
        tasks = self.session.query(Task).filter_by(state='open')

        # Remove columns that have all nulls
        for attribute in columns:
            if tasks.filter(getattr(Task, attribute).is_(None)).count() == \
                    tasks.count():
                index_to_remove = columns.index(attribute)
                columns.pop(index_to_remove)
                labels.pop(index_to_remove)

        task_data = [
            [
                task.__getattribute__(attribute)
                for attribute in columns
            ]
            for task in sorted(
                tasks.all(),
                key=lambda k: k.id,
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
