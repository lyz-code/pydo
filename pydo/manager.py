"""
Module to store the main class of pydo

Classes:
    TaskManager: Class to manipulate the tasks data
"""
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
from pydo import config
from pydo.cli import load_logger
from pydo.fulids import fulid
from pydo.models import Task, Project, Tag, RecurrentTask

import datetime
import logging
import re

load_logger()


class TableManager:
    """
    Abstract Class to manipulate a database table data.

    Arguments:
        session (session object): Database session
        table_model (Sqlalchemy model): Table model

    Internal methods:
        _add: Method to create a new table item
        _get: Retrieve the table element identified by id.
        _get_attributes: Method to extract the object attributes to a
            dictionary.
        _update: Method to update an existing table item

    Public attributes:
        session (session object): Database session
        log (logging object): Logger
    """

    def __init__(self, session, table_model):
        self.log = logging.getLogger('main')
        self.model = table_model
        self.session = session

    def _add(self, id, object_values):
        """
        Method to create a new table item

        Arguments:
            id (str): object identifier
            object_values (dict): Dictionary with the column identifier
                as keys.
        """

        obj = self.model(id=id)

        for attribute_key, attribute_value in object_values.items():
            setattr(obj, attribute_key, attribute_value)

        try:
            title = object_values['title']
        except KeyError:
            title = None

        self.session.add(obj)
        self.session.commit()
        self.log.debug(
            'Added {} {}: {}'.format(
                self.model.__name__.lower(),
                id,
                title,
            )
        )

    def _get(self, id):
        """
        Return the table element identified by id.

        Arguments:
            id (str): Table element identifier

        Returns:
            table element (obj): Sqlalchemy element of the table.
            raises: ValueError if element is not found
        """

        table_element = self.session.query(self.model).get(id)

        if table_element is None:
            raise ValueError('The element {} does not exist'.format(id))
        else:
            return table_element

    def _get_attributes(self, model):
        """
        Method to extract the object attributes to a dictionary.

        Arguments:
            model(SQLAlchemy): Object to extract attributes.

        Returns:
            attributes (dict): object attributes.
        """

        return {
            column_name: getattr(model, column_name)
            for column_name in model.__mapper__.attrs.keys()
        }

    def _update(self, id, object_values=None):
        """
        Method to update an existing table item

        Arguments:
            id (str): object identifier
            object_values (dict): Dictionary with the column identifier
                as keys.
        """

        table_element = self.session.query(self.model).get(id)

        if table_element is None:
            raise ValueError('The element {} does not exist'.format(id))
        else:
            if object_values is not None:
                for attribute_key, attribute_value in object_values.items():
                    setattr(table_element, attribute_key, attribute_value)

            self.session.commit()
            self.log.debug(
                'Modified {}: {}'.format(
                    id,
                    object_values,
                )
            )


