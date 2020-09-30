import logging
from datetime import datetime

import pytest

from pydo import exceptions, services
from pydo.fulids import fulid
from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import Task
from tests import factories


class TestTaskAdd:
    def test_add_can_create_simple_task(self, config, repo, faker, caplog, freezer):
        now = datetime.now()
        task_attributes = {"description": faker.sentence()}

        task = services.add_task(repo, task_attributes)

        # Ensure that the object is in the repository
        task = repo.get(Task, task.id)

        assert task.description == task_attributes["description"]
        assert task.state == "open"
        assert task.created == now
        assert task.closed is None
        assert task.project_id is None
        assert (
            "pydo.services",
            logging.INFO,
            f"Added task {task.id}: {task.description}",
        ) in caplog.record_tuples

    def test_add_generates_secuential_sortable_fulid_for_tasks(
        self, repo, config, faker, insert_task
    ):
        tasks = [insert_task]

        task_attributes = {"description": faker.sentence()}
        for task_number in range(1, 100):
            tasks.append(services.add_task(repo, task_attributes))

            assert fulid()._decode_id(tasks[task_number].id) == task_number

    def test_add_assigns_project_if_exist(self, config, repo, faker, insert_project):
        project = insert_project
        task_attributes = {"description": faker.sentence(), "project_id": project.id}

        task = services.add_task(repo, task_attributes)

        assert task.project_id is project.id

    def test_add_generates_project_if_doesnt_exist(self, config, repo, faker, caplog):
        task_attributes = {
            "description": faker.sentence(),
            "project_id": "non_existent",
        }

        task = services.add_task(repo, task_attributes)
        project = repo.get(Project, "non_existent")

        assert task.project_id is project.id
        assert project.id == "non_existent"
        assert (
            "pydo.services",
            logging.INFO,
            f"Added project {project.id}",
        ) in caplog.record_tuples

    def test_add_assigns_tag_if_exist(self, config, repo, faker, insert_tag):
        existent_tag = insert_tag
        task_attributes = {
            "description": faker.sentence(),
            "tag_ids": [existent_tag.id],
        }

        task = services.add_task(repo, task_attributes)

        assert task.tag_ids == [existent_tag.id]

    def test_add_generates_tag_if_doesnt_exist(self, config, repo, faker, caplog):
        task_attributes = {
            "description": faker.sentence(),
            "tag_ids": ["non_existent"],
        }

        task = services.add_task(repo, task_attributes)
        tag = repo.get(Tag, "non_existent")

        assert task.tag_ids == [tag.id]
        assert tag.id == "non_existent"
        assert (
            "pydo.services",
            logging.INFO,
            f"Added tag {tag.id}",
        ) in caplog.record_tuples

    @pytest.mark.parametrize("recurrence_type", ["recurring", "repeating"])
    def test_add_generates_recurrent_tasks(
        self, config, repo, faker, caplog, recurrence_type
    ):
        task_attributes = {
            "description": faker.sentence(),
            "due": faker.date_time(),
            "recurrence": "1d",
            "recurrence_type": recurrence_type,
            "agile": "todo",
        }

        parent_task, child_task = services.add_task(repo, task_attributes.copy())

        parent_task = repo.get(Task, parent_task.id)
        child_task = repo.get(Task, child_task.id)

        # Assert the id of the child is sequential with the parent's
        assert (
            fulid()._decode_id(child_task.id) == fulid()._decode_id(parent_task.id) + 1
        )

        assert child_task.parent_id == parent_task.id
        assert child_task.parent is parent_task
        assert child_task.state == "open"
        assert child_task.due >= task_attributes["due"]
        assert parent_task.recurrence == task_attributes["recurrence"]
        assert parent_task.recurrence_type == task_attributes["recurrence_type"]
        assert parent_task.due == task_attributes["due"]
        assert parent_task.type == "recurrent_task"
        assert child_task.type == "task"
        assert (
            "pydo.services",
            logging.INFO,
            f"Added {parent_task.recurrence_type} task {parent_task.id}:"
            f" {parent_task.description}",
        ) in caplog.record_tuples
        assert (
            "pydo.services",
            logging.INFO,
            f"Added first child task with id {child_task.id}",
        ) in caplog.record_tuples


