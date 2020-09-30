import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pydo import exceptions
from pydo.adapters import repository
from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import Task
from tests import factories

models_to_try_sql = [
    # factory, table, model, insert fixture
    [factories.ProjectFactory, "project", Project, "insert_project_sql"],
    [factories.TagFactory, "tag", Tag, "insert_tag_sql"],
    [factories.TaskFactory, "task", Task, "insert_task_sql"],
]

models_to_try_fake = [
    # factory, table, model, insert fixture
    [factories.ProjectFactory, "project", Project, "insert_project"],
    [factories.TagFactory, "tag", Tag, "insert_tag"],
    [factories.TaskFactory, "task", Task, "insert_task"],
]

# We don't need the model or the insert_fixture fixtures to add objects
add_fixtures = [model_case[:2] for model_case in models_to_try_sql]


@pytest.fixture
def repo_sql(config, session):
    return repository.SqlAlchemyRepository(config, session)


class TestSQLAlchemyRepositoryWithoutSchema:
    def test_apply_migrations_creates_schema(self, config, tmpdir):
        sqlite_file = str(tmpdir.join("sqlite.db"))

        engine = create_engine(f"sqlite:///{sqlite_file}")
        os.environ["PYDO_DATABASE_URL"] = f"sqlite:///{sqlite_file}"
        session = sessionmaker(bind=engine)()
        repo = repository.SqlAlchemyRepository(config, session)

        repo.apply_migrations()

        rows = list(session.execute("SELECT * FROM alembic_version"))
        assert len(rows) > 0


@pytest.mark.parametrize("factory,table", add_fixtures)
class TestSQLAlchemyRepositoryWithSchema:
    def test_repository_can_add_an_object(self, factory, table, session, repo_sql):
        obj = factory.create()

        repo_sql.add(obj)
        repo_sql.commit()

        rows = list(session.execute(f'SELECT id, description FROM "{table}"'))

        assert rows == [(obj.id, obj.description)]


@pytest.mark.parametrize(
    "factory,table,obj_model,insert_object_sql",
    models_to_try_sql,
    indirect=["insert_object_sql"],
)
class TestSQLAlchemyRepositoryWithOneObject:
    def test_repository_can_retrieve_an_object(
        self, factory, table, session, obj_model, insert_object_sql, repo_sql
    ):
        expected_obj = insert_object_sql

        retrieved_obj = repo_sql.get(obj_model, expected_obj.id)

        assert retrieved_obj == expected_obj
        # Task.__eq__ only compares reference
        assert retrieved_obj.description == expected_obj.description

    def test_repository_raises_error_if_no_repository_matches_get(
        self, factory, table, session, obj_model, insert_object_sql, repo_sql
    ):
        with pytest.raises(exceptions.EntityNotFoundError):
            repo_sql.get(obj_model, "unexistent_id")


