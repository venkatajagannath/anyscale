import json
from typing import Dict, List, Optional
from unittest.mock import Mock, mock_open, patch

import click
import pytest

from anyscale.controllers.cluster_controller import ClusterController
from anyscale.sdk.anyscale_client import StartClusterOptions
from anyscale.sdk.anyscale_client.models.cluster_compute_config import (
    ClusterComputeConfig,
)


@pytest.mark.parametrize(
    "cluster",
    [
        Mock(state="Running", cluster_environment_build_id="build1"),
        Mock(state="Terminated", cluster_environment_build_id="build1"),
    ],
)
@pytest.mark.parametrize(
    "build", [Mock(id="build1", revision=1), Mock(id="build2", revision=2)]
)
@pytest.mark.parametrize("cluster_compute", [Mock(id="compute1"), Mock(id="compute2")])
@pytest.mark.parametrize("passed_cluster_env", [True, False])
@pytest.mark.parametrize("passed_cluster_compute", [True, False])
def test_check_needs_start(
    cluster: Mock,
    build: Mock,
    cluster_compute: Mock,
    passed_cluster_env: bool,
    passed_cluster_compute: bool,
    mock_auth_api_client,
) -> None:
    cluster_controller = ClusterController()

    needs_start = cluster_controller._check_needs_start(
        cluster, build, cluster_compute, passed_cluster_env, passed_cluster_compute
    )
    if cluster.state != "Running":
        assert needs_start
    elif not passed_cluster_env and not passed_cluster_compute:
        assert not needs_start
    elif passed_cluster_env and cluster.cluster_environment_build_id != build.id:
        assert needs_start
    elif passed_cluster_compute and cluster.cluster_compute_id != cluster_compute.id:
        assert needs_start


def test_get_project_id_and_cluster_name_given_cluster_id(mock_auth_api_client):
    cluster_controller = ClusterController()

    # Test passing in cluster id only
    mock_cluster = Mock(id="mock_cluster_id", project_id="mock_project_id")
    mock_cluster.name = "mock_cluster_name"
    cluster_controller.anyscale_api_client.get_cluster = Mock(
        return_value=Mock(result=mock_cluster)
    )
    assert cluster_controller._get_project_id_and_cluster_name(
        cluster_id="mock_cluster_id",
        project_id=None,
        cluster_name=None,
        project_name=None,
        cloud_id=None,
    ) == ("mock_project_id", "mock_cluster_name")

    # Test passing in project id
    cluster_controller._get_or_generate_cluster_name = Mock(  # type: ignore
        return_value="mock_cluster_name1"
    )
    mock_get_and_validate_project_id = Mock(return_value="mock_project_id1")
    with patch.multiple(
        "anyscale.controllers.cluster_controller",
        get_and_validate_project_id=mock_get_and_validate_project_id,
    ):
        assert cluster_controller._get_project_id_and_cluster_name(
            cluster_id=None,
            project_id="mock_project_id1",
            cluster_name=None,
            project_name=None,
            cloud_id=None,
        ) == ("mock_project_id1", "mock_cluster_name1")
        mock_get_and_validate_project_id.assert_called_once_with(
            project_id="mock_project_id1",
            project_name=None,
            parent_cloud_id=None,
            api_client=cluster_controller.api_client,
            anyscale_api_client=cluster_controller.anyscale_api_client,
        )

    # Test passing in project name
    cluster_controller._get_or_generate_cluster_name = Mock(  # type: ignore
        return_value="mock_cluster_name1"
    )
    mock_get_and_validate_project_id.reset_mock()
    with patch.multiple(
        "anyscale.controllers.cluster_controller",
        get_and_validate_project_id=mock_get_and_validate_project_id,
    ):
        assert cluster_controller._get_project_id_and_cluster_name(
            cluster_id=None,
            project_id=None,
            cluster_name=None,
            project_name="mock_project_name1",
            cloud_id=None,
        ) == ("mock_project_id1", "mock_cluster_name1")
        mock_get_and_validate_project_id.assert_called_once_with(
            project_id=None,
            project_name="mock_project_name1",
            parent_cloud_id=None,
            api_client=cluster_controller.api_client,
            anyscale_api_client=cluster_controller.anyscale_api_client,
        )

    # Test passing in cloud_id
    mock_get_and_validate_project_id.reset_mock()
    with patch.multiple(
        "anyscale.controllers.cluster_controller",
        get_and_validate_project_id=mock_get_and_validate_project_id,
    ):
        assert cluster_controller._get_project_id_and_cluster_name(
            cluster_id=None,
            project_id=None,
            cluster_name=None,
            project_name=None,
            cloud_id="mock_cloud_id",
        ) == ("mock_project_id1", "mock_cluster_name1")
        mock_get_and_validate_project_id.assert_called_once_with(
            project_id=None,
            project_name=None,
            parent_cloud_id="mock_cloud_id",
            api_client=cluster_controller.api_client,
            anyscale_api_client=cluster_controller.anyscale_api_client,
        )