@pytest.mark.parametrize(
    "action,state", ((services.do_tasks, "completed"), (services.rm_tasks, "deleted"))
)
class TestTaskDoAndDel:
    def test_close_task_by_id(self, action, state, repo, insert_task, freezer, caplog):
        now = datetime.now()
        task = insert_task

        action(repo, task.id)

        assert task.closed == now
        assert task.state == state
        assert (
            "pydo.services",
            logging.INFO,
            f"Closed task {task.id}: {task.description} with state {state}",
        ) in caplog.record_tuples

    def test_close_task_by_short_id(
        self, action, state, repo, insert_task, freezer, caplog
    ):
        now = datetime.now()
        task = insert_task

        # Its the first and only task so the sulid is 'a'
        action(repo, "a")

        assert task.closed == now
        assert task.description == task.description
        assert task.state == state
        assert (
            "pydo.services",
            logging.INFO,
            f"Closed task {task.id}: {task.description} with state {state}",
        ) in caplog.record_tuples

    def test_close_accepts_list_of_tasks(
        self, action, state, repo, insert_tasks, freezer, caplog
    ):
        now = datetime.now()
        tasks = insert_tasks

        # Delete using the three task ids.
        action(repo, " ".join([task.id for task in tasks]))

        for task in tasks:
            assert task.closed == now
            assert task.state == state
            assert (
                "pydo.services",
                logging.INFO,
                f"Closed task {task.id}: {task.description} with state {state}",
            ) in caplog.record_tuples

    def test_close_task_with_complete_date(
        self, action, state, repo, insert_task, caplog
    ):
        complete_date = "2003-08-06"
        task = insert_task

        action(repo, task.id, complete_date)

        assert task.closed == datetime(2003, 8, 6)
        assert task.state == state
        assert (
            "pydo.services",
            logging.INFO,
            f"Closed task {task.id}: {task.description} with state {state}",
        ) in caplog.record_tuples

    def test_close_parent_task_also_do_child(
        self, action, state, repo, insert_parent_task, freezer, caplog
    ):
        now = datetime.now()
        parent_task, child_task = insert_parent_task

        action(repo, parent_task.id)

        assert parent_task.state == state
        assert parent_task.closed == now
        assert child_task.state == state
        assert child_task.closed == now

        assert (
            "pydo.services",
            logging.INFO,
            f"Closed parent task {parent_task.id}: {parent_task.description} with state"
            f" {state}",
        ) in caplog.record_tuples

        assert (
            "pydo.services",
            logging.INFO,
            f"Closed child task {child_task.id}: {child_task.description} with state"
            f" {state}",
        ) in caplog.record_tuples

    def test_close_child_task_generates_next_children(
        self, action, state, repo, insert_parent_task, freezer, caplog
    ):
        now = datetime.now()
        parent_task, child_task = insert_parent_task

        action(repo, child_task.id)

        new_child = parent_task.children[1]

        assert len(parent_task.children) == 2

        assert child_task.state == state
        assert child_task.closed == now

        assert new_child.state == "open"
        assert new_child.created == now
        assert new_child.due >= parent_task.due

        assert (
            "pydo.services",
            logging.INFO,
            f"Closed child task {child_task.id}: {child_task.description} with state"
            f" {state}",
        ) in caplog.record_tuples
        assert (
            "pydo.services",
            logging.INFO,
            f"Added child task {new_child.id}: {new_child.description}",
        ) in caplog.record_tuples

    def test_close_child_task_with_delete_parent_true_also_do_parent(
        self, action, state, repo, insert_parent_task, freezer
    ):
        now = datetime.now()
        parent_task, child_task = insert_parent_task

        action(repo, child_task.id, delete_parent=True)

        assert parent_task.state == state
        assert parent_task.closed == now
        assert child_task.state == state
        assert child_task.closed == now

    def test_close_orphan_child_task_with_delete_parent_logs_the_error(
        self, action, state, repo, insert_task, freezer, caplog
    ):
        now = datetime.now()
        task = insert_task

        action(repo, task.id, delete_parent=True)

        assert task.state == state
        assert task.closed == now
        assert (
            "pydo.services",
            logging.INFO,
            f"Task {task.id} doesn't have a parent",
        ) in caplog.record_tuples