class TaskManager(TableManager):
    """
    Class to manipulate the tasks data.

    Arguments:
        session (session object): Database session

    Public methods:
        add: Creates a new task.
        complete: Completes a task.
        delete: Deletes a task.
        freeze: Freezes a task.
        modify: Modifies a task.
        modify_parent: Modifies the parent task.
        unfreeze: Unfreezes a task.

    Internal methods:
        _add: Parent method to add table elements.
        _close: Closes a task.
        _close_children_hook: Method to call different hooks for each parent
            type once a children has been closed.
        _create_next_fulid: Method to create the next task's fulid.
        _generate_children_attributes: Method to generate the next children
            task attributes.
        _get_fulid: Method to get the task's fulid if necessary.
        _parse_arguments: Parse a Taskwarrior like add query into task
            attributes.
        _parse_attribute: Parse a Taskwarrior like add argument into a task
            attribute.
        _rm_tags: Method to delete tags from the Task attributes.
        _set: Method to set the task's attributes and get its fulid.
        _set_agile: Method to set the agile attribute.
        _set_project: Method to set the project attribute.
        _set_tags: Method to set the tags attribute.
        _spawn_next_recurring: Method to spawn the next recurring children
            task.
        _spawn_next_repeating: Method to spawn the next repeating children
            task.
        _unfreeze_parent_hook: Method to call the different hooks for each
            parent type once it's unfrozen
        _update: Parent method to update table elements.

    Public attributes:
        date (DateManager): DateManager object.
        fulid (fulid object): Fulid manager and generator object.
        log (logging object): Logger
        session (session object): Database session
        recurrence (TableManager): RecurrenceTask manager
    """

    def __init__(self, session):
        super().__init__(session, Task)
        self.date = DateManager()
        self.fulid = fulid(
            config.get('fulid.characters'),
            config.get('fulid.forbidden_characters'),
        )
        self.recurrence = TableManager(session, RecurrentTask)

    def _parse_attribute(self, add_argument):
        """
        Parse a Taskwarrior like add argument into a task attribute.

        Arguments:
            add_argument (str): Taskwarrior like add argument string.

        Returns:
            attribute_id (str): Attribute key.
            attributes_value (str|int|float|date): Attribute value.
        """

        attribute_conf = {
            'agile': {
                'regexp': r'^(ag|agile):',
                'type': 'str',
            },
            'body': {
                'regexp': r'^body:',
                'type': 'str',
            },
            'due': {
                'regexp': r'^due:',
                'type': 'date',
            },
            'estimate': {
                'regexp': r'^(est|estimate):',
                'type': 'float',
            },
            'fun': {
                'regexp': r'^fun:',
                'type': 'int',
            },
            'priority': {
                'regexp': r'^(pri|priority):',
                'type': 'int',
            },
            'project_id': {
                'regexp': r'^(pro|project):',
                'type': 'str',
            },
            'recurring': {
                'regexp': r'^(rec|recurring):',
                'type': 'str',
            },
            'repeating': {
                'regexp': r'^(rep|repeating):',
                'type': 'str',
            },
            'tags': {
                'regexp': r'^\+',
                'type': 'tag',
            },
            'tags_rm': {
                'regexp': r'^\-',
                'type': 'tag',
            },
            'value': {
                'regexp': r'^(vl|value):',
                'type': 'int',
            },
            'willpower': {
                'regexp': r'^(wp|willpower):',
                'type': 'int',
            },
        }

        for attribute_id, attribute in attribute_conf.items():
            if re.match(attribute['regexp'], add_argument):
                if attribute['type'] == 'tag':
                    if len(add_argument) < 2:
                        raise ValueError("Empty tag value")
                    return attribute_id, re.sub(r'^[+-]', '', add_argument)
                elif add_argument.split(':')[1] == '':
                    return attribute_id, ''
                elif attribute['type'] == 'str':
                    return attribute_id, add_argument.split(':')[1]
                elif attribute['type'] == 'int':
                    return attribute_id, int(add_argument.split(':')[1])
                elif attribute['type'] == 'float':
                    return attribute_id, float(add_argument.split(':')[1])
                elif attribute['type'] == 'date':
                    return attribute_id, self.date.convert(
                        ":".join(add_argument.split(':')[1:])
                    )
        return 'title', add_argument

    def _parse_arguments(self, add_arguments):
        """
        Parse a Taskwarrior like add query into task attributes

        Arguments:
            add_arguments (list): Taskwarrior like add argument list.

        Returns:
            attributes (dict): Dictionary with the attributes of the task.
        """

        attributes = {}

        for argument in add_arguments:
            attribute_id, attribute_value = self._parse_attribute(argument)
            if attribute_id in ['tags', 'tags_rm', 'title']:
                try:
                    attributes[attribute_id]
                except KeyError:
                    attributes[attribute_id] = []
                attributes[attribute_id].append(attribute_value)
            elif attribute_id in ['recurring', 'repeating']:
                attributes['recurrence'] = attribute_value
                attributes['recurrence_type'] = attribute_id
            else:
                attributes[attribute_id] = attribute_value

        try:
            attributes['title'] = ' '.join(attributes['title'])
        except KeyError:
            pass

        return attributes

    def _get_fulid(self, id, state='open'):
        """
        Method to get the task's fulid if necessary.

        Arguments:
            id (str): Ulid of the task.
            state (str): Task status.

        Returns:
            fulid (str): fulid that matches the sulid.
        """
        fulid = id
        if len(id) < 10:
            tasks = self.session.query(Task).filter_by(state=state)
            task_fulids = [task.id for task in tasks]
            try:
                fulid = self.fulid.sulid_to_fulid(id, task_fulids)
            except KeyError:
                self.log.error(
                    'There is no {} task with fulid {}'.format(
                        state,
                        fulid,
                    )
                )

        return fulid

    def _generate_children_attributes(self, parent_task):
        """
        Method to generate the next children task attributes.

        Arguments:
            parent_task (RecurrentTask):

        Returns:
            child_attributes (dict): Children attributes
        """

        child_attributes = self._get_attributes(parent_task)
        child_attributes.pop('recurrence')
        child_attributes.pop('recurrence_type')
        child_attributes['id'] = self._create_next_fulid().str
        child_attributes['parent_id'] = parent_task.id
        child_attributes['type'] = 'task'

        return child_attributes

    def _create_next_fulid(self):
        """
        Method to create the next task's fulid.

        Returns:
            fulid (str): next fulid.
        """

        last_fulid = self.session.query(
            Task
        ).filter_by(state='open').order_by(Task.id.desc()).first()

        if last_fulid is not None:
            last_fulid = last_fulid.id

        return self.fulid.new(last_fulid)

    def _set_project(self, task_attributes, project_id=None):
        """
        Method to set the project attribute.

        A new project will be created if it doesn't exist yet.

        Arguments:
            task_attributes (dict): Dictionary with the attributes of the task.
            project_id (str): Project id.
        """
        if project_id is not None:
            project = self.session.query(Project).get(project_id)
            if project is None:
                project = Project(id=project_id, description='')
                self.session.add(project)
                self.session.commit()
            task_attributes['project'] = project

    def _set_tags(self, task_attributes, tags=[]):
        """
        Method to set the tags attribute.

        A new tag will be created if it doesn't exist yet.

        Arguments:
            task_attributes (dict): Dictionary with the attributes of the task.
            tags (list): List of tag ids.
        """
        commit_necessary = False

        if 'tags' not in task_attributes:
            task_attributes['tags'] = []

        for tag_id in tags:
            tag = self.session.query(Tag).get(tag_id)
            if tag is None:
                tag = Tag(id=tag_id, description='')
                self.session.add(tag)
                commit_necessary = True
            task_attributes['tags'].append(tag)

        if commit_necessary:
            self.session.commit()

    def _rm_tags(self, task_attributes, tags_rm=[]):
        """
        Method to delete tags from the Task attributes.

        Arguments:
            task_attributes (dict): Dictionary with the attributes of the task.
            tags_rm (list): List of tag ids to remove.
        """
        for tag_id in tags_rm:
            tag = self.session.query(Tag).get(tag_id)
            if tag is None:
                raise ValueError("The tag doesn't exist")
            task_attributes['tags'].remove(tag)

    def _set_agile(self, task_attributes, agile=None):
        """
        Method to set the agile attribute.

        If the agile property value isn't between the specified ones,
        a `ValueError` will be raised.

        Arguments:
            task_attributes (dict): Dictionary with the attributes of the task.
            agile (str): Task agile state.
        """
        if agile is not None and \
                agile not in config.get('task.agile.allowed_states'):
            raise ValueError(
                'Agile state {} is not between the specified '
                'by task.agile.states'.format(agile)
            )

        if agile is not None:
            task_attributes['agile'] = agile

    def _set(
        self,
        id=None,
        project_id=None,
        tags=[],
        tags_rm=[],
        agile=None,
        **kwargs
    ):
        """
        Method to set the task's attributes and get its fulid.

        Arguments:
            id (str): Ulid of the task if it already exists.
            project_id (str): Project id.
            tags (list): List of tag ids.
            tags_rm (list): List of tag ids to remove.
            agile (str): Task agile state.
            **kwargs: (object) Other attributes (key: value).

        Returns:
            fulid (str): fulid that matches the sulid.
            task_attributes (dict): Dictionary with the attributes of the task.
        """
        fulid = None
        task_attributes = {}

        if project_id == '':
            task_attributes['project'] = None
        else:
            self._set_project(task_attributes, project_id)

        if id is not None:
            fulid = self._get_fulid(id)

            task = self.session.query(Task).get(fulid)
            task_attributes['tags'] = task.tags

            self._rm_tags(task_attributes, tags_rm)

        self._set_tags(task_attributes, tags)

        if agile == '':
            task_attributes['agile'] = None
        else:
            self._set_agile(task_attributes, agile)

        for key, value in kwargs.items():
            if value == '':
                value = None
            task_attributes[key] = value

        return fulid, task_attributes

    def add(
        self,
        title,
        project_id=None,
        tags=[],
        agile=None,
        **kwargs
    ):
        """
        Use parent method to create a new task.

        Arguments:
            title (str): Title of the task.
            project_id (str): Project id.
            tags (list): List of tag ids.
            agile (str): Task agile state.
            **kwargs: (object) Other attributes (key: value).
        """

        fulid, task_attributes = self._set(
            project_id=project_id,
            tags=tags,
            agile=agile,
            title=title,
            state='open',
            **kwargs,
        )

        if 'recurrence' in task_attributes:
            if task_attributes['due'] is None:
                self.log.error(
                    'You need to specify a due date for {} tasks'.format(
                        task_attributes['recurrence_type']
                    )
                )
            parent_id = self._create_next_fulid().str
            self.recurrence._add(
                parent_id,
                task_attributes,
            )

            task_attributes.pop('recurrence')
            task_attributes.pop('recurrence_type')
            task_attributes['parent_id'] = parent_id

        self._add(
            self._create_next_fulid().str,
            task_attributes,
        )

    def modify(
        self,
        id,
        project_id=None,
        tags=[],
        tags_rm=[],
        agile=None,
        **kwargs
    ):
        """
        Use parent method to modify an existing task.

        Arguments:
            project_id (str): Project id.
            tags (list): List of tag ids.
            tags_rm (list): List of tag ids to remove.
            agile (str): Task agile state.
            **kwargs: (object) Other attributes (key: value).
        """
        fulid, task_attributes = self._set(
            id,
            project_id,
            tags,
            tags_rm,
            agile,
            **kwargs
        )

        self._update(
            fulid,
            task_attributes,
        )

    def modify_parent(self, id, **kwargs):
        """
        Use parent method to modify the parent of an existing task.

        Arguments:
            id (str): child id.
            **kwargs: (object) Other attributes (key: value).
        """

        fulid = self._get_fulid(id)
        child_task = self.session.query(Task).get(fulid)

        if child_task.parent_id is None:
            self.log.error(
                "Task {} doesn't have a parent task".format(child_task.id)
            )
        else:
            self.modify(child_task.parent_id, **kwargs)

    def _close(self, id, state, parent):
        """
        Method to close a task

        Arguments:
            id (str): Ulid of the task
            state (str): State of the task once it's closed
            parent (bool): Also delete parent task
        """

        try:
            id = self._get_fulid(id)
        except KeyError:
            self.log.error('There is no task with that id')
            return

        task = self.session.query(Task).get(id)

        task.state = state
        task.closed = datetime.datetime.now()

        if parent:
            if task.parent_id is None:
                self.log.error(
                    "Task {} doesn't have a parent task".format(task.id)
                )
            else:
                self._close(task.parent_id, state=state, parent=False)
        elif task.parent_id is not None:
            self._close_children_hook(task)

        self.session.commit()
        self.log.debug(
            '{} task {}: {}'.format(
                state.title(),
                task.id,
                task.title
            )
        )

    def _close_children_hook(self, task):
        """
        Method to call different hooks for each parent type once a children
        has been closed

        Arguments:
            task (Task): Children closed task
        """
        if task.parent.state != 'frozen':
            if task.parent.recurrence_type == 'recurring':
                self._spawn_next_recurring(task.parent)
            elif task.parent.recurrence_type == 'repeating':
                self._spawn_next_repeating(task.parent)

    def _spawn_next_recurring(self, parent_task):
        """
        Method to spawn the next recurring children task.

        Arguments:
            parent_task (RecurrentTask):
        """
        now = datetime.datetime.now()

        child_attributes = self._generate_children_attributes(parent_task)

        last_due = parent_task.due

        while True:
            next_due = self.date.convert(parent_task.recurrence, last_due)
            if next_due > now:
                break
            last_due = next_due

        child_attributes['due'] = next_due
        self._add(
            child_attributes['id'],
            child_attributes,
        )

        # Assign parent. It seems that specifying it in the child_attributes
        # is not enough.

        child_task = self.session.query(Task).get(child_attributes['id'])
        child_task.parent_id = child_attributes['parent_id']

    def _spawn_next_repeating(self, parent_task):
        """
        Method to spawn the next repeating children task.

        Arguments:
            parent_task (RecurrentTask):
        """
        now = datetime.datetime.now()

        child_attributes = self._generate_children_attributes(parent_task)
        child_attributes['due'] = self.date.convert(
            parent_task.recurrence,
            now,
        )
        self._add(
            child_attributes['id'],
            child_attributes,
        )

        # Assign parent. It seems that specifying it in the child_attributes
        # is not enough.

        child_task = self.session.query(Task).get(child_attributes['id'])
        child_task.parent_id = child_attributes['parent_id']

    def delete(self, id, parent=False):
        """
        Method to delete a task

        Arguments:
            id (str): Ulid of the task
            parent (bool): Also delete parent task (False by default)
        """

        self._close(id, 'deleted', parent)

    def complete(self, id, parent=False):
        """
        Method to complete a task

        Arguments:
            id (str): Ulid of the task
            parent (bool): Also delete parent task (False by default)
        """

        self._close(id, 'completed', parent)

    def freeze(self, id, parent=False):
        """
        Method to freeze a task.

        Arguments:
            id (str): Ulid of the task.
            parent (bool): Freeze the parent task instead(False by default).
        """

        fulid = self._get_fulid(id)
        task = self.session.query(Task).get(fulid)

        if parent and task.parent is not None:
            task.parent.state = 'frozen'
        else:
            task.state = 'frozen'
        self.session.commit()

    def unfreeze(self, id, parent=False):
        """
        Method to unfreeze a task.

        Arguments:
            id (str): Ulid of the task
            parent (bool): Unfreeze the parent task instead(False by default).
        """

        fulid = self._get_fulid(id, 'frozen')
        task = self.session.query(Task).get(fulid)
        if parent and task.parent is not None:
            task.parent.state = 'open'
        else:
            task.state = 'open'

        self.session.commit()

        if task.type != 'task':
            self._unfreeze_parent_hook(task)

    def _unfreeze_parent_hook(self, task):
        """
        Method to call different hooks for each parent type once it's unfrozen

        Arguments:
            task (Task): Parent unfrozen task
        """

        children_states = [children.state for children in task.children]

        if 'open' not in children_states:
            if task.recurrence_type == 'recurring':
                self._spawn_next_recurring(task)
            elif task.recurrence_type == 'repeating':
                self._spawn_next_repeating(task)


