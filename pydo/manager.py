"""
Module to store the main class of pydo

Classes:
    TaskManager: Class to manipulate the tasks data
    ConfigManager: Class to manipulate the pydo configuration
"""
from pydo.cli import load_logger
from pydo.fulids import fulid
from pydo.models import Task, Config

import datetime
import json
import logging

pydo_default_config = {
    'verbose_level': {
        'default': 'info',
        'choices': ['info', 'debug', 'warning'],
        'description': 'Set the logging verbosity level',
    },
    'fulid_characters': {
        'default': 'asdfghjwer',
        'choices': '',
        'description': 'Characters used for the generation of identifiers.'
    },
    'fulid_forbidden_characters': {
        'default': 'ilou|&:;()<>~*@?!$#[]{}\\/\'"`',
        'choices': '',
        'description': 'Characters forbidden to be used in the generation'
        'of ids, due to ulid converting them to numbers or because they'
        'have a meaning for the terminal',
    }
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

    def _add(self, object_values, id, description):
        """
        Method to create a new table item

        Arguments:
            description (str): object description
            id (str): object identifier
            object_values (dict): Dictionary with the column identifier
                as keys.
        """

        obj = self.model(id, description)

        for attribute_key, attribute_value in object_values.items():
            setattr(obj, attribute_key, attribute_value)

        self.session.add(obj)
        self.session.commit()
        self.log.debug(
            'Added {} {}: {}'.format(
                self.model.__name__.lower(),
                id,
                description,
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

    Public attributes:
        fulid (fulid object): Fulid manager and generator object.
        log (logging object): Logger
        session (session object): Database session
    """

    def __init__(self, session):
        super().__init__(session, Task)
        self.config = ConfigManager(self.session)
        self.fulid = fulid(
            self.config.get('fulid_characters'),
            self.config.get('fulid_forbidden_characters'),
        )

    def add(self, description, project=None):
        """
        Use parent method to create a new task

        Arguments:
            description (str): Description of the task
            project (str): Task project
        """

        last_fulid = self.session.query(
            Task
        ).filter_by(state='open').order_by(Task.id.desc()).first()

        if last_fulid is not None:
            last_fulid = last_fulid.id

        new_fulid = self.fulid.new(last_fulid)

        task_attributes = {
            'id': new_fulid.str,
            'description': description,
            'state': 'open',
            'project': project,
        }
        self._add(
            task_attributes,
            task_attributes['id'],
            task_attributes['description'],
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
                task.description
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
