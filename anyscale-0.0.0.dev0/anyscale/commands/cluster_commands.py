import os
from typing import Optional

import click

from anyscale.controllers.cluster_controller import ClusterController
from anyscale.util import validate_non_negative_arg


HIDE_BYOD_FLAGS = os.getenv("ANYSCALE_BYOD") != "1"


@click.group("cluster", help="Interact with clusters on Anyscale.")
def cluster_cli() -> None:
    pass


@cluster_cli.command(
    name="start", help="Start or update and restart a cluster on Anyscale."
)
@click.option(
    "--name",
    "-n",
    required=False,
    default=None,
    help="Name of new or existing cluster to start or update.",
)
@click.option(
    "--env",
    required=False,
    default=None,
    help=(
        "Set the Anyscale app config to use for the cluster. This is a cluster "
        "environment name optionally followed by a colon and a build version number. "
        "Eg: my_cluster_env:1"
    ),
)
@click.option(
    "--docker",
    required=False,
    default=None,
    help=("Custom docker image name."),
    hidden=HIDE_BYOD_FLAGS,
)
@click.option(
    "--python-version",
    required=False,
    default=None,
    help=("Python version for the custom docker image."),
    hidden=HIDE_BYOD_FLAGS,
)
@click.option(
    "--ray-version",
    required=False,
    default=None,
    help=("Ray version for the custom docker image."),
    hidden=HIDE_BYOD_FLAGS,
)
@click.option(
    "--compute",
    required=False,
    default=None,
    help=(
        "Name of compute config that is already registered with Anyscale. To use specific version, use the format `compute_name:version`."
    ),
)
@click.option(
    "--compute-file",
    required=False,
    default=None,
    help=(
        "The YAML file of the compute config to launch this cluster with. "
        "An example can be found at {website}. ".format(
            website="https://docs.anyscale.com/configure/compute-configs/overview",
        )
    ),
)
@click.option(
    "--cluster-id",
    "--id",
    required=False,
    default=None,
    help=(
        "Id of existing cluster to restart. This argument can be used "
        "to interact with any cluster you have access to in any project."
    ),
)
@click.option(
    "--project-id",
    required=False,
    default=None,
    help=(
        "Override project id used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
@click.option(
    "--project",
    required=False,
    default=None,
    help=(
        "Override project name used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
@click.option(
    "--cloud-name",
    required=False,
    default=None,
    help=(
        "Name of cloud to create a default compute config with. If a default "
        "cloud needs to be used and this is not provided, the organization default "
        "cloud will be used."
    ),
)
@click.option(
    "--idle-timeout",
    required=False,
    default=None,
    help="DEPRECATED: Please specify the idle_termination_minutes field in the compute config. "
    "Idle timeout (in minutes), after which the cluster is stopped. Idle "
    "time is defined as the time during which a cluster is not running a user "
    "command and does not have an attached driver. Time spent running Jupyter "
    "commands, or commands run through ssh, is still considered "
    "'idle'. -1 means no timeout. Default: 120 minutes",
    type=int,
)
@click.option(
    "--user-service-access",
    required=False,
    default=None,
    type=click.Choice(["private", "public"]),
    help=(
        "Whether user service (eg: serve deployment) can be accessed by public "
        "internet traffic. If public, a user service endpoint can be queried from "
        "the public internet with the provided authentication token. "
        "If private, the user service endpoint can only be queried from within "
        "the same Anyscale cloud and will not require an authentication token."
    ),
)
def start(  # noqa: PLR0913
    name: Optional[str],
    env: Optional[str],
    docker: Optional[str],
    python_version: Optional[str],
    ray_version: Optional[str],
    compute: Optional[str],
    compute_file: Optional[str],
    cluster_id: Optional[str],
    project_id: Optional[str],
    project: Optional[str],
    cloud_name: Optional[str],
    idle_timeout: Optional[int],
    user_service_access: Optional[str],
) -> None:
    cluster_controller = ClusterController()
    if HIDE_BYOD_FLAGS:
        assert docker is None, "The --docker flag is not enabled for your organization"
        assert (
            python_version is None
        ), "The --python-version flag is not enabled for your organization"
        assert (
            ray_version is None
        ), "The --ray-version flag is not enabled for your organization"

    cluster_controller.start(
        cluster_name=name,
        cluster_id=cluster_id,
        cluster_env_name=env,
        docker=docker,
        python_version=python_version,
        ray_version=ray_version,
        cluster_compute_name=compute,
        cluster_compute_file=compute_file,
        cloud_name=cloud_name,
        idle_timeout=idle_timeout,
        project_id=project_id,
        project_name=project,
        user_service_access=user_service_access,
    )


@cluster_cli.command(name="terminate", help="Terminate a cluster on Anyscale.")
@click.option(
    "--name",
    "-n",
    required=False,
    default=None,
    help="Name of existing cluster to terminate.",
)
@click.option(
    "--cluster-id",
    "--id",
    required=False,
    default=None,
    help=(
        "Id of existing cluster to termiante. This argument can be used "
        "to interact with any cluster you have access to in any project."
    ),
)
@click.option(
    "--project-id",
    required=False,
    default=None,
    help=(
        "Override project id used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
@click.option(
    "--project",
    required=False,
    default=None,
    help=(
        "Override project name used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
@click.option(
    "--cloud-id",
    required=False,
    default=None,
    help=(
        "Use cloud ID to disambiguate only when selecting a cluster to terminate with `--name`"
        "that doesn't belong to any project. This requires cloud isolation to be enabled."
    ),
    hidden=True,
)
@click.option(
    "--cloud",
    required=False,
    default=None,
    help=(
        "Use cloud to disambiguate only when selecting a cluster to terminate with `--name`"
        "that doesn't belong to any project. This requires cloud isolation to be enabled."
    ),
    hidden=True,
)
def terminate(
    name: Optional[str],
    cluster_id: Optional[str],
    project_id: Optional[str],
    project: Optional[str],
    cloud_id: Optional[str],
    cloud: Optional[str],
) -> None:
    cluster_controller = ClusterController()
    cluster_controller.terminate(
        cluster_name=name,
        cluster_id=cluster_id,
        project_id=project_id,
        project_name=project,
        cloud_id=cloud_id,
        cloud_name=cloud,
    )


@cluster_cli.command(name="archive", help="Archive a cluster on Anyscale.")
@click.option(
    "--name",
    "-n",
    required=False,
    default=None,
    help="Name of existing cluster to archive.",
)
@click.option(
    "--cluster-id",
    "--id",
    required=False,
    default=None,
    help=(
        "Id of existing cluster to archive. This argument "
        "can be used to archive any cluster you have access to in any project."
    ),
)
@click.option(
    "--project-id",
    required=False,
    default=None,
    help=(
        "Override project id used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
@click.option(
    "--project",
    required=False,
    default=None,
    help=(
        "Override project name used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
@click.option(
    "--cloud-id",
    required=False,
    default=None,
    help=(
        "Use cloud ID to disambiguate only when selecting a cluster to archive with `--name`"
        "that doesn't belong to any project. This requires cloud isolation to be enabled."
    ),
    hidden=True,
)
@click.option(
    "--cloud",
    required=False,
    default=None,
    help=(
        "Use cloud to disambiguate only when selecting a cluster to archive with `--name`"
        "that doesn't belong to any project. This requires cloud isolation to be enabled."
    ),
    hidden=True,
)
def archive(
    name: Optional[str],
    cluster_id: Optional[str],
    project_id: Optional[str],
    project: Optional[str],
    cloud_id: Optional[str],
    cloud: Optional[str],
) -> None:
    cluster_controller = ClusterController()
    cluster_controller.archive(
        cluster_name=name,
        cluster_id=cluster_id,
        project_id=project_id,
        project_name=project,
        cloud_id=cloud_id,
        cloud_name=cloud,
    )


@cluster_cli.command(
    name="list",
    help=(
        "List information about clusters on Anyscale. By default only list "
        "active clusters in current project."
    ),
)
@click.option(
    "--name",
    "-n",
    required=False,
    default=None,
    help="Name of existing cluster to get information about.",
)
@click.option(
    "--cluster-id",
    "--id",
    required=False,
    default=None,
    help=(
        "Id of existing cluster get information about. This argument can be used "
        "to interact with any cluster you have access to in any project."
    ),
)
@click.option(
    "--project-id",
    required=False,
    default=None,
    help=(
        "Override project id used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
@click.option(
    "--project",
    required=False,
    default=None,
    help=(
        "Override project name used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
@click.option(
    "--include-all-projects",
    is_flag=True,
    default=False,
    help="List all active clusters user has access to in any project.",
)
@click.option(
    "--include-inactive",
    is_flag=True,
    default=False,
    help="List clusters of all states.",
)
@click.option(
    "--include-archived",
    is_flag=True,
    default=False,
    help=(
        "List archived clusters as well as unarchived clusters."
        "If not provided, defaults to listing only unarchived clusters."
    ),
)
@click.option(
    "--max-items",
    required=False,
    default=20,
    type=int,
    help="Max items to show in list.",
    callback=validate_non_negative_arg,
)
@click.option(
    "--cloud-id",
    required=False,
    default=None,
    help=(
        "Use cloud ID to disambiguate only when selecting a cluster to list with `--name`"
        "that doesn't belong to any project. This requires cloud isolation to be enabled."
        "Note: This command doesn't support filtering clusters by cloud."
    ),
    hidden=True,
)
@click.option(
    "--cloud",
    required=False,
    default=None,
    help=(
        "Use cloud to disambiguate only when selecting a cluster to list with `--name`"
        "that doesn't belong to any project. This requires cloud isolation to be enabled."
        "Note: This command doesn't support filtering clusters by cloud."
    ),
    hidden=True,
)
def list(  # noqa: A001, PLR0913
    name: Optional[str],
    cluster_id: Optional[str],
    project_id: Optional[str],
    project: Optional[str],
    include_all_projects: bool,
    include_inactive: bool,
    include_archived: bool,
    max_items: int,
    cloud_id: Optional[str],
    cloud: Optional[str],
) -> None:
    cluster_controller = ClusterController()
    cluster_controller.list(
        cluster_name=name,
        cluster_id=cluster_id,
        project_id=project_id,
        project_name=project,
        include_all_projects=include_all_projects,
        include_inactive=include_inactive,
        include_archived=include_archived,
        max_items=max_items,
        cloud_id=cloud_id,
        cloud_name=cloud,
    )


@cluster_cli.command(
    name="network_debug",
    help="Debug local network connectivity to a cluster.",
    hidden=True,
)
@click.argument(
    "cluster_id", required=True, default=None,
)
def network_debug(cluster_id: Optional[str],) -> None:
    """Debug network connectivity to a given Anyscale cluster."""
    cluster_controller = ClusterController()
    cluster_controller.debug_networking(cluster_id=cluster_id)
