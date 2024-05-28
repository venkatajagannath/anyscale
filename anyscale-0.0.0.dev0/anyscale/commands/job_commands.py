from io import StringIO
from json import dumps as json_dumps
import pathlib
from subprocess import list2cmdline
from typing import Optional, Tuple

import click
import yaml

import anyscale
from anyscale.cli_logger import BlockLogger
from anyscale.commands.util import convert_kv_strings_to_dict
from anyscale.controllers.job_controller import JobController
from anyscale.job.models import JobConfig, JobState, JobStatus
from anyscale.util import validate_non_negative_arg


log = BlockLogger()  # CLI Logger


def _validate_job_name_and_id(name: Optional[str], job_id: Optional[str]):
    if name is None and job_id is None:
        raise click.ClickException("One of '--name' and '--job-id' must be provided.")

    if name is not None and job_id is not None:
        raise click.ClickException(
            "Only one of '--name' and '--job-id' can be provided."
        )


@click.group("job", help="Interact with production jobs running on Anyscale.")
def job_cli() -> None:
    pass


@job_cli.command(
    name="submit", short_help="Submit a job.",
)
@click.option("-n", "--name", required=False, default=None, help="Name of the job.")
@click.option(
    "-f",
    "--follow",
    required=False,
    hidden=True,
    default=False,
    type=bool,
    is_flag=True,
    help="DEPRECATED: use `--wait` instead.",
)
@click.option(
    "-w",
    "--wait",
    required=False,
    default=False,
    type=bool,
    is_flag=True,
    help="Block this CLI command and print logs until the job finishes.",
)
@click.option(
    "--config-file",
    required=False,
    default=None,
    type=str,
    help="Path to a YAML config file to use for this job. Command-line flags will overwrite values read from the file.",
)
@click.option(
    "--compute-config",
    required=False,
    default=None,
    type=str,
    help="Named compute configuration to use for the job. This defaults to the compute configuration of the workspace.",
)
@click.option(
    "--image-uri",
    required=False,
    default=None,
    type=str,
    help="Container image to use for this job. When running in a workspace, this defaults to the image of the workspace.",
)
@click.option(
    "--containerfile",
    required=False,
    default=None,
    type=str,
    help="Path to a containerfile to build the image to use for the job.",
)
@click.option(
    "--env",
    required=False,
    multiple=True,
    type=str,
    help="Environment variables to set for the job. The format is 'key=value'. This argument can be specified multiple times. When the same key is also specified in the config file, the value from the command-line flag will overwrite the value from the config file.",
)
@click.option(
    "--working-dir",
    required=False,
    default=None,
    type=str,
    help="Path to a local directory that will be the working directory for the job. The files in the directory will be automatically uploaded to cloud storage. When running in a workspace, this defaults to the current working directory.",
)
@click.option(
    "-e",
    "--exclude",
    required=False,
    type=str,
    multiple=True,
    help="File pattern to exclude when uploading local directories. This argument can be specified multiple times and the patterns will be appended to the 'excludes' list in the config file (if any).",
)
@click.option(
    "-r",
    "--requirements",
    required=False,
    default=None,
    type=str,
    help="Path to a requirements.txt file containing dependencies for the job. These will be installed on top of the image. When running in a workspace, this defaults to the workspace dependencies.",
)
@click.option(
    "--py-module",
    required=False,
    default=None,
    multiple=True,
    type=str,
    help="Python modules to be available for import in the Ray workers. Each entry must be a path to a local directory.",
)
@click.argument("entrypoint", required=False, nargs=-1, type=click.UNPROCESSED)
def submit(  # noqa: PLR0912 PLR0913 C901
    entrypoint: Tuple[str],
    name: Optional[str],
    follow: Optional[bool],
    wait: Optional[bool],
    config_file: Optional[str],
    compute_config: Optional[str],
    image_uri: Optional[str],
    containerfile: Optional[str],
    env: Tuple[str],
    working_dir: Optional[str],
    exclude: Tuple[str],
    requirements: Optional[str],
    py_module: Tuple[str],
):
    """Submit a job.

    The job config can be specified in one of the following ways:

    * Job config file can be specified as a single positional argument. E.g. `anyscale job submit config.yaml`.

    * Job config can also be specified with command-line arguments. In this case, the entrypoint should be specified
as the positional arguments starting with `--`. Other arguments can be specified with command-line flags. E.g.

      * `anyscale job submit -- python main.py`: submit a job with the entrypoint `python main.py`.

      * `anyscale job submit --name my-job -- python main.py`: submit a job with the name `my-job` and the
entrypoint `python main.py`.

    * [Experimental] If you want to specify a config file and override some arguments with the commmand-line flags,
use the `--config-file` flag. E.g.

      * `anyscale job submit --config-file config.yaml`: submit a job with the config in `config.yaml`.

      * `anyscale job submit --config-file config.yaml -- python main.py`: submit a job with the config in `config.yaml`
and override the entrypoint with `python main.py`.

    Either containerfile or image-uri should be used, specifying both will result in an error.

    By default, this command submits the job asynchronously and exits. To wait for the job to complete, use the `--wait` flag.
    """

    job_controller = JobController()
    if len(entrypoint) == 1 and (
        pathlib.Path(entrypoint[0]).is_file() or entrypoint[0].endswith(".yaml")
    ):
        # If entrypoint is a single string that ends with .yaml, e.g. `anyscale job submit config.yaml`,
        # treat it as a config file, and use the old job submission API.
        if config_file is not None:
            raise click.ClickException(
                "`--config-file` should not be used when providing a config file as the entrypoint."
            )
        if image_uri:
            raise click.ClickException(
                "`--image-uri` should not be used when providing a config file as the entrypoint."
            )
        if containerfile:
            raise click.ClickException(
                "`--containerfile` should not be used when providing a config file as the entrypoint."
            )
        if env:
            raise click.ClickException(
                "`--env` should not be used when providing a config file as the entrypoint."
            )

        config_file = entrypoint[0]
        if not pathlib.Path(config_file).is_file():
            raise click.ClickException(f"Job config file '{config_file}' not found.")
        log.info(f"Submitting job from config file {config_file}.")

        job_id = job_controller.submit(config_file, name=name)
    else:
        # Otherwise, use the new job submission API. E.g.
        # `anyscale job submit -- python main.py`,
        # or `anyscale job submit --config-file config.yaml`.
        if len(entrypoint) == 0 and config_file is None:
            raise click.ClickException(
                "Either a config file or an inlined entrypoint must be provided."
            )
        if config_file is not None and not pathlib.Path(config_file).is_file():
            raise click.ClickException(f"Job config file '{config_file}' not found.")

        if follow:
            raise click.ClickException(
                "`--follow` is deprecated, use `--wait` instead."
            )

        args = {}
        if len(entrypoint) > 0:
            args["entrypoint"] = list2cmdline(entrypoint)
        if name:
            args["name"] = name

        if containerfile and image_uri:
            raise click.ClickException(
                "Only one of '--containerfile' and '--image-uri' can be provided."
            )

        if image_uri:
            args["image_uri"] = image_uri

        if containerfile:
            args["containerfile"] = containerfile

        if working_dir:
            args["working_dir"] = working_dir

        if config_file is not None:
            config = JobConfig.from_yaml(config_file, **args)
        else:
            config = JobConfig.from_dict(args)

        if compute_config is not None:
            config = config.options(compute_config=compute_config)

        if exclude:
            config = config.options(excludes=[e for e in exclude])

        if requirements is not None:
            if not pathlib.Path(requirements).is_file():
                raise click.ClickException(
                    f"Requirements file '{requirements}' not found."
                )
            config = config.options(requirements=requirements)

        if env:
            env_dict = convert_kv_strings_to_dict(env)
            if env_dict:
                config = config.options(env_vars=env_dict)
        if py_module:
            for module in py_module:
                if not pathlib.Path(module).is_dir():
                    raise click.ClickException(
                        f"Python module path '{module}' does not exist or is not a directory."
                    )
            config = config.options(py_modules=[*py_module])
        log.info(f"Submitting job with config {config}.")
        job_id = anyscale.job.submit(config)

    if wait:
        log.info(
            "Waiting for the job to run. Interrupting this command will not cancel the job."
        )
    else:
        log.info("Use `--wait` to wait for the job to run and stream logs.")

    if wait:
        anyscale.job.wait(job_id=job_id)


