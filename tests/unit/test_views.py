"""
Module to test the view implementations.
"""
import re

import pytest

from pydo import services, views
from tests import factories


class TestGenericReport:
    def test_remove_null_columns_removes_columns_if_all_nulls(self, config):
        original_columns = config.get("report.open.columns")
        original_labels = config.get("report.open.labels")

        desired_columns = original_columns.copy()
        desired_labels = original_labels.copy()

        # If we don't assign a project and tags to the tasks they are all
        # going to be null, we are going the due to be null, and as they are simple
        # tasks there aren't going to have recurrence, recurrence_type nor parent_id.
        for attribute in [
            "project_id",
            "tag_ids",
            "recurrence",
            "recurrence_type",
            "due",
            "parent_id",
        ]:
            attribute_index = desired_columns.index(attribute)
            desired_columns.pop(attribute_index)
            desired_labels.pop(attribute_index)

        tasks = factories.TaskFactory.create_batch(100, due=None)

        result_columns, result_labels = views._remove_null_columns(
            tasks, original_columns, original_labels
        )

        assert desired_columns == result_columns
        assert desired_labels == result_labels

    def test_remove_null_columns_doesnt_fail_if_column_doesnt_exist(self):
        desired_columns = ["id", "description"]
        columns = desired_columns.copy()
        columns.append("unexistent_column")

        desired_labels = ["Id", "Description"]
        labels = desired_labels.copy()
        labels.append("unexistent_label")

        tasks = factories.TaskFactory.create_batch(100, due=None)

        result_columns, result_labels = views._remove_null_columns(
            tasks, columns, labels
        )

        assert result_columns == desired_columns
        assert result_labels == desired_labels

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

    def test_open_allows_task_filter(self, repo, config, insert_tasks, capsys, faker):
        # We are going to create a task that has a special project and filter by it
        # So only that one should be shown

        # Generate the tasks

        project = faker.word()

        task_with_project = factories.TaskFactory.create(
            project_id=project, due=None, state="open"
        )
        repo.add(task_with_project)
        repo.commit()

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

        views.open(repo, config, {"project_id": project})

        out, err = capsys.readouterr()
        out = out.splitlines()

        assert len(out) == len(expected_out)
        for line_id in range(0, len(out) - 1):
            assert re.match(expected_out[line_id], out[line_id])

        assert err == ""


class TestProjectsReport:
    @pytest.mark.skip("Not yet")
    def test_projects_prints_project_attributes(
        self, repo, config, insert_tasks, insert_project, capsys
    ):
        # Assign the project to all the tasks, complete one and delete the other

        project = insert_project
        tasks = insert_tasks

        for task in tasks:
            task.project = project

        [repo.add(task) for task in tasks]
        services.do_tasks(repo, task[1])
        services.rm_tasks(repo, task[2])
        repo.commit()

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

        views.projects(repo, config)

        out, err = capsys.readouterr()
        out = out.splitlines()

        assert len(out) == len(expected_out)
        for line_id in range(0, len(out) - 1):
            assert re.match(expected_out[line_id], out[line_id])

        assert err == ""
