#!/usr/bin/python3

# Copyright (C) 2019 lyz <lyz@riseup.net>
# This file is part of pydo.
#
# pydo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pydo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pydo.  If not, see <http://www.gnu.org/licenses/>.

from pydo.cli import load_logger, load_parser
from pydo import models
from pydo.manager import TaskManager, ConfigManager
from pydo.ops import export, install
from pydo.reports import TaskReport, Projects, Tags
from sqlalchemy.orm import sessionmaker

import logging

import sys


def task_modify_commands(session, args):
    """
    Function to call the different TaskManager actions.

    Arguments:
        session (session object): Database session
        args (argparse): Parsed arguments.
    """

    task_manager = TaskManager(session)

    if args.subcommand == 'add':
        attributes = task_manager._parse_arguments(args.add_argument)
        if 'title' not in attributes:
            raise ValueError('The task must have a title')
        task_manager.add(
            **attributes
        )
    elif args.subcommand == 'mod':
        attributes = task_manager._parse_arguments(args.modify_argument)
        if args.parent:
            task_manager.modify_parent(
                args.ulid,
                **attributes
            )
        else:
            task_manager.modify(
                args.ulid,
                **attributes
            )
    elif args.subcommand == 'del':
        task_manager.delete(id=args.ulid, parent=args.parent)
    elif args.subcommand == 'freeze':
        task_manager.freeze(id=args.ulid, parent=args.parent)
    elif args.subcommand == 'done':
        task_manager.complete(id=args.ulid, parent=args.parent)
    elif args.subcommand == 'unfreeze':
        task_manager.unfreeze(id=args.ulid, parent=args.parent)


def main(argv=sys.argv[1:]):
    parser = load_parser()
    args = parser.parse_args(argv)
    load_logger()

    connection = models.engine.connect()
    session = sessionmaker()(bind=connection)
    config = ConfigManager(session)

    if args.subcommand == 'install':
        install(session, logging.getLogger('main'))
    elif args.subcommand in [
        'add',
        'del',
        'done',
        'freeze',
        'mod',
        'unfreeze',
    ]:
        task_modify_commands(session, args)
    elif args.subcommand in ['open', None]:
        open_tasks = session.query(models.Task).filter_by(
            state='open',
            type='task',
        )
        TaskReport(session).print(
            tasks=open_tasks,
            columns=config.get('report.open.columns').split(', '),
            labels=config.get('report.open.labels').split(', ')
        )
    elif args.subcommand in ['repeating', 'recurring']:
        open_recurring_tasks = session.query(models.RecurrentTask).filter_by(
            state='open',
            recurrence_type=args.subcommand,
        )
        TaskReport(session, models.RecurrentTask).print(
            tasks=open_recurring_tasks,
            columns=config.get(
                'report.{}.columns'.format(args.subcommand)
            ).split(', '),
            labels=config.get(
                'report.{}.labels'.format(args.subcommand)
            ).split(', ')
        )
    elif args.subcommand == 'frozen':
        TaskReport(session, models.RecurrentTask).print(
            tasks=session.query(models.Task).filter_by(
                state='frozen',
            ),
            columns=config.get('report.frozen.columns').split(', '),
            labels=config.get('report.frozen.labels').split(', ')
        )
    elif args.subcommand == 'projects':
        Projects(session).print(
            columns=config.get('report.projects.columns').split(', '),
            labels=config.get('report.projects.labels').split(', ')
        )
    elif args.subcommand == 'tags':
        Tags(session).print(
            columns=config.get('report.tags.columns').split(', '),
            labels=config.get('report.tags.labels').split(', ')
        )
    elif args.subcommand == 'export':
        export(logging.getLogger('main'))