class TestTaskFilter:
    def test_task_filter_accepts_a_task_short_id(self, repo, insert_task):
        task = insert_task

        extracted_tasks = services.tasks_from_task_filter(repo, task.id[-1])

        assert extracted_tasks == [task]

    def test_task_filter_accepts_a_list_of_task_ids(self, repo, insert_tasks):
        tasks = insert_tasks
        task_ids = [task.id for task in tasks]

        extracted_tasks = services.tasks_from_task_filter(repo, " ".join(task_ids))

        assert extracted_tasks == sorted(tasks)

    def test_task_filter_accepts_a_filter_of_task_ids(self, repo):
        tasks = factories.TaskFactory.create_batch(3, priority=3)
        tasks_to_extract = factories.TaskFactory.create_batch(2, priority=5)
        tasks_to_add = tasks.copy()
        tasks_to_add.extend(tasks_to_extract)
        [repo.add(task) for task in tasks_to_add]
        repo.commit()

        extracted_tasks = services.tasks_from_task_filter(repo, "pri:5")

        assert extracted_tasks == sorted(tasks_to_extract)


class TestTaskMod:
    def test_modify_raises_error_if_no_task_matches(self, repo, faker):
        with pytest.raises(exceptions.EntityNotFoundError):
            services.modify_tasks(
                repo, "Unexistent task", {"description": faker.word()}
            )

    def test_modify_task_modifies_task_attributes(
        self, repo, faker, insert_task, caplog
    ):
        task = insert_task
        description = faker.sentence()

        services.modify_tasks(repo, task.id, {"description": description})

        modified_task = repo.get(Task, task.id)

        assert modified_task.description == description
        assert (
            "pydo.services",
            logging.INFO,
            f"Modified task {task.id}.",
        ) in caplog.record_tuples

    def test_modify_task_modifies_project(self, repo, faker, insert_task):
        task = insert_task
        project_id = faker.word()

        services.modify_tasks(repo, task.id, {"project_id": project_id})

        modified_task = repo.get(Task, task.id)
        created_project = repo.get(Project, project_id)

        assert modified_task.project_id == project_id
        assert created_project.id == project_id

    def test_modify_task_unsets_project(self, repo, faker, insert_task):
        task = insert_task
        task.project_id = faker.word()
        repo.add(task)
        repo.commit()

        services.modify_tasks(repo, task.id, {"project_id": None})

        modified_task = repo.get(Task, task.id)

        assert modified_task.project_id is None

    def test_modify_task_adds_tags(self, repo, faker, insert_task, insert_tags):
        task = insert_task
        tags = insert_tags

        services.modify_tasks(repo, task.id, {"tag_ids": [tags[1].id]})

        modified_task = repo.get(Task, task.id)
        created_tag = repo.get(Tag, tags[1].id)

        assert modified_task.tag_ids == [tags[1].id]
        assert created_tag.id == tags[1].id

    def test_modify_task_removes_tags(self, repo, faker, insert_task, insert_tags):
        task = insert_task
        tags = insert_tags
        task.tag_ids = [tag.id for tag in tags]
        repo.add(task)
        repo.commit()

        services.modify_tasks(repo, task.id, {"tags_rm": [tags[1].id, tags[2].id]})

        modified_task = repo.get(Task, task.id)

        assert modified_task.tag_ids == [tags[0].id]

    def test_modify_task_warns_if_task_doesnt_have_any_tag(
        self, repo, faker, insert_task, caplog
    ):
        task = insert_task

        services.modify_tasks(repo, task.id, {"tags_rm": ["unexistent_tag"]})

        assert (
            "pydo.services",
            logging.WARNING,
            f"Task {task.id} doesn't have any tag assigned.",
        ) in caplog.record_tuples

    def test_modify_task_warns_if_task_doesnt_have_tag_assigned(
        self, repo, faker, insert_task, insert_tags, caplog
    ):
        task = insert_task
        tags = insert_tags
        task.tag_ids = [tag.id for tag in tags]
        repo.add(task)
        repo.commit()

        services.modify_tasks(repo, task.id, {"tags_rm": ["unexistent_tag"]})

        assert (
            "pydo.services",
            logging.WARNING,
            f"Task {task.id} doesn't have the tag unexistent_tag assigned.",
        ) in caplog.record_tuples

    def test_modify_task_modifies_parent_attributes(
        self, repo, faker, insert_parent_task
    ):
        parent_task, child_task = insert_parent_task
        description = faker.sentence()

        services.modify_tasks(
            repo, child_task.id, {"description": description}, modify_parent=True
        )

        modified_child_task = repo.get(Task, child_task.id)
        modified_parent_task = repo.get(Task, parent_task.id)

        assert modified_child_task.description == description
        assert modified_parent_task.description == description

    def test_modify_parent_task_doesnt_modify_child(
        self, repo, faker, insert_parent_task
    ):
        parent_task, child_task = insert_parent_task
        description = faker.sentence()

        services.modify_tasks(repo, parent_task.id, {"description": description})

        modified_child_task = repo.get(Task, child_task.id)

        assert modified_child_task.description != description

    def test_modify_child_task_parent_notifies_orphan_if_no_parent(
        self, repo, faker, insert_task, caplog
    ):
        task = insert_task
        description = faker.sentence()

        services.modify_tasks(
            repo, task.id, {"description": description}, modify_parent=True
        )

        modified_task = repo.get(Task, task.id)

        assert modified_task.description == description
        assert (
            "pydo.services",
            logging.WARNING,
            f"Task {task.id} doesn't have a parent task.",
        ) in caplog.record_tuples