def test_get_cluster_env_and_build(mock_auth_api_client):
    cluster_controller = ClusterController()
    mock_get_build_from_cluster_env_identifier = Mock(return_value=Mock(id="build_id1"))
    mock_get_default_cluster_env_build = Mock(return_value=Mock(id="default_build_id"))

    with patch.multiple(
        "anyscale.controllers.cluster_controller",
        get_build_from_cluster_env_identifier=mock_get_build_from_cluster_env_identifier,
        get_default_cluster_env_build=mock_get_default_cluster_env_build,
    ):
        assert (
            cluster_controller._get_cluster_env_and_build(None)[1].id
            == "default_build_id"
        )
        assert (
            cluster_controller._get_cluster_env_and_build("mock_cluster_env")[1].id
            == "build_id1"
        )


def test_load_cluster_compute(mock_auth_api_client):
    cluster_controller = ClusterController()
    cluster_compute_dict = {
        "cloud_id": "mock_cloud_id",
        "max_workers": 10,
        "region": "us-west-2",
        "allowed_azs": ["us-west-2a", "us-west-2b"],
        "head_node_type": {
            "name": "head-1",
            "instance_type": "m5.2xlarge",
            "aws_advanced_configurations": None,
            "gcp_advanced_configurations": None,
            "resources": None,
        },
        "worker_node_types": [],
    }
    with patch(
        "builtins.open", mock_open(read_data=json.dumps(cluster_compute_dict)),
    ):
        assert cluster_controller._load_cluster_compute(
            "cluster_compute_file",
        ) == ClusterComputeConfig(**cluster_compute_dict)


def test_get_cluster_compute(mock_auth_api_client):
    cluster_controller = ClusterController()
    mock_get_cluster_compute_from_name = Mock(
        return_value=Mock(id="new_cluster_compute_1")
    )
    cluster_controller.anyscale_api_client.create_cluster_compute = Mock(
        return_value=Mock(result=Mock(id="create_cluster_compute_2"))
    )
    mock_get_default_cluster_compute = Mock(
        return_value=Mock(id="default_cluster_compute_3_and_5")
    )
    mock_existing_cluster = Mock(cluster_compute_id="mock_existing_cluster_compute_id")
    cluster_controller.anyscale_api_client.get_cluster_compute = Mock(
        return_value=Mock(result=Mock(id="existing_cluster_compute_4"))
    )

    with patch(
        "builtins.open",
        mock_open(
            read_data=json.dumps(
                {
                    "cloud_id": "mock_cloud_id",
                    "region": "mock_region",
                    "head_node_type": "mock_head_node_type",
                    "worker_node_types": "mock_worker_node_types",
                }
            )
        ),
    ), patch.multiple(
        "anyscale.controllers.cluster_controller",
        get_cluster_compute_from_name=mock_get_cluster_compute_from_name,
        get_default_cluster_compute=mock_get_default_cluster_compute,
    ):
        assert (
            cluster_controller._get_cluster_compute(
                "cluster_compute_name1", None, None, None, "mock_project_id"
            ).id
            == "new_cluster_compute_1"
        )
        assert (
            cluster_controller._get_cluster_compute(
                None, "cluster_compute_file2", None, None, "mock_project_id"
            ).id
            == "create_cluster_compute_2"
        )
        assert (
            cluster_controller._get_cluster_compute(
                None, None, "cloud_name3", None, "mock_project_id"
            ).id
            == "default_cluster_compute_3_and_5"
        )
        assert (
            cluster_controller._get_cluster_compute(
                None, None, None, mock_existing_cluster, "mock_project_id"
            ).id
            == "existing_cluster_compute_4"
        )
        assert (
            cluster_controller._get_cluster_compute(
                None, None, None, None, "mock_project_id"
            ).id
            == "default_cluster_compute_3_and_5"
        )


