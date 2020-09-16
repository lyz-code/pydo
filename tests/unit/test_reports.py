# from pydo.model import RecurrentTask, Task
# from pydo.reports import TaskReport, Projects, Tags
# from tests.factories import \
#     ProjectFactory, \
#     RecurrentTaskFactory, \
#     TagFactory, \
#     TaskFactory
from unittest.mock import patch

import pytest
from faker import Faker

from pydo import config


@pytest.mark.skip("Not yet")
class BaseReport:
    """
    Abstract base test class to ensure that all the reporst have the same
    interface.

    The Children classes must define the following attributes:
        self.report: The report class to test.

    Public attributes:
        print (mock): print mock.
        fake (Faker object): Faker object.
        tabulate (mock): tabulate mock.
        session (Session object): Database session.
    """

    @pytest.fixture(autouse=True)
    def base_setup(self, session):
        self.print_patch = patch("pydo.reports.print", autospect=True)
        self.print = self.print_patch.start()
        self.fake = Faker()
        self.tabulate_patch = patch("pydo.reports.tabulate", autospect=True)
        self.tabulate = self.tabulate_patch.start()
        self.session = session

        yield "base_setup"

        self.print_patch.stop()
        self.tabulate_patch.stop()

    def test_session_attribute_exists(self):
        assert self.report.session is self.session

    def test_date_to_string_converts_with_desired_format(self):
        date = self.fake.date_time()
        assert self.report._date2str(date) == date.strftime(
            config.get("report.date_format")
        )

    def test_date_to_string_converts_None_to_None(self):
        assert self.report._date2str(None) is None


@pytest.mark.skip("Not yet")
@pytest.mark.usefixtures("base_setup")
class TestProjects(BaseReport):
    """
    Class to test the Projects report.

    Public attributes:
        print (mock): print mock.
        fake (Faker object): Faker object.
        tabulate (mock): tabulate mock.
        session (Session object): Database session.
    """

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.report = Projects(session)
        self.columns = config.get("report.projects.columns")
        self.labels = config.get("report.projects.labels")
        self.tasks = TaskFactory.create_batch(20, state="open")

        yield "setup"

    def test_report_prints_projects_with_tasks(self):
        project = ProjectFactory.create()

        # Project assignment
        for task in self.tasks:
            task.project = project
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [[project.id, 20, project.description],],
            headers=self.labels,
            tablefmt="simple",
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_print_projects_without_tasks(self):
        project = ProjectFactory.create()

        # empty project
        ProjectFactory.create()

        # Project assignment
        for task in self.tasks:
            task.project = project
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [[project.id, 20, project.description],],
            headers=self.labels,
            tablefmt="simple",
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_print_projects_without_open_tasks(self):
        project = ProjectFactory.create()
        project_with_closed_tasks = ProjectFactory.create()

        completed_task = TaskFactory.create(state="completed")
        completed_task.project = project_with_closed_tasks
        deleted_task = TaskFactory.create(state="deleted")
        deleted_task.project = project_with_closed_tasks

        # Project assignment
        for task in self.tasks:
            task.project = project
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [[project.id, 20, project.description],],
            headers=self.labels,
            tablefmt="simple",
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_count_completed_tasks_in_projects(self):
        project = ProjectFactory.create()

        # Project assignment
        for task in self.tasks:
            task.project = project

        # Complete one task
        self.tasks[0].state = "completed"
        self.tasks[1].state = "deleted"
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [[project.id, 18, project.description],],
            headers=self.labels,
            tablefmt="simple",
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_prints_tasks_without_project(self):
        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [["None", 20, "Tasks without project"],],
            headers=self.labels,
            tablefmt="simple",
        )
        self.print.assert_called_once_with(self.tabulate.return_value)


@pytest.mark.skip("Not yet")
@pytest.mark.usefixtures("base_setup")
class TestTags(BaseReport):
    """
    Class to test the Tags report.

    Public attributes:
        print (mock): print mock.
        fake (Faker object): Faker object.
        tabulate (mock): tabulate mock.
        session (Session object): Database session.
    """

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.report = Tags(session)
        self.columns = config.get("report.tags.columns")
        self.labels = config.get("report.tags.labels")
        self.tasks = TaskFactory.create_batch(20, state="open")

        yield "setup"

    def test_report_prints_tags_with_tasks(self):
        tag = TagFactory.create()

        # Tag assignment
        for task in self.tasks:
            task.tags = [tag]
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [[tag.id, 20, tag.description],], headers=self.labels, tablefmt="simple"
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_print_tags_without_tasks(self):
        tag = TagFactory.create()

        # empty Tag
        TagFactory.create()

        # Tag assignment
        for task in self.tasks:
            task.tags = [tag]
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [[tag.id, 20, tag.description],], headers=self.labels, tablefmt="simple"
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_print_tags_without_open_tasks(self):
        tag = TagFactory.create()
        tag_with_closed_tasks = TagFactory.create()

        completed_task = TaskFactory.create(state="completed")
        completed_task.tags = [tag_with_closed_tasks]
        deleted_task = TaskFactory.create(state="deleted")
        deleted_task.tags = [tag_with_closed_tasks]

        # Tag assignment
        for task in self.tasks:
            task.tags = [tag]
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [[tag.id, 20, tag.description],], headers=self.labels, tablefmt="simple"
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_count_completed_tasks_in_tags(self):
        tag = TagFactory.create()

        # Tag assignment
        for task in self.tasks:
            task.tags = [tag]

        # Complete one task
        self.tasks[0].state = "completed"
        self.tasks[1].state = "deleted"
        self.session.commit()

        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [[tag.id, 18, tag.description],], headers=self.labels, tablefmt="simple"
        )
        self.print.assert_called_once_with(self.tabulate.return_value)

    def test_report_does_not_print_tasks_without_tag(self):
        self.report.print(columns=self.columns, labels=self.labels)

        self.tabulate.assert_called_once_with(
            [], headers=self.labels, tablefmt="simple"
        )
        self.print.assert_called_once_with(self.tabulate.return_value)
