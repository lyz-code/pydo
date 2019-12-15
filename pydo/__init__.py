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
from pydo.manager import TaskManager
from pydo.models import engine
from pydo.ops import install
from pydo.reports import List
from sqlalchemy.orm import sessionmaker

import logging

__version__ = '0.1.0'


def main():
    parser = load_parser()
    args = parser.parse_args()
    load_logger()

    connection = engine.connect()
    session = sessionmaker()(bind=connection)

    if args.subcommand == 'install':

        install(session, logging.getLogger('main'))
    elif args.subcommand in ['add', 'del', 'done']:
        task_manager = TaskManager(session)

        if args.subcommand == 'add':
            task_manager.add(
                description=args.description,
                project=args.project,
            )
        elif args.subcommand == 'del':
            task_manager.delete(id=args.ulid)
        elif args.subcommand == 'done':
            task_manager.complete(id=args.ulid)
    elif args.subcommand in ['list', None]:
        columns = ['id', 'description', 'project']
        labels = ['ID', 'Description', 'Project']
        List(session).print(
            columns=columns,
            labels=labels
        )
