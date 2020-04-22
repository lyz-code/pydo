"""
Module to store the main class of pydo

Classes:
    TaskManager: Class to manipulate the tasks data
    ConfigManager: Class to manipulate the pydo configuration
"""
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
from pydo.cli import load_logger
from pydo.fulids import fulid
from pydo.models import Task, Config, Project, Tag

import datetime
import json
import logging
import re

pydo_default_config = {
    'verbose_level': {
        'default': 'info',
        'choices': ['info', 'debug', 'warning'],
        'description': 'Set the logging verbosity level',
    },
    'fulid.characters': {
        'default': 'asdfghjwer',
        'choices': '',
        'description': 'Characters used for the generation of identifiers.'
    },
    'fulid.forbidden_characters': {
        'default': 'ilou|&:;()<>~*@?!$#[]{}\\/\'"`',
        'choices': '',
        'description': 'Characters forbidden to be used in the generation'
        'of ids, due to ulid converting them to numbers or because they'
        'have a meaning for the terminal',
    },
    'report.date_format': {
        'default': '%Y-%m-%d %H:%M',
        'choices': '',
        'description': 'Datetime strftime compatible string to print dates',
    },
    'report.list.columns': {
        'default': 'id, title, project_id, priority, tags, due',
        'choices': 'id, title, description, project_id, priority, tags, '
        'agile, estimate, willpower, value, fun',
        'description': 'Ordered coma separated list of Task attributes '
        'to print',
    },
    'report.list.labels': {
        'default': 'ID, Title, Project, Pri, Tags, Due',
        'choices': '',
        'description': 'Ordered coma separated list of names for the '
        'Task attributes to print',
    },
    'report.projects.columns': {
        'default': 'id, task.count, description',
        'choices': '',
        'description': 'Ordered coma separated list of Project attributes '
        'to print',
    },
    'report.projects.labels': {
        'default': 'Name, Tasks, Description',
        'choices': '',
        'description': 'Ordered coma separated list of names for the '
        'Project attributes to print',
    },
    'report.tags.columns': {
        'default': 'id, task.count, description',
        'choices': '',
        'description': 'Ordered coma separated list of Tag attributes '
        'to print',
    },
    'report.tags.labels': {
        'default': 'Name, Tasks, Description',
        'choices': '',
        'description': 'Ordered coma separated list of names for the '
        'Tag attributes to print',
    },
    'task.default.agile': {
        'default': None,
        'choices': 'See task.agile.states',
        'description': 'Default task agile state if not specified.',
    },
    'task.agile.states': {
        'default': 'backlog, todo, doing, review, complete',
        'choices': '',
        'description': 'Coma separated list of agile states the task '
        'can transition to.',
    },
}

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
        _update: Method to update an existing table item

    Public attributes:
        session (session object): Database session
        log (logging object): Logger
    """

    def __init__(self, session, table_model):
        self.log = logging.getLogger('main')
        self.model = table_model
        self.session = session

    def _add(self, object_values, id, title):
        """
        Method to create a new table item

        Arguments:
            title (str): object title
            id (str): object identifier
            object_values (dict): Dictionary with the column identifier
                as keys.
        """

        obj = self.model(id, title)

        for attribute_key, attribute_value in object_values.items():
            setattr(obj, attribute_key, attribute_value)

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
        delete: Deletes a task.
        complete: Completes a task.

    Internal methods:
        _add: Parent method to add table elements.
        _update: Parent method to update table elements.
        _close: Closes a task.
        _parse_attribute: Parse a Taskwarrior like add argument into a task
            attribute.
        _parse_arguments: Parse a Taskwarrior like add query into task
            attributes.
        _get_fulid: Method to get the task's fulid if necessary.
        _set: Method to set the task's attributes and get its fulid.

    Public attributes:
        fulid (fulid object): Fulid manager and generator object.
        log (logging object): Logger
        session (session object): Database session
    """

    def __init__(self, session):
        super().__init__(session, Task)
        self.config = ConfigManager(self.session)
        self.date = DateManager()
        self.fulid = fulid(
            self.config.get('fulid.characters'),
            self.config.get('fulid.forbidden_characters'),
        )

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
                if attribute['type'] == 'str':
                    return attribute_id, add_argument.split(':')[1]
                elif attribute['type'] == 'int':
                    return attribute_id, int(add_argument.split(':')[1])
                elif attribute['type'] == 'float':
                    return attribute_id, float(add_argument.split(':')[1])
                elif attribute['type'] == 'date':
                    return attribute_id, self.date.convert(
                        ":".join(add_argument.split(':')[1:])
                    )
                elif attribute['type'] == 'tag':
                    return attribute_id, re.sub(r'^[+-]', '', add_argument)
        return 'title', add_argument

    def _parse_arguments(self, add_arguments):
        """
        Parse a Taskwarrior like add query into task attributes

        Arguments:
            add_arguments (list): Taskwarrior like add argument list.

        Returns:
            attributes (dict): Dictionary with the attributes of the task.
        """

        attributes = {
            'agile': None,
            'body': None,
            'due': None,
            'title': [],
            'estimate': None,
            'fun': None,
            'priority': None,
            'project_id': None,
            'tags': [],
            'tags_rm': [],
            'value': None,
            'willpower': None,
        }

        for argument in add_arguments:
            attribute_id, attribute_value = self._parse_attribute(argument)
            if attribute_id in ['tags', 'tags_rm', 'title']:
                attributes[attribute_id].append(attribute_value)
            else:
                attributes[attribute_id] = attribute_value

        attributes['title'] = ' '.join(attributes['title'])
        return attributes

    def _get_fulid(self, id):
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
            open_tasks = self.session.query(Task).filter_by(state='open')
            open_task_fulids = [task.id for task in open_tasks]
            fulid = self.fulid.sulid_to_fulid(id, open_task_fulids)

        return fulid

    def _set_project(
        self,
        task_attributes,
        project_id=None
    ):
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

    def _set_tags(
        self,
        task_attributes,
        tags=[]
    ):
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

    def _rm_tags(
        self,
        task_attributes,
        tags_rm=[]
    ):
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

    def _set_agile(
        self,
        task_attributes,
        agile=None
    ):
        """
        Method to set the agile attribute.

        If the agile tag value isn't between the specified ones,
        a `ValueError` will be raised.

        Arguments:
            task_attributes (dict): Dictionary with the attributes of the task.
            agile (str): Task agile state.
        """
        if agile is not None and \
                agile not in self.config.get('task.agile.states').split(', '):
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

        self._set_project(task_attributes, project_id)

        if id is not None:
            fulid = self._get_fulid(id)

            task = self.session.query(Task).get(fulid)
            task_attributes['tags'] = task.tags

            self._rm_tags(task_attributes, tags_rm)

        self._set_tags(task_attributes, tags)
        self._set_agile(task_attributes, agile)

        for key, value in kwargs.items():
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

        # Define ID
        last_fulid = self.session.query(
            Task
        ).filter_by(state='open').order_by(Task.id.desc()).first()

        if last_fulid is not None:
            last_fulid = last_fulid.id

        new_fulid = self.fulid.new(last_fulid)

        fulid, task_attributes = self._set(None,
                                           project_id,
                                           tags,
                                           None,
                                           agile,
                                           title=title,
                                           state='open',
                                           **kwargs)

        self._add(
            task_attributes,
            new_fulid.str,
            task_attributes['title'],
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
        fulid, task_attributes = self._set(id,
                                           project_id,
                                           tags,
                                           tags_rm,
                                           agile,
                                           **kwargs)

        self._update(
            fulid,
            task_attributes,
        )

    def _close(self, id, state):
        """
        Method to close a task

        Arguments:
            id (str): Ulid of the task
            state (str): State of the task once it's closed
        """

        id = self._get_fulid(id)

        task = self.session.query(Task).get(id)

        task.state = state
        task.closed = datetime.datetime.now()

        self.session.commit()
        self.log.debug(
            '{} task {}: {}'.format(
                state.title(),
                task.id,
                task.title
            )
        )

    def delete(self, id):
        """
        Method to delete a task

        Arguments:
            id (str): Ulid of the task
        """

        self._close(id, 'deleted')

    def complete(self, id):
        """
        Method to complete a task

        Arguments:
            id (str): Ulid of the task
        """

        self._close(id, 'completed')


class ConfigManager(TableManager):
    """
    Class to manipulate the pydo configuration.

    Arguments:
        session (session object): Database session

    Public methods:
        add: Creates a new configuration element.
        get: Return the configuration value.
        seed: Generates the default config data in an idempotent way.

    Internal methods:

    Public attributes:
        session (session object): Database session
        log (logging object): Logger
    """

    def __init__(self, session):
        super().__init__(session, Config)

    def add(
        self,
        property,
        choices=None,
        description=None,
        user=None,
        default=None
    ):
        """
        Use parent method to create a new configuration

        Arguments:
            choices (str): JSON list of possible values.
            default (str): Default value of the property.
            description (str): Property description.
            property (str): Property identifier
            user (str): User defined value of the property.
        """

        config_attributes = {
            'choices': choices,
            'default': default,
            'description': description,
            'property': property,
            'user': user,
        }
        self._add(
            config_attributes,
            config_attributes['property'],
            config_attributes['description'],
        )

    def seed(self):
        """
        Generates the default config data in an idempotent way.
        """

        for attribute_key, attribute_data in pydo_default_config.items():
            config = self.session.query(Config).get(attribute_key)
            if config is not None:
                config.description = attribute_data['description']
                config.default = attribute_data['default']
                config.choices = json.dumps(attribute_data['choices'])
                self.session.add(config)
                self.session.commit()
            else:
                self.add(
                    property=attribute_key,
                    description=attribute_data['description'],
                    default=attribute_data['default'],
                    choices=json.dumps(attribute_data['choices']),
                    user=None
                )

    def get(self, id):
        """
        Return the configuration value.

        Arguments:
            id (str): Configuration element identifier

        Returns:
            value (str): Configuration value
            raises: ValueError if element is not found
        """

        config = self._get(id)

        if config.user is not None:
            return config.user
        else:
            return config.default


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
        elif re.match(r'now', human_date):
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