class DateManager:
    """
    Class to manipulate dates.

    Public methods:
        convert: Converts a human string into a datetime

    Internal methods:
        _convert_weekday: Method to convert a weekday human string into
            a datetime object.
        _str2date: Method do operations on dates with short codes.
        _next_weekday: Method to get the next week day of a given date.
        _next_monthday: Method to get the difference between for the next same
            week day of the month for the specified months.
        _weekday: Method to return the dateutil.relativedelta weekday.
    """

    def convert(self, human_date, starting_date=datetime.datetime.now()):
        """
        Method to convert a human string into a datetime object

        Arguments:
            human_date (str): Date string to convert
            starting_date (datetime): Date to compare.

        Returns:
            date (datetime)
        """

        date = self._convert_weekday(human_date, starting_date)

        if date is not None:
            return date

        if re.match(
            r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}',
            human_date,
        ):
            return datetime.datetime.strptime(human_date, '%Y-%m-%dT%H:%M')
        elif re.match(r'[0-9]{4}.[0-9]{2}.[0-9]{2}', human_date,):
            return datetime.datetime.strptime(human_date, '%Y-%m-%d')
        elif re.match(r'(now|today)', human_date):
            return starting_date
        elif re.match(r'tomorrow', human_date):
            return starting_date + relativedelta(days=1)
        elif re.match(r'yesterday', human_date):
            return starting_date + relativedelta(days=-1)
        else:
            return self._str2date(human_date, starting_date)

    def _convert_weekday(self, human_date, starting_date):
        """
        Method to convert a weekday human string into a datetime object.

        Arguments:
            human_date (str): Date string to convert
            starting_date (datetime): Date to compare.

        Returns:
            date (datetime)
        """

        if re.match(r'mon.*', human_date):
            return self._next_weekday(0, starting_date)
        elif re.match(r'tue.*', human_date):
            return self._next_weekday(1, starting_date)
        elif re.match(r'wed.*', human_date):
            return self._next_weekday(2, starting_date)
        elif re.match(r'thu.*', human_date):
            return self._next_weekday(3, starting_date)
        elif re.match(r'fri.*', human_date):
            return self._next_weekday(4, starting_date)
        elif re.match(r'sat.*', human_date):
            return self._next_weekday(5, starting_date)
        elif re.match(r'sun.*', human_date):
            return self._next_weekday(6, starting_date)
        else:
            return None

    def _str2date(self, modifier, starting_date=datetime.datetime.now()):
        """
        Method do operations on dates with short codes.

        Arguments:
            modifier (str): Possible inputs are a combination of:
                s: seconds,
                m: minutes,
                h: hours,
                d: days,
                w: weeks,
                mo: months,
                rmo: relative months,
                y: years.

                For example '5d 10h 3m 10s'.
            starting_date (datetime): Date to compare

        Returns:
            resulting_date (datetime)
        """

        date_delta = relativedelta()
        for element in modifier.split(' '):
            element = re.match(r'(?P<value>[0-9]+)(?P<unit>.*)', element)
            value = int(element.group('value'))
            unit = element.group('unit')

            if unit == 's':
                date_delta += relativedelta(seconds=value)
            elif unit == 'm':
                date_delta += relativedelta(minutes=value)
            elif unit == 'h':
                date_delta += relativedelta(hours=value)
            elif unit == 'd':
                date_delta += relativedelta(days=value)
            elif unit == 'mo':
                date_delta += relativedelta(months=value)
            elif unit == 'w':
                date_delta += relativedelta(weeks=value)
            elif unit == 'y':
                date_delta += relativedelta(years=value)
            elif unit == 'rmo':
                date_delta += self._next_monthday(value, starting_date) - \
                    starting_date
        return starting_date + date_delta

    def _next_weekday(self, weekday, starting_date=datetime.datetime.now()):
        """
        Method to get the next week day of a given date.

        Arguments:
            weekday (int): Integer representation of weekday (0 == monday)
            starting_date (datetime): Date to compare

        Returns:
            next_week_day (datetime)
        """

        if weekday == starting_date.weekday():
            starting_date = starting_date + relativedelta(days=1)

        weekday = self._weekday(weekday)

        date_delta = relativedelta(day=starting_date.day, weekday=weekday,)
        return starting_date + date_delta

    def _next_monthday(self, months, starting_date=datetime.datetime.now()):
        """
        Method to get the difference between for the next same week day of the
        month for the specified months.

        For example the difference till the next 3rd Wednesday of the month
        after the next `months` months.

        Arguments:
            months (int): Number of months to skip.

        Returns:
            next_week_day ()
        """
        weekday = self._weekday(starting_date.weekday())

        first_month_weekday = starting_date - \
            relativedelta(day=1, weekday=weekday(1))
        month_weekday = (starting_date - first_month_weekday).days // 7 + 1

        date_delta = relativedelta(
            months=months,
            day=1,
            weekday=weekday(month_weekday)
        )
        return starting_date + date_delta

    def _weekday(self, weekday):
        """
        Method to return the dateutil.relativedelta weekday.

        Arguments:
            weekday (int): Weekday, Monday == 0

        Returns:
            weekday (datetil.relativedelta.weekday)
        """

        if weekday == 0:
            weekday = MO
        elif weekday == 1:
            weekday = TU
        elif weekday == 2:
            weekday = WE
        elif weekday == 3:
            weekday = TH
        elif weekday == 4:
            weekday = FR
        elif weekday == 5:
            weekday = SA
        elif weekday == 6:
            weekday = SU
        return weekday
