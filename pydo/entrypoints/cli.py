"""
Module to store the command line interface.

Functions:
    add: Define the interface to add tasks.
    cli: Define the main click group.
    do: Define the interface to complete tasks
    null: Does nothing.
"""

import logging
import sys
from typing import Any, Dict, Tuple

import click
from click_default_group import DefaultGroup

from pydo import exceptions, services, views
from pydo.entrypoints import (load_config, load_logger, load_repository,
                              load_session)

load_logger()
log = logging.getLogger(__name__)


@click.group(cls=DefaultGroup, default="open", default_if_no_args=True)
@click.option(
    "-c",
    "--Config_path",
    default="~/.local/share/pydo/config.yaml",
    help="configuration file path",
    envvar="PYDO_CONFIG_PATH",
)
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def cli(ctx: Any, config_path: str, verbose: bool) -> None:
    """
    Free software command line task manager.
    """

    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj["config"] = load_config(config_path)
    ctx.obj["session"] = load_session(ctx.obj["config"])
    ctx.obj["repo"] = load_repository(ctx.obj["config"], ctx.obj["session"])
    ctx.obj["repo"].apply_migrations()
    load_logger(verbose)


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.argument("task_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def add(ctx: Any, task_args: Tuple) -> None:
    """
    Subcommand to add tasks.
    """

    try:
        task_attributes: Dict = services.parse_task_arguments(list(task_args))
    except exceptions.DateParseError as e:
        log.error(str(e))
        sys.exit(1)

    try:
        services.add_task(ctx.obj["repo"], task_attributes)
    except exceptions.TaskAttributeError as e:
        log.error(str(e))
        sys.exit(1)


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.option("-d", "--close_date", default="now")
@click.option("-p", "--close_parent", is_flag=True)
@click.argument("task_filter", nargs=-1, required=True, type=click.UNPROCESSED)
@click.pass_context
def do(ctx: Any, task_filter: Tuple, close_date: str, close_parent: bool) -> None:
    """
    Subcommand to complete tasks.
    """
    try:
        services.do_tasks(
            ctx.obj["repo"], " ".join(task_filter), close_date, close_parent
        )
    except exceptions.EntityNotFoundError as e:
        log.error(str(e))
        sys.exit(1)


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.option("-d", "--close_date", default="now")
@click.option("-p", "--close_parent", is_flag=True)
@click.argument("task_filter", nargs=-1, required=True, type=click.UNPROCESSED)
@click.pass_context
def rm(ctx: Any, task_filter: Tuple, close_date: str, close_parent: bool) -> None:
    """
    Subcommand to delete tasks.
    """
    try:
        services.rm_tasks(
            ctx.obj["repo"], " ".join(task_filter), close_date, close_parent
        )
    except exceptions.EntityNotFoundError as e:
        log.error(str(e))
        sys.exit(1)


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.option(
    "-p",
    "--modify_parent",
    help="For children tasks, also modify the parent task.",
    is_flag=True,
)
@click.argument("task_filter", required=True)
@click.argument("task_args", nargs=-1, required=True, type=click.UNPROCESSED)
@click.pass_context
def mod(ctx: Any, task_filter: str, task_args: Tuple, modify_parent: bool) -> None:
    """
    Subcommand to modify tasks.
    """
    try:
        task_attributes: Dict = services.parse_task_arguments(list(task_args))
    except exceptions.DateParseError as e:
        log.error(str(e))
        sys.exit(1)

    try:
        services.modify_tasks(
            ctx.obj["repo"], task_filter, task_attributes, modify_parent
        )
    except exceptions.EntityNotFoundError as e:
        log.error(str(e))
        sys.exit(1)


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.argument("task_filter", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def open(ctx: Any, task_filter: Tuple) -> None:
    """
    Show the open tasks.
    """

    try:
        task_attributes: Dict = services.parse_task_arguments(list(task_filter))
    except exceptions.DateParseError as e:
        log.error(str(e))
        sys.exit(1)

    try:
        views.open(ctx.obj["repo"], ctx.obj["config"], task_attributes)
    except exceptions.EntityNotFoundError as e:
        log.info(str(e))
        sys.exit(0)


@cli.command()
def null() -> None:
    """
    Function that does nothing.

    Used for the tests until we have a better solution.
    """
    pass


if __name__ == "__main__":
    cli(obj={})

# def load_parser():
#     """
#     Function to define the command line arguments.
#     """
#
#     # Argparse
#     parser = argparse.ArgumentParser(
#         description="CLI task manager built with Python and SQLite.",
#     )
#
#     subparser = parser.add_subparsers(dest="subcommand", help="subcommands")
#     subparser.add_parser("install")
#
#     modify_parser = subparser.add_parser("mod")
#     modify_parser.add_argument(
#         "ulid", type=str, help="Task ulid",
#     )
#     modify_parser.add_argument(
#         "-p", "--parent", action="store_true", help="Modify parent task instead",
#     )
#     modify_parser.add_argument(
#         "modify_argument",
#         type=str,
#         help="Task modify arguments",
#         default=None,
#         nargs=argparse.REMAINDER,
#     )
#
#     delete_parser = subparser.add_parser("del")
#     delete_parser.add_argument(
#         "ulid", type=str, help="Task ulid",
#     )
#     delete_parser.add_argument(
#         "-p", "--parent", action="store_true", help="Delete parent task instead",
#     )
#
#     complete_parser = subparser.add_parser("done")
#     complete_parser.add_argument(
#         "ulid", type=str, help="Task ulid",
#     )
#     complete_parser.add_argument(
#         "-p", "--parent", action="store_true", help="Complete parent task instead",
#     )
#     freeze_parser = subparser.add_parser("freeze")
#     freeze_parser.add_argument(
#         "ulid", type=str, help="Task ulid",
#     )
#     freeze_parser.add_argument(
#         "-p", "--parent", action="store_true", help="Freeze parent task instead",
#    )
#
#    unfreeze_parser = subparser.add_parser("unfreeze")
#    unfreeze_parser.add_argument(
#        "ulid", type=str, help="Task ulid",
#    )
#    unfreeze_parser.add_argument(
#        "-p", "--parent", action="store_true", help="Unfreeze parent task instead",
#    )
#
#    subparser.add_parser("open")
#    subparser.add_parser("recurring")
#    subparser.add_parser("repeating")
#    subparser.add_parser("frozen")
#    subparser.add_parser("projects")
#    subparser.add_parser("tags")
#    subparser.add_parser("export")
#
#    return parser
