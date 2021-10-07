"""Command line interface definition."""

import logging
import sys
from typing import Any, Optional, Tuple

import click
from click.core import Context
from click_default_group import DefaultGroup
from pydantic import ValidationError
from repository_orm import EntityNotFoundError

from .. import services, version, views
from ..model.task import RecurrentTask, TaskState
from .utils import (
    _parse_changes,
    _parse_task_selector,
    get_repo,
    load_config,
    load_logger,
)

load_logger()
log = logging.getLogger(__name__)


@click.group(cls=DefaultGroup, default="open", default_if_no_args=True)
@click.version_option(version="", message=version.version_info())
@click.option("-v", "--verbose", is_flag=True)
@click.option(
    "-c",
    "--config_path",
    default="~/.local/share/pydo/config.yaml",
    help="configuration file path",
    envvar="PYDO_CONFIG_PATH",
)
@click.pass_context
def cli(ctx: Context, config_path: str, verbose: bool) -> None:
    """Command line interface main click entrypoint."""
    ctx.ensure_object(dict)

    ctx.obj["config"] = load_config(config_path)
    ctx.obj["repo"] = get_repo(ctx.obj["config"])
    load_logger(verbose)


# ---------------------------------------------------------------
#                   Actions over tasks
# ---------------------------------------------------------------


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("task_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def add(ctx: Any, task_args: Tuple[str]) -> None:
    """Add a task."""
    change = _parse_changes(task_args)
    try:
        services.add_task(ctx.obj["repo"], change)
    except ValidationError as error:
        log.error(str(error))
        sys.exit(1)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.option("-d", "--close_date", default="now")
@click.option("-p", "--parent", is_flag=True)
@click.argument("task_filter", nargs=-1, required=True, type=click.UNPROCESSED)
@click.pass_context
def do(ctx: Any, task_filter: Tuple[str], close_date: str, parent: bool) -> None:
    """Complete tasks."""
    task_selector = _parse_task_selector(task_filter)
    try:
        services.do_tasks(
            ctx.obj["repo"],
            task_selector,
            close_date,
            parent,
        )
    except EntityNotFoundError as error:
        log.error(str(error))
        sys.exit(1)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.option("-d", "--close_date", default="now")
@click.option("-p", "--parent", is_flag=True)
@click.argument("task_filter", nargs=-1, required=True, type=click.UNPROCESSED)
@click.pass_context
def rm(ctx: Any, task_filter: Tuple[str], close_date: str, parent: bool) -> None:
    """Delete tasks."""
    task_selector = _parse_task_selector(task_filter)
    try:
        services.rm_tasks(ctx.obj["repo"], task_selector, close_date, parent)

    except EntityNotFoundError as error:
        log.error(str(error))
        sys.exit(1)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.option(
    "--parent",
    help="For children tasks, also modify the parent task.",
    is_flag=True,
)
@click.argument("task_filter", required=True)
@click.argument("task_args", nargs=-1, required=True, type=click.UNPROCESSED)
@click.pass_context
def mod(ctx: Any, task_filter: str, task_args: Tuple[str], parent: bool) -> None:
    """Change task attributes."""
    task_selector = _parse_task_selector([task_filter])
    changes = _parse_changes(task_args)
    try:
        services.modify_tasks(
            ctx.obj["repo"],
            task_selector,
            changes,
            parent,
        )
    except EntityNotFoundError as error:
        log.error(str(error))
        sys.exit(1)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.option("-p", "--parent", is_flag=True)
@click.argument("task_filter", nargs=-1, required=True, type=click.UNPROCESSED)
@click.pass_context
def freeze(ctx: Any, task_filter: Tuple[str], parent: bool) -> None:
    """Temporarily deactivate recurrent tasks."""
    task_selector = _parse_task_selector(task_filter)
    if not parent:
        task_selector.model = RecurrentTask

    try:
        services.freeze_tasks(
            ctx.obj["repo"],
            task_selector,
        )
    except (EntityNotFoundError, ValueError) as error:
        log.error(str(error))
        sys.exit(1)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.option("-s", "--state")
@click.argument("task_filter", nargs=-1, required=True, type=click.UNPROCESSED)
@click.pass_context
def thaw(ctx: Any, task_filter: Tuple[str], state: Optional[TaskState] = None) -> None:
    """Reactivate frozen tasks."""
    task_selector = _parse_task_selector(task_filter)

    try:
        services.thaw_tasks(
            ctx.obj["repo"],
            task_selector,
            state,
        )
    except (EntityNotFoundError, ValueError) as error:
        log.error(str(error))
        sys.exit(1)


# ---------------------------------------------------------------
#                   Reports
# ---------------------------------------------------------------


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("report_name")
@click.argument("task_filter", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def report(ctx: Any, report_name: str, task_filter: Tuple[str]) -> None:
    """Print any report."""
    try:
        views.print_task_report(
            ctx.obj["repo"],
            ctx.obj["config"],
            report_name,
            _parse_task_selector(task_filter),
        )
    except EntityNotFoundError as error:
        log.info(str(error))
        sys.exit(0)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("task_filter", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def open(ctx: Any, task_filter: Tuple[str]) -> None:
    """List the active tasks."""
    ctx.forward(report, report_name="open")


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("task_filter", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def closed(ctx: Any, task_filter: Tuple[str]) -> None:
    """List the closed tasks."""
    ctx.forward(report, report_name="closed")


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("task_filter", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def recurring(ctx: Any, task_filter: Tuple[str]) -> None:
    """List the recurring and repeating tasks."""
    ctx.forward(report, report_name="recurring")


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("task_filter", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def frozen(ctx: Any, task_filter: Tuple[str]) -> None:
    """List the frozen tasks."""
    ctx.forward(report, report_name="frozen")


@cli.command(context_settings={"ignore_unknown_options": True})
@click.pass_context
def areas(ctx: Any) -> None:
    """List the areas present in the active tasks."""
    try:
        views.areas(ctx.obj["repo"])
    except EntityNotFoundError:
        log.info("No areas found with any open tasks.")
        sys.exit(0)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.pass_context
def tags(ctx: Any) -> None:
    """List the tags present in the active tasks."""
    try:
        views.tags(ctx.obj["repo"])
    except EntityNotFoundError:
        log.info("No tags found with any open tasks.")
        sys.exit(0)


@cli.command(hidden=True)
def null() -> None:
    """Do nothing.

    Used for the tests until we have a better solution.
    """


if __name__ == "__main__":  # pragma: no cover
    # E1120: As the arguments are passed through the function decorators instead of
    # during the function call, pylint get's confused.
    cli(ctx={})  # noqa: E1120