#
#     def test_freeze_freezes_task_with_fulid(self):
#         task = self.factory.create(state="open")
#
#         self.manager.freeze(fulid().fulid_to_sulid(task.id, [task.id]),)
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.state == "frozen"
#
#     def test_freeze_parent_freezes_parent_task_with_child_id(self):
#         parent_task = RecurrentTaskFactory(
#             state="open", recurrence="1d", recurrence_type="repeating",
#         )
#
#         child_task = TaskFactory.create(
#             state="open",
#             parent_id=parent_task.id, description=parent_task.description,
#         )
#
#         self.manager.freeze(child_task.id, parent=True)
#
#         result_child_task = self.session.query(Task).get(child_task.id)
#         result_parent_task = self.session.query(Task).get(parent_task.id)
#
#         assert result_child_task.state == "open"
#         assert result_parent_task.state == "frozen"
#
#     def test_unfreeze_unfreezes_task_with_fulid(self):
#         task = self.factory.create(state="frozen")
#
#         self.manager.unfreeze(fulid().fulid_to_sulid(task.id, [task.id]),)
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.state == "open"
#
#     def test_unfreeze_parent_unfreezes_parent_task_with_child_id(self):
#         parent_task = RecurrentTaskFactory(
#             state="frozen", recurrence="1d", recurrence_type="repeating",
#         )
#
#         child_task = TaskFactory.create(
#             state="frozen",
#             parent_id=parent_task.id, description=parent_task.description,
#         )
#
#         self.manager.unfreeze(child_task.id, parent=True)
#
#         result_child_task = self.session.query(Task).get(child_task.id)
#         result_parent_task = self.session.query(Task).get(parent_task.id)
#
#         assert result_child_task.state == "frozen"
#         assert result_parent_task.state == "open"
#
#     @patch("pydo.manager.TaskManager._unfreeze_parent_hook")
#     def test_unfreeze_spawns_unfreeze_parent_hook(self, hookMock):
#         parent_task = RecurrentTaskFactory(state="frozen",)
#
#         self.manager.unfreeze(parent_task.id)
#
#         hookMock.assert_called_once_with(parent_task)
#
#     def test_unfreeze_doesnt_spawn_unfreeze_parent_hook_on_child_tasks(self):
#         task = TaskFactory(state="frozen",)
#
#         self.manager.unfreeze(task.id)
#
#         assert hookMock.called is False
#
#     @patch("pydo.manager.TaskManager._spawn_next_recurring")
#     def test_unfreeze_spawns_next_recurring_if_none_open_exists(self, recurringMock):
#         parent_task = RecurrentTaskFactory(recurrence_type="recurring",
#         state="frozen",)
#
#         self.manager.unfreeze(parent_task.id)
#
#         recurringMock.assert_called_once_with(parent_task)
#
#     @patch("pydo.manager.TaskManager._spawn_next_recurring")
#     def test_unfreeze_doesnt_spawns_next_recurring_if_one_open_exists(
#         self, recurringMock
#     ):
#         parent_task = RecurrentTaskFactory(recurrence_type="recurring",
#         state="frozen",)
#         self.factory.create(
#             parent_id=parent_task.id, state="open",
#         )
#
#         self.manager.unfreeze(parent_task.id)
#
#         assert recurringMock.called is False
#
#     @patch("pydo.manager.TaskManager._spawn_next_repeating")
#     def test_unfreeze_spawns_next_repeating_if_none_open_exists(self, repeatingMock):
#         parent_task = RecurrentTaskFactory(recurrence_type="repeating",
#         state="frozen",)
#
#         self.manager.unfreeze(parent_task.id)
#
#         repeatingMock.assert_called_once_with(parent_task)
#
#     @patch("pydo.manager.TaskManager._spawn_next_repeating")
#     def test_unfreeze_doesnt_spawns_next_repeating_if_one_open_exists(
#         self, repeatingMock
#     ):
#         parent_task = RecurrentTaskFactory(recurrence_type="repeating",
#         state="frozen",)
#         self.factory.create(
#             parent_id=parent_task.id, state="open",
#         )
#
#         self.manager.unfreeze(parent_task.id)
#
#         assert repeatingMock.called is False
#     @patch("pydo.manager.TaskManager._spawn_next_recurring")
#     def test_close_children_hook_doesnt_spawn_next_recurring_when_frozen(
#         self, recurringMock
#     ):
#         parent_task = RecurrentTaskFactory(
#             state="frozen", recurrence="1d", recurrence_type="recurring",
#         )
#
#         child_task = TaskFactory.create(
#             state="open", parent_id=parent_task.id,
#             description=parent_task.description,
#         )
#
#         self.manager._close_children_hook(child_task)
#
#         assert recurringMock.called is False
#
#     @patch("pydo.manager.TaskManager._spawn_next_repeating")
#     def test_close_children_hook_doesnt_spawn_next_repeating_when_frozen(
#         self, repeatingMock
#     ):
#         parent_task = RecurrentTaskFactory(
#             state="frozen", recurrence="1d", recurrence_type="repeating",
#         )
#
#         child_task = TaskFactory.create(
#             state="open", parent_id=parent_task.id,
#             description=parent_task.description,
#         )
#
#         self.manager._close_children_hook(child_task)
#
#         assert repeatingMock.called is False