@pytest.mark.parametrize("needs_start", [True, False])
@pytest.mark.parametrize("cluster_exists", [True, False])
def test_start(mock_auth_api_client, needs_start: bool, cluster_exists: bool,) -> None:
    cluster_controller = ClusterController()
    mock_build = Mock(id="build_id")
    mock_cluster_compute = Mock(id="cluster_compute_id")
    cluster_controller._get_project_id_and_cluster_name = Mock(  # type: ignore
        return_value=("mock_project_id", "mock_cluster_name")
    )
    mock_existing_cluster = Mock() if cluster_exists else None
    cluster_list = [mock_existing_cluster] if cluster_exists else []
    cluster_controller.anyscale_api_client.search_clusters = Mock(
        return_value=Mock(results=cluster_list)
    )
    cluster_controller._get_cluster_env_and_build = Mock(  # type: ignore
        return_value=(Mock(id="cluster_env_id"), mock_build)
    )
    cluster_controller._get_cluster_compute = Mock(return_value=mock_cluster_compute)  # type: ignore
    cluster_controller._create_or_update_cluster_data = Mock(  # type: ignore
        return_value=(Mock(id="cluster_id"), needs_start)
    )
    mock_user_service_access = "private"
    mock_cloud = Mock(id="mock_cloud_id")
    mock_cloud.name = "mock_cloud_name"
    cluster_controller.anyscale_api_client.get_cloud = Mock(
        return_value=Mock(result=mock_cloud)
    )
    mock_get_selected_cloud_id_or_default = Mock(return_value="mock_cloud_id")
    mock_get_cluster_compute_from_name = Mock(
        return_value=Mock(id="mock_cluster_compute_id")
    )
    with patch.multiple(
        "anyscale.controllers.cluster_controller",
        wait_for_session_start=Mock(),
        get_selected_cloud_id_or_default=mock_get_selected_cloud_id_or_default,
        get_cluster_compute_from_name=mock_get_cluster_compute_from_name,
    ):
        cluster_controller.start(
            cluster_name=None,
            cluster_id="cluster_id",
            cluster_env_name="cluster_env_name",
            docker=None,
            python_version=None,
            ray_version=None,
            cluster_compute_name="cluster_compute_name",
            cluster_compute_file=None,
            cloud_name=None,
            idle_timeout=None,
            project_id=None,
            project_name=None,
            user_service_access=mock_user_service_access,
        )

    cluster_controller._get_project_id_and_cluster_name.assert_called_once_with(
        "cluster_id", None, None, None, cloud_id="mock_cloud_id",
    )
    mock_get_selected_cloud_id_or_default.assert_called_once_with(
        cluster_controller.api_client,
        cluster_controller.anyscale_api_client,
        cluster_compute_id="mock_cluster_compute_id",
        cluster_compute_config=None,
        cloud_id=None,
        cloud_name=None,
    )
    mock_get_cluster_compute_from_name.assert_called_once_with(
        "cluster_compute_name", cluster_controller.api_client
    )
    cluster_controller.anyscale_api_client.search_clusters.assert_called_once_with(
        {
            "project_id": "mock_project_id",
            "name": {"equals": "mock_cluster_name"},
            "archive_status": "ALL",
        }
    )
    cluster_controller._get_cluster_env_and_build.assert_called_once_with(
        "cluster_env_name"
    )
    cluster_controller._get_cluster_compute.assert_called_once_with(
        "cluster_compute_name", None, None, mock_existing_cluster, "mock_project_id",
    )
    cluster_controller._create_or_update_cluster_data.assert_called_once_with(
        mock_existing_cluster,
        "mock_cluster_name",
        "mock_project_id",
        mock_build,
        mock_cluster_compute,
        True,
        True,
        None,
        mock_user_service_access,
    )

    if needs_start:
        cluster_controller.anyscale_api_client.start_cluster.assert_called_once_with(
            "cluster_id",
            StartClusterOptions(
                cluster_environment_build_id=mock_build.id,
                cluster_compute_id=mock_cluster_compute.id,
            ),
        )