@job_cli.command(name="list", help="Display information about existing jobs.")
@click.option("--name", "-n", required=False, default=None, help="Filter by job name.")
@click.option(
    "--job-id", "--id", required=False, default=None, help="Filter by job id."
)
@click.option(
    "--project-id", required=False, default=None, help="Filter by project id."
)
@click.option(
    "--include-all-users",
    is_flag=True,
    default=False,
    help="Include jobs not created by current user.",
)
@click.option(
    "--include-archived",
    is_flag=True,
    default=False,
    help=(
        "List archived jobs as well as unarchived jobs."
        "If not provided, defaults to listing only unarchived jobs."
    ),
)
@click.option(
    "--max-items",
    required=False,
    default=10,
    type=int,
    help="Max items to show in list.",
    callback=validate_non_negative_arg,
)
def list(  # noqa: A001
    name: Optional[str],
    job_id: Optional[str],
    project_id: Optional[str],
    include_all_users: bool,
    include_archived: bool,
    max_items: int,
) -> None:
    job_controller = JobController()
    job_controller.list(
        name=name,
        job_id=job_id,
        project_id=project_id,
        include_all_users=include_all_users,
        include_archived=include_archived,
        max_items=max_items,
    )


@job_cli.command(name="archive", short_help="Archive a job.")
@click.option("--job-id", "--id", required=False, help="Unique ID of the job.")
@click.option("--name", "-n", required=False, help="Name of the job.")
def archive(job_id: Optional[str], name: Optional[str]) -> None:
    """Archive a job.

    To specify the job by name, use the --name flag. To specify the job by id, use the --job-id flag. Either name or
id should be used, specifying both will result in an error.

    If job is specified by name and there are multiple jobs with the specified name, the most recently created job
status will be archived.
    """
    _validate_job_name_and_id(name=name, job_id=job_id)
    anyscale.job.archive(job_id=job_id, name=name)


