from io import StringIO
from json import dumps as json_dumps
import pathlib
from typing import Any, Dict, Optional, Tuple

import click
from typing_extensions import Literal
import yaml

from anyscale.cli_logger import BlockLogger
from anyscale.commands.util import convert_kv_strings_to_dict
from anyscale.controllers.service_controller import ServiceController
import anyscale.service
from anyscale.service import ServiceConfig, ServiceState, ServiceStatus
from anyscale.util import validate_non_negative_arg


log = BlockLogger()  # CLI Logger


@click.group("service")
def service_cli():
    pass


def _read_name_from_config_file(path: str):
    """Read the 'name' property from the config file at `path`.

    This enables reading the name for both the existing (rollout) and new (deploy)
    config file formats.
    """
    if not pathlib.Path(path).is_file():
        raise click.ClickException(f"Config file not found at path: '{path}'.")

    with open(path) as f:
        config = yaml.safe_load(f)

    if config is None or "name" not in config:
        raise click.ClickException(f"No 'name' property found in config file '{path}'.")

    return config["name"]


@service_cli.command(
    name="deploy", short_help="Deploy or update a service.", hidden=True,
)
@click.argument("import_path", type=str, required=False, default=None)
@click.argument("arguments", nargs=-1, required=False)
@click.option(
    "-f",
    "--config-file",
    required=False,
    default=None,
    type=str,
    help="Path to a YAML config file to deploy. When deploying from a file, import path and arguments cannot be provided. Command-line flags will overwrite values read from the file.",
)
@click.option(
    "-n",
    "--name",
    required=False,
    default=None,
    type=str,
    help="Unique name for the service. When running in a workspace, this defaults to the workspace name.",
)
@click.option(
    "--image-uri",
    required=False,
    default=None,
    type=str,
    help="Container image to use for the service. This cannot be changed when using --in-place and is exclusive with --containerfile. When running in a workspace, this defaults to the image of the workspace.",
)
@click.option(
    "--containerfile",
    required=False,
    default=None,
    type=str,
    help="Path to a containerfile to build the image to use for the service. This cannot be changed when using --in-place and is exclusive with --image-uri.",
)
@click.option(
    "--compute-config",
    required=False,
    default=None,
    type=str,
    help="Named compute configuration to use for the service. This cannot be changed when using --in-place. When running in a workspace, this defaults to the compute configuration of the workspace.",
)
@click.option(
    "-w",
    "--working-dir",
    required=False,
    default=None,
    type=str,
    help="Path to a local directory that will be the working directory for the service. The files in the directory will be automatically uploaded to cloud storage. When running in a workspace, this defaults to the current working directory.",
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
    help="Path to a requirements.txt file containing dependencies for the service. These will be installed on top of the image. When running in a workspace, this defaults to the workspace dependencies.",
)
@click.option(
    "-i",
    "--in-place",
    is_flag=True,
    show_default=True,
    default=False,
    help="Perform an in-place upgrade without starting a new cluster. This can be used for faster iteration during development but is *not* currently recommended for production deploys. This *cannot* be used to change cluster-level options such as image and compute config (they will be ignored).",
)
@click.option(
    "--canary-percent",
    required=False,
    default=None,
    type=int,
    help="The percentage of traffic to send to the canary version of the service (0-100). This can be used to manually shift traffic toward (or away from) the canary version. If not provided, traffic will be shifted incrementally toward the canary version until it reaches 100. Not supported when using --in-place.",
)
@click.option(
    "--max-surge-percent",
    required=False,
    default=None,
    type=int,
    help="Amount of excess capacity allowed to be used while updating the service (0-100). Defaults to 100. Not supported when using --in-place.",
)
@click.option(
    "--env",
    required=False,
    multiple=True,
    type=str,
    help="Environment variables to set for the service. The format is 'key=value'. This argument can be specified multiple times. When the same key is also specified in the config file, the value from the command-line flag will overwrite the value from the config file.",
)
@click.option(
    "--py-module",
    required=False,
    default=None,
    multiple=True,
    type=str,
    help="Python modules to be available for import in the Ray workers. Each entry must be a path to a local directory.",
)
def deploy(  # noqa: PLR0912, PLR0913 C901
    config_file: Optional[str],
    import_path: Optional[str],
    arguments: Tuple[str],
    name: Optional[str],
    image_uri: Optional[str],
    containerfile: Optional[str],
    compute_config: Optional[str],
    working_dir: Optional[str],
    exclude: Tuple[str],
    requirements: Optional[str],
    in_place: bool,
    canary_percent: Optional[int],
    max_surge_percent: Optional[int],
    env: Optional[Tuple[str]],
    py_module: Tuple[str],
):
    """Deploy or update a service.

    If no service with the provided name is running, one will be created, else the existing service will be updated.

    To deploy a single application, the import path and optional arguments can be passed directly as arguments:

    `$ anyscale service deploy main:app arg1=val1`

    To deploy multiple applications, deploy from a config file using `-f`:

    `$ anyscale service deploy -f config.yaml`

    Command-line flags override values in the config file.
    """

    if config_file is not None:
        if import_path is not None or len(arguments) > 0:
            raise click.ClickException(
                "When a config file is provided, import path and application arguments can't be."
            )

        if not pathlib.Path(config_file).is_file():
            raise click.ClickException(f"Config file '{config_file}' not found.")

        config = ServiceConfig.from_yaml(config_file)
    else:
        if import_path is None:
            raise click.ClickException(
                "Either config file or import path must be provided."
            )

        if (
            import_path.endswith((".yaml", ".yml"))
            or pathlib.Path(import_path).is_file()
        ):
            log.warning(
                f"The provided import path '{import_path}' looks like a config file. Did you mean to use '-f config.yaml'?"
            )

        app: Dict[str, Any] = {"import_path": import_path}
        arguments_dict = convert_kv_strings_to_dict(arguments)
        if arguments_dict:
            app["args"] = arguments_dict

        config = ServiceConfig(applications=[app])

    if containerfile and image_uri:
        raise click.ClickException(
            "Only one of '--containerfile' and '--image-uri' can be provided."
        )

    if name is not None:
        config = config.options(name=name)

    if image_uri is not None:
        config = config.options(image_uri=image_uri)

    if containerfile is not None:
        config = config.options(containerfile=containerfile)

    if compute_config is not None:
        config = config.options(compute_config=compute_config)

    if working_dir is not None:
        config = config.options(working_dir=working_dir)

    if exclude:
        config = config.options(excludes=[e for e in exclude])

    if requirements is not None:
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

    anyscale.service.deploy(
        config,
        in_place=in_place,
        canary_percent=canary_percent,
        max_surge_percent=max_surge_percent,
    )