@pytest.mark.parametrize(
    "factory,table,obj_model,insert_objects_sql",
    models_to_try_sql,
    indirect=["insert_objects_sql"],
)
class TestSQLAlchemyRepositoryWithSeveralObjects:
    def test_repository_can_retrieve_all_objects(
        self, factory, table, session, obj_model, insert_objects_sql, repo_sql
    ):
        expected_objs = insert_objects_sql

        retrieved_objs = repo_sql.all(obj_model)

        assert retrieved_objs == expected_objs
        assert len(retrieved_objs) == 3
        assert retrieved_objs[0].description == expected_objs[0].description

    def test_repository_can_filter_by_property(
        self, factory, table, session, obj_model, insert_objects_sql, repo_sql
    ):
        expected_obj = [insert_objects_sql[1]]

        retrieved_obj = repo_sql.search(obj_model, "id", insert_objects_sql[1].id)

        assert retrieved_obj == expected_obj

    def test_repository_search_raises_error_if_searching_by_unexistent_field(
        self, factory, table, session, obj_model, insert_objects_sql, repo_sql
    ):
        with pytest.raises(exceptions.EntityNotFoundError):
            repo_sql.search(obj_model, "unexistent_field", "unexistent_value")

    def test_repository_search_raises_error_if_searching_by_unexistent_value(
        self, factory, table, session, obj_model, insert_objects_sql, repo_sql
    ):
        with pytest.raises(exceptions.EntityNotFoundError):
            repo_sql.search(obj_model, "id", "unexistent_value")

    def test_repository_can_search_by_multiple_properties(
        self, factory, table, session, obj_model, insert_objects_sql, repo_sql
    ):
        expected_obj = insert_objects_sql[1]

        task_filter = {
            "state": expected_obj.state,
            "description": expected_obj.description,
        }

        retrieved_obj = repo_sql.msearch(obj_model, task_filter)

        assert retrieved_obj == [expected_obj]

    def test_repository_msearch_raises_error_if_unexistent_key(
        self, factory, table, session, obj_model, insert_objects_sql, repo_sql
    ):
        filter = {"unexistent": "value"}

        with pytest.raises(exceptions.EntityNotFoundError):
            repo_sql.msearch(obj_model, filter)

    def test_repository_msearch_raises_error_if_unexistent_value(
        self, factory, table, session, obj_model, insert_objects_sql, repo_sql
    ):
        filter = {"description": "unexistent value"}

        with pytest.raises(exceptions.EntityNotFoundError):
            repo_sql.msearch(obj_model, filter)


class TestSQLAlchemyRepositoryPopulatesRelationships:
    def test_repository_sets_task_project_attributes_on_get(
        self, repo_sql, session, insert_project_sql
    ):
        task = factories.TaskFactory.create(state="open")
        project = insert_project_sql(session)
        session.execute(
            "INSERT INTO task (id, description, state, type, project_id)"
            "VALUES ("
            f'"{task.id}", "{task.description}", "{task.state}", "task", "{project.id}"'
            ")"
        )

        task = repo_sql.get(Task, task.id)
        project = repo_sql.get(Project, project.id)

        assert task.project == project
        assert project.tasks == [task]

    def test_repository_sets_tasks_tags_attribute_on_add(
        self, repo_sql, session, insert_tag_sql
    ):
        task = factories.TaskFactory.create(state="open")
        tags = [insert_tag_sql(session), insert_tag_sql(session)]
        task.tag_ids = [tag.id for tag in tags]

        repo_sql.add(task)
        repo_sql.commit()

        rows = list(
            session.execute('SELECT task_id, tag_id FROM "task_tag_association"')
        )

        assert (task.id, tags[0].id) in rows
        assert (task.id, tags[1].id) in rows

    def test_repository_sets_tasks_tag_attributes_on_get(
        self, repo_sql, session, insert_tag_sql, insert_task_sql
    ):
        task = insert_task_sql(session)
        tag = insert_tag_sql(session)

        session.execute(
            "INSERT INTO task_tag_association (task_id, tag_id)"
            f'VALUES ("{task.id}", "{tag.id}")'
        )

        task = repo_sql.get(Task, task.id)
        tag = repo_sql.get(Tag, tag.id)

        assert task.tags == [tag]
        assert tag.tasks == [task]


@pytest.mark.parametrize("factory,table", add_fixtures)
class TestFakeRepositoryEmpty:
    def test_repository_can_save_an_object(self, factory, table, repo):
        obj = factory.create()

        repo.add(obj)
        repo.commit()

        rows = list(repo.__getattribute__(f"_{table}"))

        assert rows == [obj]


@pytest.mark.parametrize(
    "factory,table,obj_model,insert_object",
    models_to_try_fake,
    indirect=["insert_object"],
)
class TestFakeRepositoryWithOneObject:
    def test_repository_can_retrieve_an_object(
        self, factory, table, obj_model, insert_object, repo
    ):
        expected_obj = insert_object

        retrieved_obj = repo.get(obj_model, expected_obj.id)

        assert retrieved_obj == expected_obj
        # Task.__eq__ only compares reference
        assert retrieved_obj.description == expected_obj.description

    def test_repository_raises_error_if_no_repository_matches_get(
        self, factory, table, obj_model, insert_object, repo
    ):
        with pytest.raises(exceptions.EntityNotFoundError):
            repo.get(obj_model, "unexistent_id")


