"""
Module to test the view implementations.
"""
import re

from pydo import services, views
from tests import factories


class TestGenericReport:
    def test_remove_null_columns_removes_columns_if_all_nulls(self, config):
        tasks = factories.TaskFactory.create_batch(100, due=None, priority="")
        report = views.Report(["ID", "Description", "Due", "Priority"])
        for task in tasks:
            report.add([task.id, task.description, task.due, task.priority])

        report._remove_null_columns()

        assert report.labels == ["ID", "Description"]
        assert report.data[0] == [tasks[0].id, tasks[0].description]

    def test_print_entities_doesnt_fail_if_some_doent_have_an_attr(
        self, config, capsys
    ):
        # The Task tasks don't have `recurrence` attribute, the print should not fail,
        # instead, it should fill it up with blanks

        # Id                          Recurrence
        # --------------------------  ------------
        # 01EJB7M7JS804ZQZ44BAAAAAAA
        # 01EJB7M7JS1XXVG4H3JAAAAAAA
        # 01EJB7M7JT1XWPSZ411AAAAAAA
        # 01EJB7M7JTPVZMM5SRZAAAAAAA  1d
        # 01EJB7M7JT1BF0K2VX4AAAAAAA  1d
        # 01EJB7M7JTZDYE4119BAAAAAAA  1y2mo30s

        columns = ["id", "recurrence"]
        labels = ["ID", "Recurrence"]

        # Generate the tasks
        tasks = factories.TaskFactory.create_batch(3, state="open")
        [
            tasks.append(task)
            for task in factories.RecurrentTaskFactory.create_batch(3, state="open")
        ]

        # Generate the output
        expected_out = [
            r"ID +Recurrence",
            r"-+  -+",
        ]
        for task in tasks:
            try:
                task_str = fr"{task.id} +{task.recurrence}"
            except AttributeError:
                task_str = fr"{task.id}"
            expected_out.append(task_str)

        views._print_entities(config, tasks, columns, labels)

        out, err = capsys.readouterr()
        out = out.splitlines()

        assert len(out) == len(expected_out)
        for line_id in range(0, len(out) - 1):
            assert re.match(expected_out[line_id], out[line_id])

        assert err == ""

    def test_print_entities_can_print_tags(self, config, capsys):

        # ID                          Tags
        # --------------------------  ------
        # 01EKFRS0EXDC9VSMM83AAAAAAA  course
        # 01EKFRS0EXQWQ8S094BAAAAAAA
        # 01EKFRS0EYJR1Z6XWTHAAAAAAA

        columns = ["id", "tags"]
        labels = ["ID", "Tags"]

        # Generate the tasks
        tag = factories.TagFactory.create()
        tasks = factories.TaskFactory.create_batch(3, state="open")
        tasks[0].tags = [tag]

        # Generate the output
        expected_out = [
            r"ID +Tags",
            r"-+  -+",
        ]
        for task in tasks:
            try:
                task_str = fr"{task.id} +{task.tags[0].id}"
            except IndexError:
                task_str = fr"{task.id}"
            expected_out.append(task_str)

        views._print_entities(config, tasks, columns, labels)

        out, err = capsys.readouterr()
        out = out.splitlines()

        assert len(out) == len(expected_out)
        for line_id in range(0, len(out) - 1):
            assert re.match(expected_out[line_id], out[line_id])

        assert err == ""

    def test_print_entities_can_print_projects(self, config, capsys):

        # ID                          Project
        # --------------------------  ------
        # 01EKFRS0EXDC9VSMM83AAAAAAA  course
        # 01EKFRS0EXQWQ8S094BAAAAAAA
        # 01EKFRS0EYJR1Z6XWTHAAAAAAA

        columns = ["id", "project"]
        labels = ["ID", "Project"]

        # Generate the tasks
        project = factories.ProjectFactory.create()
        tasks = factories.TaskFactory.create_batch(3, state="open")
        tasks[0].project = project

        # Generate the output
        expected_out = [
            r"ID +Project",
            r"-+  -+",
        ]
        for task in tasks:
            try:
                task_str = fr"{task.id} +{task.project.id}"
            except AttributeError:
                task_str = fr"{task.id}"
            expected_out.append(task_str)

        views._print_entities(config, tasks, columns, labels)

        out, err = capsys.readouterr()
        out = out.splitlines()

        assert len(out) == len(expected_out)
        for line_id in range(0, len(out) - 1):
            assert re.match(expected_out[line_id], out[line_id])

        assert err == ""