@service_cli.command(
    name="status", help="Get the status of a service.", hidden=True,
)
@click.option(
    "-n", "--name", required=False, default=None, type=str, help="Name of the service.",
)
@click.option(
    "-f",
    "--config-file",
    required=False,
    default=None,
    type=str,
    help="Path to a YAML config file to read the name from.",
)
@click.option(
    "-j",
    "--json",
    is_flag=True,
    default=False,
    help="Output the status in a structured JSON format.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Include verbose details in the status.",
)
def status(name: Optional[str], config_file: Optional[str], json: bool, verbose: bool):
    if name is not None and config_file is not None:
        raise click.ClickException(
            "Only one of '--name' and '--config-file' can be provided."
        )

    if config_file is not None:
        name = _read_name_from_config_file(config_file)

    if name is None:
        raise click.ClickException(
            "Service name must be provided using '--name' or in a config file using '-f'."
        )

    status: ServiceStatus = anyscale.service.status(name=name)
    status_dict = status.to_dict()
    if not verbose:
        # TODO(edoakes): consider adding this as an API on the model itself if it
        # becomes a common pattern.
        status_dict.get("primary_version", {}).pop("config", None)
        status_dict.get("canary_version", {}).pop("config", None)

    if json:
        print(json_dumps(status_dict, indent=4, sort_keys=False))
    else:
        stream = StringIO()
        yaml.dump(status_dict, stream, sort_keys=False)
        print(stream.getvalue(), end="")


@service_cli.command(
    name="wait", help="Wait for a service to enter a target state.", hidden=True,
)
@click.option(
    "-n", "--name", required=False, default=None, type=str, help="Name of the service.",
)
@click.option(
    "-f",
    "--config-file",
    required=False,
    default=None,
    type=str,
    help="Path to a YAML config file to read the name from.",
)
@click.option(
    "-s",
    "--state",
    default=str(ServiceState.RUNNING),
    help="The ServiceState to wait for the service to reach. Defaults to RUNNING.",
)
@click.option(
    "-t",
    "--timeout-s",
    default=600,
    type=float,
    help="Timeout to wait for the service to reach the target state. Defaults to 600s (10min).",
)
def wait(name: Optional[str], config_file: Optional[str], state: str, timeout_s: int):
    try:
        state = ServiceState.validate(state)
    except ValueError as e:
        raise click.ClickException(str(e))

    if name is not None and config_file is not None:
        raise click.ClickException(
            "Only one of '--name' and '--config-file' can be provided."
        )

    if config_file is not None:
        name = _read_name_from_config_file(config_file)

    if name is None:
        raise click.ClickException(
            "Service name must be provided using '--name' or in a config file using '-f'."
        )

    anyscale.service.wait(name=name, state=state, timeout_s=timeout_s)