@pytest.mark.parametrize(
    "factory,table,obj_model,insert_objects",
    models_to_try_fake,
    indirect=["insert_objects"],
)
class TestFakeRepositoryWithSeveralObject:
    def test_repository_can_retrieve_all_objects(
        self, factory, table, session, obj_model, insert_objects, repo
    ):
        expected_obj = sorted(insert_objects)

        retrieved_obj = repo.all(obj_model)

        assert retrieved_obj == expected_obj
        assert len(retrieved_obj) == 3
        assert retrieved_obj[0].description == expected_obj[0].description

    def test_repository_can_search_by_property(
        self, factory, table, session, obj_model, insert_objects, repo
    ):
        expected_obj = [insert_objects[1]]

        retrieved_obj = repo.search(obj_model, "id", insert_objects[1].id)

        assert retrieved_obj == expected_obj

    def test_repository_search_raises_error_if_searching_by_unexistent_field(
        self, factory, table, session, obj_model, insert_objects, repo
    ):
        with pytest.raises(exceptions.EntityNotFoundError):
            repo.search(obj_model, "unexistent_field", "unexistent_value")

    def test_repository_search_raises_error_if_searching_by_unexistent_value(
        self, factory, table, session, obj_model, insert_objects, repo
    ):
        with pytest.raises(exceptions.EntityNotFoundError):
            repo.search(obj_model, "id", "unexistent_value")

    def test_repository_can_search_by_multiple_properties(
        self, factory, table, session, obj_model, insert_objects, repo
    ):
        expected_obj = insert_objects[1]

        filter = {"state": expected_obj.state, "description": expected_obj.description}

        retrieved_obj = repo.msearch(obj_model, filter)

        assert retrieved_obj == [expected_obj]

    def test_repository_msearch_raises_error_if_unexistent_key(
        self, factory, table, session, obj_model, insert_objects, repo
    ):
        filter = {"unexistent": "value"}

        with pytest.raises(exceptions.EntityNotFoundError):
            repo.msearch(obj_model, filter)

    def test_repository_msearch_raises_error_if_unexistent_value(
        self, factory, table, session, obj_model, insert_objects, repo
    ):
        filter = {"description": "unexistent value"}

        with pytest.raises(exceptions.EntityNotFoundError):
            repo.msearch(obj_model, filter)


class TestFakeRepositoryPopulatesRelationships:
    def test_repository_sets_tasks_project_attribute_on_set(self, repo, insert_project):
        task = factories.TaskFactory.create(state="open")
        project = insert_project
        task.project_id = project.id

        repo.add(task)

        assert repo._select_table(Task)[0].project == project
        assert repo._select_table(Project)[0].tasks == [task]

    def test_repository_sets_tasks_and_project_attributes_on_get(
        self, repo, insert_project
    ):
        task = factories.TaskFactory.create(state="open")
        project = insert_project
        task.project_id = project.id
        task.project = project
        project.tasks = [task]
        repo._task.add(task)

        task = repo.get(Task, task.id)
        project = repo.get(Project, project.id)

        assert task.project == project
        assert project.tasks == [task]

    def test_repository_sets_tasks_tags_attribute_on_add(self, repo, insert_tags):
        task = factories.TaskFactory.create(state="open")
        tags = insert_tags
        task.tag_ids = [tag.id for tag in tags]

        repo.add(task)
        repo.commit()

        assert repo._select_table(Task)[0].tags == tags
        assert repo._select_table(Tag)[0].tasks == [task]

    def test_repository_sets_tasks_tags_attribute_on_get(self, repo, insert_tag):
        task = factories.TaskFactory.create(state="open")
        tag = insert_tag

        task.tag_ids = [tag.id]
        task.tags = [tag]
        tag.tasks.append(task)
        repo._task.add(task)

        task = repo.get(Task, task.id)

        assert task.tags == [tag]
        assert tag.tasks == [task]
