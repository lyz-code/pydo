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
from pydo.models import engine
from pydo.manager import TaskManager, ConfigManager
from pydo.ops import export, install
from pydo.reports import List, Projects, Tags
from sqlalchemy.orm import sessionmaker

import logging


def main():
    parser = load_parser()
    args = parser.parse_args()
    load_logger()

    connection = engine.connect()
    session = sessionmaker()(bind=connection)
    config = ConfigManager(session)

    if args.subcommand == 'install':
        install(session, logging.getLogger('main'))
    elif args.subcommand in ['add', 'mod', 'del', 'done']:
        task_manager = TaskManager(session)

        if args.subcommand == 'add':
            attributes = task_manager._parse_arguments(args.add_argument)
            task_manager.add(
                **attributes
            )
        elif args.subcommand == 'mod':
            attributes = task_manager._parse_arguments(args.modify_argument)
            task_manager.modify(
                args.ulid,
                **attributes
            )
        elif args.subcommand == 'del':
            task_manager.delete(id=args.ulid)
        elif args.subcommand == 'done':
            task_manager.complete(id=args.ulid)
    elif args.subcommand in ['list', None]:
        List(session).print(
            columns=config.get('report.list.columns').split(', '),
            labels=config.get('report.list.labels').split(', ')
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
