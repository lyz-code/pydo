from datetime import datetime

from pydo.services import parse_task_arguments
from tests import factories


class TestTaskArgumentParser:
    def test_parse_extracts_description_without_quotes(self, faker):
        description = faker.sentence()
        task_arguments = description.split(" ")

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description

    def test_parse_allows_empty_description(self):
        attributes = parse_task_arguments("")

        assert "description" not in attributes

    def test_parse_extracts_project_in_short_representation(self, faker):
        description = faker.sentence()
        project = faker.word()
        task_arguments = [
            description,
            f"pro:{project}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["project_id"] == project

    def test_parse_extracts_project_in_long_representation(self, faker):
        description = faker.sentence()
        project = faker.word()
        task_arguments = [
            description,
            f"project:{project}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["project_id"] == project

    def test_parse_extracts_tags(self, faker):
        description = faker.sentence()
        tags = [faker.word(), faker.word()]

        task_arguments = [
            description,
            f"+{tags[0]}",
            f"+{tags[1]}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["tag_ids"] == tags

    def test_parse_extracts_tags_to_remove(self, faker):
        description = faker.sentence()
        tags = [faker.word(), faker.word()]

        task_arguments = [
            description,
            f"-{tags[0]}",
            f"-{tags[1]}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["tags_rm"] == tags

    def test_parse_extracts_priority_in_short_representation(self, faker):
        description = faker.sentence()
        priority = faker.random_number()
        task_arguments = [
            description,
            f"pri:{priority}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["priority"] == priority

    def test_parse_extracts_priority_in_long_representation(self, faker):
        description = faker.sentence()
        priority = faker.random_number()
        task_arguments = [
            description,
            f"priority:{priority}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["priority"] == priority

    def test_parse_extracts_estimate_in_short_representation(self, faker):
        description = faker.sentence()
        estimate = faker.random_number()
        task_arguments = [
            description,
            f"est:{estimate}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["estimate"] == estimate

    def test_parse_extracts_estimate_in_long_representation(self, faker):
        description = faker.sentence()
        estimate = faker.random_number()
        task_arguments = [
            description,
            f"estimate:{estimate}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["estimate"] == estimate

    def test_parse_extracts_willpower_in_short_representation(self, faker):
        description = faker.sentence()
        willpower = faker.random_number()
        task_arguments = [
            description,
            f"wp:{willpower}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["willpower"] == willpower

    def test_parse_extracts_willpower_in_long_representation(self, faker):
        description = faker.sentence()
        willpower = faker.random_number()
        task_arguments = [
            description,
            f"willpower:{willpower}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["willpower"] == willpower

    def test_parse_extracts_value_in_short_representation(self, faker):
        description = faker.sentence()
        value = faker.random_number()
        task_arguments = [
            description,
            f"vl:{value}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["value"] == value

    def test_parse_extracts_value_in_long_representation(self, faker):
        description = faker.sentence()
        value = faker.random_number()
        task_arguments = [
            description,
            f"value:{value}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["value"] == value

    def test_parse_extracts_fun_in_long_representation(self, faker):
        description = faker.sentence()
        fun = faker.random_number()
        task_arguments = [
            description,
            f"fun:{fun}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["fun"] == fun

    def test_parse_extracts_body_in_long_representation(self, faker):
        description = faker.sentence()
        body = faker.sentence()
        task_arguments = [
            description,
            f"body:{body}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["body"] == body

    def test_parse_extracts_agile_in_short_representation(self, faker):
        description = faker.sentence()
        agile = faker.word()
        task_arguments = [
            description,
            f"ag:{agile}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["agile"] == agile

    def test_parse_extracts_agile_in_long_representation(self, faker):
        description = faker.sentence()
        agile = faker.word()
        task_arguments = [
            description,
            f"agile:{agile}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["agile"] == agile

    def test_parse_extracts_due(self, faker, freezer):
        description = faker.sentence()
        freezer.move_to("2017-05-20")
        due = "1d"
        task_arguments = [
            description,
            f"due:{due}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert isinstance(attributes["due"], datetime)
        assert attributes["due"] == datetime(2017, 5, 21)

    def test_parse_return_empty_string_if_argument_is_empty(self):
        # One of each type (str, date, float, int) and the description
        # empty tags are tested separately
        task_arguments = [
            "",
            "agile:",
            "due:",
            "estimate:",
            "fun:",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == ""
        assert attributes["agile"] == ""
        assert attributes["due"] == ""
        assert attributes["estimate"] == ""
        assert attributes["fun"] == ""

    def test_parse_extracts_recurring_in_long_representation(self, faker):
        description = faker.sentence()
        recurring = faker.word()
        task_arguments = [
            description,
            f"recurring:{recurring}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["recurrence_type"] == "recurring"
        assert attributes["recurrence"] == recurring

    def test_parse_extracts_recurring_in_short_representation(self, faker):
        description = faker.sentence()
        recurring = faker.word()
        task_arguments = [
            description,
            f"rec:{recurring}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["recurrence_type"] == "recurring"
        assert attributes["recurrence"] == recurring

    def test_parse_extracts_repeating_in_long_representation(self, faker):
        description = faker.sentence()
        repeating = faker.word()
        task_arguments = [
            description,
            f"repeating:{repeating}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["recurrence_type"] == "repeating"
        assert attributes["recurrence"] == repeating

    def test_parse_extracts_repeating_in_short_representation(self, faker):
        description = faker.sentence()
        repeating = faker.word()
        task_arguments = [
            description,
            f"rep:{repeating}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["description"] == description
        assert attributes["recurrence_type"] == "repeating"
        assert attributes["recurrence"] == repeating

    def test_parse_extracts_task_ids(self, faker):
        task_arguments = ["a", "s", "d"]

        attributes = parse_task_arguments(task_arguments, "filter")

        assert attributes["task_ids"] == task_arguments

    def test_parse_doesnt_process_task_ids(self, faker):
        task_arguments = [factories.create_fulid()]

        attributes = parse_task_arguments(task_arguments, "filter")

        assert attributes["task_ids"] == task_arguments

    def test_parse_extracts_state(self, faker):
        description = faker.sentence()
        state = "open"
        task_arguments = [
            description,
            f"state:{state}",
        ]

        attributes = parse_task_arguments(task_arguments)

        assert attributes["state"] == "open"
