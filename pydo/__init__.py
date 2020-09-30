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

# import logging
# import os
# import sys
#
# from pydo import model
# from pydo.config import Config
#
#
# def task_modify_commands(session, args):
#     """
#     Function to call the different TaskManager actions.
#
#     Arguments:
#         session (session object): Database session
#         args (argparse): Parsed arguments.
#     """
#
#     task_manager = TaskManager(session)
#
#     elif args.subcommand == "mod":
#         attributes = task_manager._parse_arguments(args.modify_argument)
#         if args.parent:
#             task_manager.modify_parent(args.ulid, **attributes)
#         else:
#             task_manager.modify(args.ulid, **attributes)
#     elif args.subcommand == "del":
#         task_manager.delete(id=args.ulid, parent=args.parent)
#     elif args.subcommand == "freeze":
#         task_manager.freeze(id=args.ulid, parent=args.parent)
#     elif args.subcommand == "done":
#         task_manager.complete(id=args.ulid, parent=args.parent)
#     elif args.subcommand == "unfreeze":
#         task_manager.unfreeze(id=args.ulid, parent=args.parent)
#
#
# def main(argv=sys.argv[1:]):
#     # parser = load_parser()
#     # args = parser.parse_args(argv)
#
#     connection = model.engine.connect()
#     session = sessionmaker()(bind=connection)
#
#     if args.subcommand == "install":
#         install(session, logging.getLogger("main"))
#     elif args.subcommand in [
#         "freeze",
#         "mod",
#         "unfreeze",
#     ]:
#         task_modify_commands(session, args)
#     elif args.subcommand in ["open", None]:
#         open_tasks = session.query(model.Task).filter_by(state="open", type="task",)
#         TaskReport(session).print(
#             tasks=open_tasks,
#             columns=config.get("report.open.columns"),
#             labels=config.get("report.open.labels"),
#         )
#     elif args.subcommand in ["repeating", "recurring"]:
#         open_recurring_tasks = session.query(model.RecurrentTask).filter_by(
#             state="open", recurrence_type=args.subcommand,
#         )
#         TaskReport(session, model.RecurrentTask).print(
#             tasks=open_recurring_tasks,
#             columns=config.get("report.{}.columns".format(args.subcommand)),
#             labels=config.get("report.{}.labels".format(args.subcommand)),
#         )
#     elif args.subcommand == "frozen":
#         TaskReport(session, model.RecurrentTask).print(
#             tasks=session.query(model.Task).filter_by(state="frozen",),
#             columns=config.get("report.frozen.columns"),
#             labels=config.get("report.frozen.labels"),
#         )
#     elif args.subcommand == "projects":
#         Projects(session).print(
#             columns=config.get("report.projects.columns"),
#             labels=config.get("report.projects.labels"),
#         )
#     elif args.subcommand == "tags":
#         Tags(session).print(
#             columns=config.get("report.tags.columns"),
#             labels=config.get("report.tags.labels"),
#         )
#     elif args.subcommand == "export":
#         export(logging.getLogger("main"))