@pytest.mark.parametrize("cluster_list", [[], [Mock(id="mock_cluster_id")]])
@pytest.mark.parametrize(
    "terminate_args",
    [
        {
            "cluster_name": "cluster_name",
            "cluster_id": None,
            "project_id": "project_id",
            "project_name": None,
            "cloud_name": None,
            "cloud_id": None,
        },
        {
            "cluster_name": "cluster_name",
            "cluster_id": None,
            "project_id": None,
            "project_name": None,
            "cloud_name": "cloud_name",
            "cloud_id": None,
        },
    ],
)
def test_terminate(
    mock_auth_api_client,
    cluster_list: List[Mock],
    terminate_args: Dict[str, Optional[str]],
) -> None:
    cluster_controller = ClusterController()
    cluster_controller._get_project_id_and_cluster_name = Mock(  # type: ignore
        return_value=("mock_project_id", "mock_cluster_name")
    )
    cluster_controller.anyscale_api_client.search_clusters = Mock(  # type: ignore
        return_value=Mock(results=cluster_list)
    )
    mock_found_cloud_id = "mock_cloud_id" if terminate_args["cloud_name"] else None
    cluster_controller.api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post = Mock(
        return_value=Mock(result=Mock(id=mock_found_cloud_id))
    )

    with pytest.raises(click.ClickException):
        cluster_controller.terminate(None, None, None, None, None, None)
    with pytest.raises(click.ClickException):
        cluster_controller.terminate(
            "cluster_name", "cluster_id", None, None, None, None
        )
    with pytest.raises(click.ClickException):
        cluster_controller.terminate(
            "cluster_name", None, None, None, "cloud_name", "cloud_id"
        )
    with pytest.raises(click.ClickException):
        cluster_controller.api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get = Mock(
            return_value=Mock(result=Mock(is_on=True))
        )
        cluster_controller.terminate("cluster_name", None, None, None, None, None)
    if len(cluster_list) == 0:
        with pytest.raises(click.ClickException):
            cluster_controller.terminate(**terminate_args)
    else:
        cluster_controller._validate_args_to_find_cluster = Mock()  # type: ignore
        cluster_controller.terminate(**terminate_args)
        cluster_controller._get_project_id_and_cluster_name.assert_called_once_with(
            terminate_args["cluster_id"],
            terminate_args["project_id"],
            terminate_args["cluster_name"],
            terminate_args["project_name"],
            cloud_id=mock_found_cloud_id,
        )
        cluster_controller._validate_args_to_find_cluster.assert_called_once_with(
            terminate_args["cluster_name"],
            terminate_args["cluster_id"],
            terminate_args["project_name"],
            terminate_args["project_id"],
            terminate_args["cloud_name"],
            terminate_args["cloud_id"],
        )
        cluster_controller.anyscale_api_client.search_clusters.assert_called_once_with(
            {"project_id": "mock_project_id", "name": {"equals": "mock_cluster_name"}}
        )
        cluster_controller.anyscale_api_client.terminate_cluster.assert_called_once_with(
            "mock_cluster_id", {}
        )


