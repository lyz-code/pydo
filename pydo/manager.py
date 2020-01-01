"""
Module to store the main class of pydo

Classes:
    TaskManager: Class to manipulate the tasks data
    ConfigManager: Class to manipulate the pydo configuration
"""
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
    'report.list.columns': {
        'default': 'id, title, project_id, priority, tags',
        'choices': 'id, title, description, project_id, priority, tags, '
        'agile, estimate, willpower, value, fun',
        'description': 'Ordered coma separated list of Task attributes '
        'to print',
    },
    'report.list.labels': {
        'default': 'ID, Title, Project, Pri, Tags',
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
        _close: Closes a task.
        _parse_arguments: Parse a Taskwarrior like add query into task
            attributes

    Public attributes:
        fulid (fulid object): Fulid manager and generator object.
        log (logging object): Logger
        session (session object): Database session
    """

    def __init__(self, session):
        super().__init__(session, Task)
        self.config = ConfigManager(self.session)
        self.fulid = fulid(
            self.config.get('fulid.characters'),
            self.config.get('fulid.forbidden_characters'),
        )

    def _parse_arguments(self, add_arguments):
        """
        Parse a Taskwarrior like add query into task attributes

        Arguments:
            add_arguments (str): Taskwarrior like add argument string.

        Returns:
            attributes (dict): Dictionary with the attributes of the task.
        """

        attributes = {
            'agile': None,
            'body': None,
            'title': [],
            'estimate': None,
            'fun': None,
            'priority': None,
            'project_id': None,
            'tags': [],
            'value': None,
            'willpower': None,
        }
        for argument in add_arguments:
            if re.match(r'^(pro|project):', argument):
                attributes['project_id'] = argument.split(':')[1]
            elif re.match(r'^(ag|agile):', argument):
                attributes['agile'] = argument.split(':')[1]
            elif re.match(r'^(pri|priority):', argument):
                attributes['priority'] = int(argument.split(':')[1])
            elif re.match(r'^(wp|willpower):', argument):
                attributes['willpower'] = int(argument.split(':')[1])
            elif re.match(r'^(est|estimate):', argument):
                attributes['estimate'] = float(argument.split(':')[1])
            elif re.match(r'^(vl|value):', argument):
                attributes['value'] = int(argument.split(':')[1])
            elif re.match(r'^fun:', argument):
                attributes['fun'] = int(argument.split(':')[1])
            elif re.match(r'^body:', argument):
                attributes['body'] = argument.split(':')[1]
            elif re.match(r'^\+', argument):
                attributes['tags'].append(argument.replace('+', ''))
            else:
                attributes['title'].append(argument)
        attributes['title'] = ' '.join(attributes['title'])
        return attributes

    def add(
        self,
        title,
        agile=None,
        body=None,
        estimate=None,
        fun=None,
        priority=None,
        project_id=None,
        tags=[],
        value=None,
        willpower=None,
    ):
        """
        Use parent method to create a new task

        Arguments:
            agile (str): Task agile state.
            title (str): Title of the task.
            body (str): Description of the task.
            estimate (float): Estimate size of the task.
            fun (int): Fun size of the task.
            priority (int): Task priority.
            project_id (str): Project id.
            tags (list): List of tag ids.
            title (str): Title of the task.
            value (int): Objective/Bussiness value of the task.
            willpower (int): Willpower consumption of the task.
        """

        # Define ID
        last_fulid = self.session.query(
            Task
        ).filter_by(state='open').order_by(Task.id.desc()).first()

        if last_fulid is not None:
            last_fulid = last_fulid.id

        new_fulid = self.fulid.new(last_fulid)

        task_attributes = {
            'id': new_fulid.str,
            'agile': agile,
            'body': body,
            'title': title,
            'estimate': estimate,
            'fun': fun,
            'state': 'open',
            'priority': priority,
            'value': value,
            'tags': [],
            'willpower': willpower,
        }

        # Define Project
        if project_id is not None:
            project = self.session.query(Project).get(project_id)
            if project is None:
                project = Project(id=project_id, description='')
                self.session.add(project)
                self.session.commit()
            task_attributes['project'] = project

        # Define tags
        for tag_id in tags:
            tag = self.session.query(Tag).get(tag_id)
            if tag is None:
                tag = Tag(id=tag_id, description='')
                self.session.add(tag)
                self.session.commit()
            task_attributes['tags'].append(tag)

        # Test the task attributes are into the available choices
        if agile not in self.config.get('task.agile.states').split(', '):
            raise ValueError(
                'Agile state {} is not between the specified '
                'by task.agile.states'.format(agile)
            )

        self._add(
            task_attributes,
            task_attributes['id'],
            task_attributes['title'],
        )

    def _close(self, id, state):
        """
        Method to close a task

        Arguments:
            id (str): Ulid of the task
            state (str): State of the task once it's closed
        """

        if len(id) < 10:
            open_tasks = self.session.query(Task).filter_by(state='open')
            open_task_fulids = [task.id for task in open_tasks]
            id = self.fulid.sulid_to_fulid(id, open_task_fulids)

        task = self.session.query(Task).get(id)

        task.state = state
        task.closed_utc = datetime.datetime.now()

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
