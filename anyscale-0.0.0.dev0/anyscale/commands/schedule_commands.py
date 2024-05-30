from typing import Optional

import click

from anyscale.controllers.schedule_controller import ScheduleController


@click.group("schedule", help="Create and manage Anyscale Schedules.")
def schedule_cli() -> None:
    pass


@schedule_cli.command(name="create")
@click.argument("schedule_config_file", required=True)
@click.option(
    "--name", "-n", required=False, default=None, help="Name of the schedule."
)
@click.option(
    "--description", required=False, default=None, help="Description of schedule."
)
def create(
    schedule_config_file: str, name: Optional[str], description: Optional[str],
) -> None:
    """ Create or Update a Schedule

    This function accepts 1 argument, a path to a YAML config file that defines this schedule.

    Note: if a schedule with the name exists in the specified project, it will be updated instead.
    """

    job_controller = ScheduleController()
    job_controller.apply(
        schedule_config_file, name, description,
    )


@schedule_cli.command(name="update")
@click.argument("schedule_config_file", required=True)
@click.option(
    "--name", "-n", required=False, default=None, help="Name of the schedule."
)
@click.option(
    "--description", required=False, default=None, help="Description of schedule."
)
def update(
    schedule_config_file: str, name: Optional[str], description: Optional[str],
) -> None:
    """ Create or Update a Schedule

    This function accepts 1 argument, a path to a YAML config file that defines this schedule.
    """

    job_controller = ScheduleController()
    job_controller.apply(
        schedule_config_file, name, description,
    )


@schedule_cli.command(name="list",)
@click.option(
    "--name", "-n", required=False, default=None, help="Filter by the name of the job"
)
@click.option("--id", "-i", required=False, default=None, help="Id of the schedule.")
def list(  # noqa: A001
    name: Optional[str] = None, id: Optional[str] = None  # noqa: A002
) -> None:
    """ List Schedules

    You can optionally filter schedules by rowname.
    """
    job_controller = ScheduleController()
    job_controller.list(name=name, id=id)


@schedule_cli.command(name="pause",)
@click.argument("schedule_config_file", required=False)
@click.option(
    "--name", "-n", required=False, default=None, help="Name of the schedule."
)
@click.option("--id", "-i", required=False, default=None, help="Id of the schedule.")
def pause(schedule_config_file: str, name: str, id: str) -> None:  # noqa: A002
    """ Pause a Schedule

    This function accepts 1 argument, a path to a YAML config file that defines this schedule.
    You can also specify the schedule by name or id.
    """

    job_controller = ScheduleController()
    id = job_controller.resolve_file_name_or_id(  # noqa: A001
        schedule_config_file=schedule_config_file, id=id, name=name
    )
    job_controller.pause(id, is_paused=True)


@schedule_cli.command(name="resume",)
@click.argument("schedule_config_file", required=False)
@click.option(
    "--name", "-n", required=False, default=None, help="Name of the schedule."
)
@click.option("--id", "-i", required=False, default=None, help="Id of the schedule.")
def unpause(schedule_config_file: str, name: str, id: str) -> None:  # noqa: A002
    """ Resume a Schedule

    This function accepts 1 argument, a path to a YAML config file that defines this schedule.
    You can also specify the schedule by name or id.
    """

    job_controller = ScheduleController()
    id = job_controller.resolve_file_name_or_id(  # noqa: A001
        schedule_config_file=schedule_config_file, id=id, name=name
    )
    job_controller.pause(id, is_paused=False)


@schedule_cli.command(name="run",)
@click.argument("schedule_config_file", required=False)
@click.option(
    "--name", "-n", required=False, default=None, help="Name of the schedule."
)
@click.option("--id", "-i", required=False, default=None, help="Id of the schedule.")
def trigger(schedule_config_file: str, id: str, name: str) -> None:  # noqa: A002
    """ Manually run a Schedule

    This function takes an existing schedule and runs it now.
    You can specify the schedule by name or id.
    You can also pass in a YAML file as a convinience. This is equivalent to passing in the name specified in the YAML file.
    IMPORTANT: if you pass in a YAML definition that differs from the Schedule defition, the Schedule will NOT be updated.
    Please use the `anyscale schedule update` command to update the configuration of your schedule
    or use the `anyscale job submit` command to submit a one off job that is not a part of a schedule.
    """

    job_controller = ScheduleController()
    id = job_controller.resolve_file_name_or_id(  # noqa: A001
        schedule_config_file=schedule_config_file, id=id, name=name
    )
    job_controller.trigger(id)


@schedule_cli.command(name="url",)
@click.argument("schedule_config_file", required=False)
@click.option(
    "--name", "-n", required=False, default=None, help="Name of the schedule."
)
@click.option("--id", "-i", required=False, default=None, help="Id of the schedule.")
def url(schedule_config_file: str, id: str, name: str) -> None:  # noqa: A002
    """ Get a Schedule URL

    This function accepts 1 argument, a path to a YAML config file that defines this schedule.
    You can also specify the schedule by name or id.
    """

    job_controller = ScheduleController()
    id = job_controller.resolve_file_name_or_id(  # noqa: A001
        schedule_config_file=schedule_config_file, id=id, name=name
    )
    job_controller.url(id)
