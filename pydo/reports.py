"""
Module to store the pydo reports

Classes:
    BaseReport: Abstract class to gather common report methods and attributes.
    List: Class to print the list report.
"""

from pydo.fulids import fulid
from pydo.models import Task, Project, Tag
from pydo.manager import ConfigManager
from tabulate import tabulate


class BaseReport():
    """
    Abstract class to gather common report methods and attributes.

    Arguments:
        session: Database session.
        config: ConfigManager object.

    Public attributes:
        session: Database session.
        config: ConfigManager object.

    Internal methods:
        _date2str: Returns a string with the config report.date_format format
    """

    def __init__(self, session):
        self.session = session
        self.config = ConfigManager(session)

    def _date2str(self, date):
        """
        Method to convert a datetime object into a string with the format
        specified in the report.date_format configuration.

        Arguments:
            date (datetime or None): Object to convert.

        Returns:
            str: converted date string.
        """
        try:
            return date.strftime(self.config.get('report.date_format'))
        except AttributeError:
            return None


class List(BaseReport):
    """
    Class to print the list report.

    Arguments:
        session: Database session.
        config: ConfigManager object.

    Public methods:
        print: Method to print the report.

    Internal methods:

    Public attributes:
        session: Database session.
    """

    def __init__(self, session):
        super().__init__(session)

    def _remove_null_columns(self, tasks, columns, labels):
        """
        Method to remove the columns that have all null items.

        Arguments:
            tasks (session.query): A Task session query
            columns (list): Element attributes to print
            labels (list): Headers of the attributes
        """
        for attribute in columns.copy():
            remove_attribute = False
            try:
                # Task with attribute == None
                if tasks.filter(getattr(Task, attribute).is_(None)).count() \
                        == tasks.count():
                    remove_attribute = True
            except NotImplementedError:
                # Task with empty relationship
                if tasks.filter(getattr(Task, attribute).any()).count() == 0:
                    remove_attribute = True
            if remove_attribute:
                index_to_remove = columns.index(attribute)
                columns.pop(index_to_remove)
                labels.pop(index_to_remove)
        return columns, labels

    def print(self, columns, labels):
        """
        Method to print the report

        Arguments:
            columns (list): Element attributes to print
            labels (list): Headers of the attributes
        """
        report_data = []
        tasks = self.session.query(Task).filter_by(state='open')

        columns, labels = self._remove_null_columns(tasks, columns, labels)

        # Transform the fulids into sulids
        sulids = fulid(
            self.config.get('fulid.characters'),
            self.config.get('fulid.forbidden_characters'),
        ).sulids([task.id for task in tasks])

        for task in sorted(
            tasks.all(),
            key=lambda k: k.id,
            reverse=True
        ):
            task_report = []
            for attribute in columns:
                if attribute == 'id':
                    task.sulid = sulids[task.id]
                    task_report.append(task.sulid)
                elif attribute == 'tags':
                    if len(task.tags) != 0:
                        task_report.append(
                            ', '.join([tag.id for tag in task.tags])
                        )
                    else:
                        task_report.append('')
                elif attribute == 'due':
                    task_report.append(self._date2str(task.due))
                else:
                    task_report.append(task.__getattribute__(attribute))
            report_data.append(task_report)
        print(tabulate(report_data, headers=labels, tablefmt='simple'))


class Projects(BaseReport):
    """
    Class to print the projects report.

    Arguments:
        session: Database session.
        config: ConfigManager object.

    Public methods:
        print: print report.

    Internal methods:

    Public attributes:
        session: Database session.
        config: ConfigManager object.
    """

    def __init__(self, session):
        super().__init__(session)

    def print(self, columns, labels):
        """
        Method to print the report

        Arguments:
            columns (list): Element attributes to print
            labels (list): Headers of the attributes
        """
        report_data = []

        # Gather tasks without project
        tasks_without_project = self.session.query(Task).\
            filter_by(state='open').filter_by(project_id=None).count()

        if tasks_without_project > 0:
            report_data.append(
                [
                    'None',
                    tasks_without_project,
                    'Tasks without project'
                ]
            )

        # Gather project tasks
        active_projects = self.session.query(Project)

        for project in sorted(
            active_projects.all(),
            key=lambda k: k.id,
            reverse=True,
        ):
            open_tasks = [
                task for task in project.tasks if task.state == 'open'
            ]

            if len(open_tasks) > 0:
                report_data.append(
                    [
                        project.id,
                        len(open_tasks),
                        project.description
                    ]
                )

        print(tabulate(report_data, headers=labels, tablefmt='simple'))


class Tags(BaseReport):
    """
    Class to print the tags report.

    Arguments:
        session: Database session.
        config: ConfigManager object.

    Public methods:
        print: print report.

    Internal methods:

    Public attributes:
        session: Database session.
        config: ConfigManager object.
    """

    def __init__(self, session):
        super().__init__(session)

    def print(self, columns, labels):
        """
        Method to print the report

        Arguments:
            columns (list): Element attributes to print
            labels (list): Headers of the attributes
        """
        report_data = []

        # Gather tag tasks
        tags = self.session.query(Tag)

        for tag in sorted(
            tags.all(),
            key=lambda k: k.id,
            reverse=True,
        ):
            open_tasks = [
                task for task in tag.tasks if task.state == 'open'
            ]

            if len(open_tasks) > 0:
                report_data.append(
                    [
                        tag.id,
                        len(open_tasks),
                        tag.description
                    ]
                )

        print(tabulate(report_data, headers=labels, tablefmt='simple'))