@service_cli.command(
    name="rollout", help="Roll out a service.",
)
@click.option(
    "-f",
    "--config-file",
    "--service-config-file",
    required=True,
    help="The path of the service configuration file.",
)
@click.option("--name", "-n", required=False, default=None, help="Name of service.")
@click.option("--version", required=False, default=None, help="Version of service.")
@click.option(
    "--max-surge-percent",
    required=False,
    default=None,
    type=int,
    help="Max amount of excess capacity allocated during the rollout (0-100).",
)
@click.option(
    "--canary-percent",
    required=False,
    default=None,
    type=int,
    help="The percentage of traffic to send to the canary version of the service.",
)
@click.option(
    "--rollout-strategy",
    required=False,
    default=None,
    type=click.Choice(["ROLLOUT", "IN_PLACE"], case_sensitive=False),
    help="Strategy for rollout.",
)
@click.option(
    "-i",
    "--in-place",
    "in_place",
    is_flag=True,
    show_default=True,
    default=False,
    help="Alias for `--rollout-strategy=IN_PLACE`.",
)
@click.option(
    "--no-auto-complete-rollout",
    is_flag=True,
    show_default=True,
    default=False,
    help="Do not complete the rollout (terminate the existing version cluster) after the canary version reaches 100%",
)
def rollout(  # noqa: PLR0913
    config_file: str,
    name: Optional[str],
    version: Optional[str],
    max_surge_percent: Optional[int],
    canary_percent: Optional[int],
    rollout_strategy: Optional[Literal["ROLLOUT", "IN_PLACE"]],
    in_place: bool,
    no_auto_complete_rollout: bool,
):
    """Start or update a service rollout to a new version."""
    if in_place:
        if rollout_strategy is not None:
            raise click.ClickException(
                "Only one of `--in-place/-i` and `--rollout-strategy` can be provided."
            )
        rollout_strategy = "IN_PLACE"

    service_controller = ServiceController()
    service_config = service_controller.read_service_config_file(config_file)
    service_controller.rollout(
        service_config,
        name=name,
        version=version,
        max_surge_percent=max_surge_percent,
        canary_percent=canary_percent,
        rollout_strategy=rollout_strategy,
        auto_complete_rollout=not no_auto_complete_rollout,
    )


@service_cli.command(name="list", help="Display information about services.")
@click.option(
    "--name", "-n", required=False, default=None, help="Filter by service name."
)
@click.option(
    "--service-id", "--id", required=False, default=None, help="Filter by service id."
)
@click.option(
    "--project-id", required=False, default=None, help="Filter by project id."
)
@click.option(
    "--created-by-me",
    help="List services created by me only.",
    is_flag=True,
    default=False,
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
    service_id: Optional[str],
    project_id: Optional[str],
    created_by_me: bool,
    max_items: int,
):
    """List services based on the provided filters.

    This returns both v1 and v2 services.
    """
    service_controller = ServiceController()
    service_controller.list(
        name=name,
        service_id=service_id,
        project_id=project_id,
        created_by_me=created_by_me,
        max_items=max_items,
    )


@service_cli.command(name="rollback", help="Roll back a service.")
@click.option(
    "--service-id", "--id", default=None, help="ID of service.",
)
@click.option("-n", "--name", required=False, default=None, help="Name of service.")
@click.option("--project-id", required=False, help="Filter by project id.")
@click.option(
    "-f",
    "--config-file",
    "--service-config-file",
    help="Path to a YAML config file to read the name from. `--service-config-file` is deprecated, use `-f` or `--config-file`.",
)
@click.option(
    "--max-surge-percent",
    required=False,
    default=None,
    type=int,
    help="Max amount of excess capacity allocated during the rollback (0-100).",
)
def rollback(
    service_id: Optional[str],
    name: Optional[str],
    project_id: Optional[str],
    config_file: Optional[str],
    max_surge_percent: Optional[int],
):
    """Perform a rollback for a service that is currently in a rollout."""
    service_controller = ServiceController()
    service_id = service_controller.get_service_id(
        service_id=service_id,
        service_name=name,
        service_config_file=config_file,
        project_id=project_id,
    )
    service_controller.rollback(service_id, max_surge_percent)


@service_cli.command(name="terminate", help="Terminate a service.")
@click.option(
    "--service-id", "--id", required=False, help="ID of service.",
)
@click.option("-n", "--name", required=False, help="Name of service.")
@click.option("--project-id", required=False, help="Filter by project id.")
@click.option(
    "-f",
    "--config-file",
    "--service-config-file",
    help="Path to a YAML config file to read the name from. `--service-config-file` is deprecated, use `-f` or `--config-file`.",
)
def terminate(
    service_id: Optional[str],
    name: Optional[str],
    project_id: Optional[str],
    config_file: Optional[str],
):
    """Terminate a service.

    This applies to both v1 and v2 services.
    """
    service_controller = ServiceController()
    service_id = service_controller.get_service_id(
        service_id=service_id,
        service_name=name,
        service_config_file=config_file,
        project_id=project_id,
    )
    service_controller.terminate(service_id)