class TestOpenReport:
    def test_open_prints_open_task_attributes(self, repo, config, insert_tasks, capsys):
        tasks = insert_tasks
        short_ids = repo.fulid.sulids([task.id for task in tasks])

        # Build Expected output
        #
        # ID        Description                                          Pri  Due
        # --------  ------------------------------------------------  ------  ----------
        # raaaaaaa  Set recently within soon popular stage election.       7  2026-03-12
        # caaaaaaa  Kind matter change political head series.         630719  2017-06-06
        # gaaaaaaa  Require respond so.                                 8864

        expected_out = [
            r"ID +Description +Pri +Due",
            r"-+  -+  -+  -+",
        ]
        for task in tasks:
            task_str = fr"{short_ids[task.id]} +{task.description} +{task.priority}"
            if task.due is not None:
                task_str += fr" +{task.due}"
            expected_out.append(task_str)

        views.open(repo, config)

        out, err = capsys.readouterr()
        out = out.splitlines()

        assert len(out) == len(expected_out)
        for line_id in range(0, len(out) - 1):
            assert re.match(expected_out[line_id], out[line_id])

        assert err == ""

    def test_open_allows_task_filter(
        self, repo, config, insert_tasks, insert_project, capsys, faker
    ):
        # We are going to create a task that has a special project and filter by it
        # So only that one should be shown

        # Generate the tasks

        project = insert_project
        tasks = insert_tasks
        task_with_project = tasks[0]
        services.modify_tasks(repo, task_with_project.id, {"project_id": project.id})

        # Generate the output
        #
        # ID        Description                 Project      Pri
        # --------  -------------------------  ---------  ---------
        # 6aaaaaaa  Ground of window magazine.    air     489686834

        expected_out = [
            r"ID +Description +Project +Pri",
            r"-+  -+  -+  -+",
            fr"{task_with_project.id} +{task_with_project.description} +{project}"
            fr" +{task_with_project.priority}",
        ]

        views.open(repo, config, {"project_id": project.id})

        out, err = capsys.readouterr()
        out = out.splitlines()

        assert len(out) == len(expected_out)
        for line_id in range(0, len(out) - 1):
            assert re.match(expected_out[line_id], out[line_id])

        assert err == ""


class TestProjectsReport:
    def test_projects_prints_only_counts_open_tasks(
        self, repo, config, insert_tasks, insert_project, capsys
    ):
        # Assign the same project to all the tasks, complete one and delete the other

        project = insert_project
        tasks = insert_tasks

        for task in tasks:
            services.modify_tasks(repo, task.id, {"project_id": project.id})

        services.do_tasks(repo, tasks[1].id)
        services.rm_tasks(repo, tasks[2].id)
        repo.commit()
        capsys.readouterr()

        # Build Expected output

        # Name      Open Tasks  Description
        # ------  ------------  ----------------------
        # west               1  As or later ten happy.

        expected_out = [
            r"Name +Open Tasks +Description",
            r"-+  -+  -+",
            fr"{project.id} *1 *{project.description}",
        ]

        views.projects(repo, config)

        out, err = capsys.readouterr()
        out = out.splitlines()

        assert len(out) == len(expected_out)
        for line_id in range(0, len(out) - 1):
            assert re.match(expected_out[line_id], out[line_id])

        assert err == ""

    def test_projects_prints_only_projects_with_open_tasks(
        self, repo, config, insert_tasks, insert_projects, capsys
    ):
        # Assign a different project to each tasks, complete one and delete the other
        # The report should only show the one with the open task.

        projects = insert_projects
        tasks = insert_tasks

        # Assign one task to each project
        for task_id in range(0, len(tasks)):
            services.modify_tasks(
                repo, tasks[task_id].id, {"project_id": projects[task_id].id}
            )

        # Complete and remove the tasks of two of them
        services.do_tasks(repo, tasks[0].id)
        services.rm_tasks(repo, tasks[2].id)
        repo.commit()
        capsys.readouterr()

        # Build Expected output

        # Name      Open Tasks  Description
        # ------  ------------  ----------------------
        # west               1  As or later ten happy.

        expected_out = [
            r"Name +Open Tasks +Description",
            r"-+  -+  -+",
            fr"{projects[2].id} *1 *{projects[2].description}",
        ]

        views.projects(repo, config)

        out, err = capsys.readouterr()
        out = out.splitlines()

        assert len(out) == len(expected_out)
        for line_id in range(0, len(out) - 1):
            assert re.match(expected_out[line_id], out[line_id])

        assert err == ""