@pytest.mark.parametrize("cluster_list", [[], [Mock(id="mock_cluster_id")]])
@pytest.mark.parametrize(
    "archive_args",
    [
        {
            "cluster_name": "cluster_name",
            "cluster_id": None,
            "project_id": "project_id",
            "project_name": None,
            "cloud_name": None,
            "cloud_id": None,
        },
        {
            "cluster_name": "cluster_name",
            "cluster_id": None,
            "project_id": None,
            "project_name": None,
            "cloud_name": "cloud_name",
            "cloud_id": None,
        },
    ],
)
def test_archive(
    mock_auth_api_client,
    cluster_list: List[Mock],
    archive_args: Dict[str, Optional[str]],
) -> None:
    cluster_controller = ClusterController()
    cluster_controller._get_project_id_and_cluster_name = Mock(  # type: ignore
        return_value=("mock_project_id", "mock_cluster_name")
    )
    cluster_controller.anyscale_api_client.search_clusters = Mock(  # type: ignore
        return_value=Mock(results=cluster_list)
    )
    mock_found_cloud_id = "mock_cloud_id" if archive_args["cloud_name"] else None
    cluster_controller.api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post = Mock(
        return_value=Mock(result=Mock(id=mock_found_cloud_id))
    )
    with pytest.raises(click.ClickException):
        cluster_controller.archive(
            "cluster_name", None, None, None, "cloud_name", "cloud_id"
        )
    with pytest.raises(click.ClickException):
        cluster_controller.api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get = Mock(
            return_value=Mock(result=Mock(is_on=True))
        )
        cluster_controller.archive("cluster_name", None, None, None, None, None)
    with pytest.raises(click.ClickException):
        cluster_controller.archive(None, None, None, None, None, None)
    with pytest.raises(click.ClickException):
        cluster_controller.archive("cluster_name", "cluster_id", None, None, None, None)

    if len(cluster_list) == 0:
        with pytest.raises(click.ClickException):
            cluster_controller.archive(**archive_args)
    else:
        cluster_controller._validate_args_to_find_cluster = Mock()  # type: ignore
        cluster_controller.archive(**archive_args)
        cluster_controller._get_project_id_and_cluster_name.assert_called_once_with(
            archive_args["cluster_id"],
            archive_args["project_id"],
            archive_args["cluster_name"],
            archive_args["project_name"],
            mock_found_cloud_id,
        )
        cluster_controller._validate_args_to_find_cluster.assert_called_once_with(
            archive_args["cluster_name"],
            archive_args["cluster_id"],
            archive_args["project_name"],
            archive_args["project_id"],
            archive_args["cloud_name"],
            archive_args["cloud_id"],
        )
        cluster_controller.anyscale_api_client.search_clusters.assert_called_once_with(
            {"project_id": "mock_project_id", "name": {"equals": "mock_cluster_name"}}
        )
        cluster_controller.anyscale_api_client.archive_cluster.assert_called_once_with(
            "mock_cluster_id"
        )


@pytest.mark.parametrize("cluster_name", ["mock_cluster_name", None])
@pytest.mark.parametrize("cluster_id", ["mock_cluster_id", None])
@pytest.mark.parametrize("project_name", ["mock_project_name", None])
@pytest.mark.parametrize("project_id", ["mock_project_id", None])
@pytest.mark.parametrize("cloud_name", ["mock_cloud_name", None])
@pytest.mark.parametrize("cloud_id", ["mock_cloud_id", None])
@pytest.mark.parametrize("cloud_isolation_ff_on", [True, False])
def test_validate_args_to_find_cluster(  # noqa: PLR0913
    mock_auth_api_client,
    cluster_name: Optional[str],
    cluster_id: Optional[str],
    project_name: Optional[str],
    project_id: Optional[str],
    cloud_name: Optional[str],
    cloud_id: Optional[str],
    cloud_isolation_ff_on: bool,
):
    cluster_controller = ClusterController()
    cluster_controller.api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get = Mock(
        return_value=Mock(result=Mock(is_on=cloud_isolation_ff_on))
    )
    if (bool(cluster_name) + bool(cluster_id) != 1) or (
        bool(cloud_name) + bool(cloud_id) > 1
    ):
        with pytest.raises(click.ClickException):
            cluster_controller._validate_args_to_find_cluster(
                cluster_name, cluster_id, project_name, project_id, cloud_name, cloud_id
            )
        return
    if (
        cloud_isolation_ff_on
        and cluster_name
        and not (project_name or project_id or cloud_name or cloud_id)
    ):
        with pytest.raises(click.ClickException):
            cluster_controller._validate_args_to_find_cluster(
                cluster_name, cluster_id, project_name, project_id, cloud_name, cloud_id
            )
        return
    # Verify runs successfully
    cluster_controller._validate_args_to_find_cluster(
        cluster_name, cluster_id, project_name, project_id, cloud_name, cloud_id
    )
