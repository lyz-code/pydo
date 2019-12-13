"""
Module to store the main class of pydo

Classes:
    TaskManager: Class to manipulate the tasks data
    ConfigManager: Class to manipulate the pydo configuration
"""
from pydo.cli import load_logger
from pydo.models import Task, Config

import datetime
import json
import logging
import ulid

pydo_default_config = {
    'verbose_level': {
        'default': 'info',
        'choices': ['info', 'debug', 'warning'],
        'description': 'Set the logging verbosity level',
    }
}

load_logger()


class TableManager:
    """
    Abstract Class to manipulate a database table data.

    Arguments:
        session (session object): Database session
        table_model (Sqlalchemy model): Table model

    Public methods:
        short_ulids: Return a the suild of a list of ulids.

    Internal methods:
        _add: Method to create a new table item

    Public attributes:
        session (session object): Database session
        log (logging object): Logger
    """

    def __init__(self, session, table_model):
        self.log = logging.getLogger('main')
        self.session = session
        self.model = table_model

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

    def short_ulids(self, ulids):
        """
        Method to shorten the length of the ulids so we need to type less
        while retaining the uniqueness.

        The ulids as stated [here](https://github.com/ulid/spec) have to parts
        the first bytes are an encoding of the date, while the last are
        an encoding of randomness.

        Therefore, for all the ulids that come, we're going to transform
        to lower and reverse them to search the minimum characters that
        uniquely identify each ulids.

        Once we've got all return the equivalence in a dictionary.

        Arguments:
            uilds (list): List of ulids to shorten.

        Return
            sulids (dict): List of associations between ulids and sulids.
        """
        work_ulids = [ulid.lower()[::-1] for ulid in ulids]

        char_num = 1
        while True:
            work_sulids = [ulid[:char_num] for ulid in work_ulids]
            if len(work_sulids) == len(set(work_sulids)):
                sulids = {
                    ulids[index]: work_sulids[index][::-1]
                    for index in range(0, len(ulids))
                }
                return sulids
            char_num += 1


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
        session (session object): Database session
        log (logging object): Logger
    """

    def __init__(self, session):
        super().__init__(session, Task)

    def add(self, description, project=None):
        """
        Use parent method to create a new task

        Arguments:
            description (str): Description of the task
            project (str): Task project
        """

        task_attributes = {
            'ulid': ulid.new().str,
            'description': description,
            'state': 'open',
            'project': project,
        }
        self._add(
            task_attributes,
            task_attributes['ulid'],
            task_attributes['description'],
        )

    def _close(self, id, state):
        """
        Method to close a task

        Arguments:
            id (str): Ulid of the task
            state (str): State of the task once it's closed
        """

        task = self.session.query(Task).get(id)

        task.state = state
        task.closed_utc = datetime.datetime.now()

        self.session.commit()
        self.log.debug(
            '{} task {}: {}'.format(
                state.title(),
                task.ulid,
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