@job_cli.command(name="terminate", short_help="Terminate a job.")
@click.option("--job-id", "--id", required=False, help="Unique ID of the job.")
@click.option("--name", "-n", required=False, help="Name of the job.")
def terminate(job_id: Optional[str], name: Optional[str]) -> None:
    """Terminate a job.

    To specify the job by name, use the --name flag. To specify the job by id, use the --job-id flag. Either name or
id should be used, specifying both will result in an error.

    If job is specified by name and there are multiple jobs with the specified name, the most recently created job
status will be terminated.
    """
    _validate_job_name_and_id(name=name, job_id=job_id)
    anyscale.job.terminate(name=name, job_id=job_id)
    if job_id is not None:
        log.info(
            f"Query the status of the job with `anyscale job status --id {job_id}`."
        )
    else:
        log.info(
            f"Query the status of the job with `anyscale job status --name {name}`."
        )


@job_cli.command(name="logs")
@click.option("--job-id", "--id", required=False, help="Unique ID of the job.")
@click.option("--name", "-n", required=False, help="Name of the job.")
@click.option(
    "--run",
    required=False,
    help="Name of the job run to query logs for, by default the latest job run will be used.",
)
@click.option(
    "--follow",
    "-f",
    required=False,
    default=False,
    type=bool,
    is_flag=True,
    help="Whether to follow the log.",
)
@click.option(
    "--all-attempts",
    is_flag=True,
    default=False,
    help="DEPRECATED. Querying all attempts is no longer supported.",
)
def logs(
    job_id: Optional[str],
    name: Optional[str],
    run: Optional[str],
    follow: bool = False,
    all_attempts: bool = False,
) -> None:
    """Print the logs of a job.

    By default from the latest job attempt.

    Example usage:

        anyscale job logs --id prodjob_123

        anyscale job logs --name my-job

        anyscale job logs --id prodjob_123 -f"""
    # TODO(mowen): Do we need to leave this stub or should we just delete?
    if all_attempts:
        raise click.ClickException(
            "`--all-attempts` is deprecated, query individual logs directly with `--run` instead."
        )
    _validate_job_name_and_id(name=name, job_id=job_id)
    print(anyscale.job.logs(job_id=job_id, name=name, run=run, follow=follow))


@job_cli.command(name="wait", short_help="Wait for a job to enter a specific state.")
@click.option("--job-id", "--id", required=False, help="Unique ID of the job.")
@click.option("--name", "-n", required=False, help="Name of the job.")
@click.option(
    "--state",
    "-s",
    required=False,
    default=JobState.SUCCEEDED,
    help="The state to wait for this job to enter",
)
@click.option(
    "--timeout-s",
    "--timeout",
    "-t",
    required=False,
    default=1800,
    type=float,
    help="The timeout in seconds after which this command will exit.",
)
def wait(
    job_id: Optional[str],
    name: Optional[str],
    state: str = JobState.SUCCEEDED,
    timeout_s=None,
) -> None:
    """Wait for a job to enter a specific state (default: SUCCEEDED).

    To specify the job by name, use the --name flag. To specify the job by id, use the --job-id flag.

    If the job reaches the target state, the command will exit successfully.

    If the job reaches a terminal state other than the target state, the command will exit with an error.

    If the command reaches the timeout, the command will exit with an error but job execution will continue.
    """
    _validate_job_name_and_id(name=name, job_id=job_id)
    try:
        state = JobState.validate(state)
    except ValueError as e:
        raise click.ClickException(str(e))
    anyscale.job.wait(name=name, job_id=job_id, state=state, timeout_s=timeout_s)


@job_cli.command(
    name="status", short_help="Get the status of a job.",
)
@click.option(
    "--job-id", "--id", required=False, default=None, help="Unique ID of the job."
)
@click.option("--name", "-n", required=False, default=None, help="Name of the job.")
@click.option(
    "--json",
    "-j",
    is_flag=True,
    default=False,
    help="Output the status in a structured JSON format.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Include verbose details in the status.",
)
def status(name: Optional[str], job_id: Optional[str], json: bool, verbose: bool):
    """Query the status of a job.

    To specify the job by name, use the --name flag. To specify the job by id, use the --job-id flag. Either name or
id should be used, specifying both will result in an error.

    If job is specified by name and there are multiple jobs with the specified name, the most recently created job
status will be returned.
    """
    _validate_job_name_and_id(name=name, job_id=job_id)

    status: JobStatus = anyscale.job.status(name=name, job_id=job_id)
    status_dict = status.to_dict()

    if not verbose:
        status_dict.pop("config", None)

    if json:
        print(json_dumps(status_dict, indent=4, sort_keys=False))
    else:
        stream = StringIO()
        yaml.dump(status_dict, stream, sort_keys=False)
        print(stream.getvalue(), end="")
