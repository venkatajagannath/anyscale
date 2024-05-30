from typing import Any, Dict, Optional
from unittest.mock import _Call, ANY, call, Mock, patch

import pytest

from anyscale.connect_utils.prepare_cluster import (
    PrepareClusterAction,
    PrepareClusterBlock,
)
from anyscale.sdk.anyscale_client import (
    ArchiveStatus,
    CreateCluster,
    StartClusterOptions,
    UpdateCluster,
)
from anyscale.sdk.anyscale_client.models.compute_template_query import (
    ComputeTemplateQuery,
)


@pytest.fixture()
def mock_prepare_cluster_block():
    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster.PrepareClusterBlock",
        __init__=Mock(return_value=None),
    ):
        prepare_cluster_block = PrepareClusterBlock()
        prepare_cluster_block.anyscale_api_client = Mock()
        prepare_cluster_block.api_client = Mock()
        prepare_cluster_block._ray = Mock()
        prepare_cluster_block.log = Mock()
        prepare_cluster_block.block_label = ""
        return prepare_cluster_block


@pytest.mark.parametrize("cluster_name", [None, "test_cluster_name"])
@pytest.mark.parametrize("ray_cli_is_connected", [True, False])
def test_start_or_create_cluster(
    mock_prepare_cluster_block, cluster_name: Optional[str], ray_cli_is_connected: bool
):
    mock_prepare_cluster_block.anyscale_api_client.list_sessions = Mock(
        return_value=Mock(results=[], metadata=Mock(next_paging_token=None))
    )
    mock_prepare_cluster_block._ray.util.client.ray.is_connected = Mock(
        return_value=ray_cli_is_connected
    )
    mock_cluster = Mock()
    mock_prepare_cluster_block._create_or_update_session_data = Mock(
        return_value=(mock_cluster, True)
    )
    mock_prepare_cluster_block._start_cluster_if_required = Mock()

    mock_prepare_cluster_block._start_or_create_cluster(
        "test_project_id",
        "test_build_id",
        "test_compute_template_id",
        cluster_name,
        100,
        None,
    )

    if not cluster_name:
        mock_prepare_cluster_block.anyscale_api_client.list_sessions.assert_called_once_with(
            "test_project_id", count=50, paging_token=None
        )
    if ray_cli_is_connected:
        mock_prepare_cluster_block._ray.util.disconnect.assert_called_once_with()
    mock_prepare_cluster_block._create_or_update_session_data.assert_called_once_with(
        cluster_name if cluster_name else "cluster-0",
        "test_project_id",
        "test_build_id",
        "test_compute_template_id",
        100,
        False,
        not cluster_name,
    )
    mock_prepare_cluster_block._start_cluster_if_required.assert_called_once_with(
        mock_cluster,
        True,
        "test_project_id",
        "test_build_id",
        "test_compute_template_id",
        None,
    )


@pytest.mark.parametrize("start_required", [True, False])
@pytest.mark.parametrize("allow_public_internet_traffic", [True, False])
def test_start_cluster_if_required(
    mock_prepare_cluster_block,
    start_required: bool,
    allow_public_internet_traffic: bool,
):
    mock_cluster = Mock(id="test_cluster_id")
    mock_cluster.name = "test_cluster_name"

    mock_prepare_cluster_block._create_or_update_session_data = Mock(
        return_value=(mock_cluster, start_required)
    )
    mock_prepare_cluster_block._log_cluster_configs = Mock()
    mock_wait_for_session_start = Mock()
    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster",
        wait_for_session_start=mock_wait_for_session_start,
    ):
        mock_prepare_cluster_block._start_cluster_if_required(
            mock_cluster,
            start_required,
            "test_project_id",
            "test_build_id",
            "test_compute_template_id",
            allow_public_internet_traffic,
        )
    mock_prepare_cluster_block._log_cluster_configs.assert_called_once_with(
        mock_cluster, "test_build_id", "test_compute_template_id", ANY
    )
    if start_required:
        mock_prepare_cluster_block.anyscale_api_client.start_cluster.assert_called_once_with(
            mock_cluster.id,
            StartClusterOptions(
                cluster_environment_build_id="test_build_id",
                cluster_compute_id="test_compute_template_id",
                allow_public_internet_traffic=allow_public_internet_traffic,
            ),
        )
        mock_wait_for_session_start.assert_called_once_with(
            "test_project_id",
            "test_cluster_name",
            mock_prepare_cluster_block.api_client,
            log=mock_prepare_cluster_block.log,
            block_label=mock_prepare_cluster_block.block_label,
        )


@pytest.mark.parametrize("cluster_exists", [True, False])
@pytest.mark.parametrize("start_required", [True, False])
@pytest.mark.parametrize(
    ("idle_timeout", "expected_idle_timeout"), [(None, 120), (100, 100)]
)
def test_create_or_update_session_data(
    mock_prepare_cluster_block,
    cluster_exists: bool,
    start_required: bool,
    idle_timeout: Optional[int],
    expected_idle_timeout: int,
):
    mock_cluster = Mock(state="Running", id="test_cluster_id")
    mock_get_cluster = Mock(
        side_effect=[(mock_cluster if cluster_exists else None), mock_cluster]
    )
    mock_prepare_cluster_block._validate_new_cluster_compute_and_env_match_existing_cluster = Mock(
        return_value=start_required
    )

    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster", get_cluster=mock_get_cluster
    ):
        mock_prepare_cluster_block._create_or_update_session_data(
            "test_cluster_name",
            "test_project_id",
            "test_build_id",
            "test_compute_template_id",
            idle_timeout,
            None,
        )

    if not cluster_exists:
        mock_get_cluster.assert_called_with(
            mock_prepare_cluster_block.anyscale_api_client,
            "test_project_id",
            "test_cluster_name",
        )
        assert mock_get_cluster.call_count == 2
        mock_prepare_cluster_block.anyscale_api_client.create_cluster.assert_called_once_with(
            CreateCluster(
                name="test_cluster_name",
                project_id="test_project_id",
                cluster_environment_build_id="test_build_id",
                cluster_compute_id="test_compute_template_id",
                idle_timeout_minutes=expected_idle_timeout,
                allow_public_internet_traffic=None,
            )
        )
        mock_prepare_cluster_block.anyscale_api_client.update_cluster.assert_not_called()
        mock_prepare_cluster_block._validate_new_cluster_compute_and_env_match_existing_cluster.assert_not_called()
    else:
        mock_get_cluster.assert_called_once_with(
            mock_prepare_cluster_block.anyscale_api_client,
            "test_project_id",
            "test_cluster_name",
        )
        mock_prepare_cluster_block.anyscale_api_client.create_cluster.assert_not_called()
        mock_prepare_cluster_block._validate_new_cluster_compute_and_env_match_existing_cluster.assert_called_once_with(
            "test_project_id", mock_cluster, print_warnings=False
        )
        if idle_timeout:
            mock_prepare_cluster_block.anyscale_api_client.update_cluster.assert_called_once_with(
                mock_cluster.id, UpdateCluster(idle_timeout_minutes=idle_timeout)
            )


def test_create_or_update_session_data_generates_new_cluster_name(
    mock_prepare_cluster_block,
):
    mock_taken_cluster = Mock(
        state="Running", id="test_cluster_id", name="cluster-exists"
    )
    mock_new_cluster = Mock(
        state="Running", id="test_cluster_id", name="cluster-newgen"
    )

    mock_get_cluster = Mock(side_effect=[mock_taken_cluster, None, mock_new_cluster])
    mock_prepare_cluster_block._validate_new_cluster_compute_and_env_match_existing_cluster = (
        Mock()
    )

    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster", get_cluster=mock_get_cluster
    ):
        mock_prepare_cluster_block._create_or_update_session_data(
            "cluster-exists",
            "test_project_id",
            "test_build_id",
            "test_compute_template_id",
            100,
            None,
            True,
        )

    mock_get_cluster.assert_has_calls(
        [
            call(
                mock_prepare_cluster_block.anyscale_api_client,
                "test_project_id",
                "cluster-exists",
            ),
            call(
                mock_prepare_cluster_block.anyscale_api_client, "test_project_id", ANY,
            ),
            call(
                mock_prepare_cluster_block.anyscale_api_client, "test_project_id", ANY,
            ),
        ]
    )
    # assert the newly generated cluster has a different name than the existing cluster
    cluster_name_of_first_get_cluster_call = mock_get_cluster.call_args_list[0][0][-1]
    cluster_name_of_last_get_cluster_call = mock_get_cluster.call_args_list[-1][0][-1]
    assert (
        cluster_name_of_first_get_cluster_call != cluster_name_of_last_get_cluster_call
    )

    mock_prepare_cluster_block.anyscale_api_client.create_cluster.assert_called_once_with(
        CreateCluster(
            name=ANY,
            project_id="test_project_id",
            cluster_environment_build_id="test_build_id",
            cluster_compute_id="test_compute_template_id",
            idle_timeout_minutes=100,
            allow_public_internet_traffic=None,
        )
    )
    mock_prepare_cluster_block.anyscale_api_client.update_cluster.assert_not_called()
    mock_prepare_cluster_block._validate_new_cluster_compute_and_env_match_existing_cluster.assert_not_called()


@pytest.mark.parametrize("needs_update", [True, False])
@pytest.mark.parametrize("cluster_exists", [True, False])
@pytest.mark.parametrize("cluster_name", ["test_cluster_name", None])
@pytest.mark.parametrize("cluster_state", ["Running", "Other"])
def test_get_prepare_cluster_action(
    mock_prepare_cluster_block,
    needs_update: bool,
    cluster_exists: bool,
    cluster_name: Optional[str],
    cluster_state: str,
):
    mock_cluster = Mock(state=cluster_state)
    mock_cluster.name = cluster_name
    mock_prepare_cluster_block.anyscale_api_client.search_clusters = Mock(
        return_value=Mock(results=[mock_cluster] if cluster_exists else [])
    )
    mock_prepare_cluster_block.anyscale_api_client.get_session = Mock(
        return_value=Mock(result=mock_cluster if cluster_exists else None)
    )

    prepare_cluster_action = mock_prepare_cluster_block._get_prepare_cluster_action(
        "test_project_id", cluster_name, needs_update
    )
    if not cluster_name or not cluster_exists:
        assert prepare_cluster_action == PrepareClusterAction.CREATE
    elif cluster_state != "Running":
        assert prepare_cluster_action == PrepareClusterAction.START
    elif needs_update:
        assert prepare_cluster_action == PrepareClusterAction.UPDATE
    else:
        assert prepare_cluster_action == PrepareClusterAction.NO_OP

    if cluster_name:
        mock_prepare_cluster_block.anyscale_api_client.search_clusters.assert_called_once_with(
            {
                "project_id": "test_project_id",
                "name": {"equals": cluster_name},
                "archive_status": "ALL",
            },
        )


@pytest.mark.parametrize("cluster_env_name", ["test_cluster_env_name", None])
def test_get_cluster_build(mock_prepare_cluster_block, cluster_env_name: Optional[str]):
    mock_build = Mock()
    mock_prepare_cluster_block._get_cluster_env_build = Mock(return_value=mock_build)
    mock_prepare_cluster_block._get_default_cluster_env_build = Mock(
        return_value=mock_build
    )

    assert (
        mock_prepare_cluster_block._get_cluster_build(cluster_env_name, None)
        == mock_build
    )

    if cluster_env_name:
        mock_prepare_cluster_block._get_cluster_env_build.assert_called_once_with(
            cluster_env_name, None
        )
    else:
        mock_prepare_cluster_block._get_default_cluster_env_build.assert_called_once_with()


@pytest.mark.parametrize("clust_env_revision", [None, 1])
def test_get_cluster_env_build(
    mock_prepare_cluster_block, clust_env_revision: Optional[int]
):
    mock_cluster_env = Mock(id="test_app_template_id")
    mock_cluster_env.name = "test_cluster_env_name"
    mock_prepare_cluster_block.anyscale_api_client.list_app_configs = Mock(
        return_value=Mock(
            results=[mock_cluster_env], metadata=Mock(next_paging_token=None)
        )
    )
    mock_build1 = Mock(id="build1", revision=1)
    mock_build2 = Mock(id="build2", revision=2)
    mock_prepare_cluster_block.anyscale_api_client.list_builds = Mock(
        return_value=Mock(
            results=[mock_build1, mock_build2], metadata=Mock(next_paging_token=None)
        )
    )

    if clust_env_revision == 1:
        assert (
            mock_prepare_cluster_block._get_cluster_env_build(
                "test_cluster_env_name", clust_env_revision
            )
            == mock_build1
        )
    else:
        assert (
            mock_prepare_cluster_block._get_cluster_env_build(
                "test_cluster_env_name", clust_env_revision
            )
            == mock_build2
        )


@pytest.mark.parametrize("build_pr", [None, "test_build_pr"])
@pytest.mark.parametrize("build_commit", [None, "test_build_commit"])
@pytest.mark.parametrize("cluster_env_name", [None, "test_cluster_env:name"])
@pytest.mark.parametrize("cluster_env_dict", [None, {"key": "val"}])
def test_build_cluster_env_if_needed(
    mock_prepare_cluster_block,
    build_pr: Optional[str],
    build_commit: Optional[str],
    cluster_env_name: Optional[str],
    cluster_env_dict: Optional[Dict[str, Any]],
):
    mock_prepare_cluster_block._build_app_config_from_source = Mock(
        return_value="test_built_cluster_env_name"
    )

    observed_result = mock_prepare_cluster_block._build_cluster_env_if_needed(
        "test_project_id",
        build_pr,
        build_commit,
        cluster_env_dict,
        cluster_env_name,
        False,
    )
    if build_pr or build_commit:
        assert observed_result == "test_built_cluster_env_name"
    elif cluster_env_dict:
        if cluster_env_name:
            assert observed_result == "test_cluster_env-name"
        else:
            assert observed_result.startswith("anonymous_cluster_env-")
        mock_prepare_cluster_block.anyscale_api_client.create_app_config.assert_called_once_with(
            {
                "name": observed_result,
                "project_id": "test_project_id",
                "config_json": cluster_env_dict,
            }
        )
    else:
        assert observed_result == cluster_env_name


@pytest.mark.parametrize("cluster_compute_name", [None, "test_cluster_compute_name"])
@pytest.mark.parametrize("cluster_compute_dict", [None, {"cloud_id": "mock_cloud_id"}])
@pytest.mark.parametrize("cloud_name", [None, "test_cloud_name"])
def test_get_cluster_compute_id(
    mock_prepare_cluster_block,
    cluster_compute_name: Optional[str],
    cluster_compute_dict: Optional[Dict[str, str]],
    cloud_name: Optional[str],
):
    cloud_id = "test_cloud_id"
    mock_get_selected_cloud_id_or_default = Mock(return_value=cloud_id)
    mock_default_config_obj = Mock()
    mock_config_obj_from_cluster_compute_dict = Mock()
    mock_prepare_cluster_block.anyscale_api_client.get_default_compute_config = Mock(
        return_value=Mock(result=mock_default_config_obj)
    )
    mock_search_compute_templates_api_v2_compute_templates_search_post = Mock()
    mock_search_compute_templates_api_v2_compute_templates_search_post.return_value.results = [
        Mock(
            id="mock_cluster_compute_template",
            name="test_cluster_compute_name",
            archived_at=None,
        )
    ]

    mock_prepare_cluster_block.api_client.search_compute_templates_api_v2_compute_templates_search_post = (
        mock_search_compute_templates_api_v2_compute_templates_search_post
    )

    mock_prepare_cluster_block._register_compute_template = Mock(
        return_value="mock_registered_template"
    )

    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster",
        ComputeTemplateConfig=Mock(
            return_value=mock_config_obj_from_cluster_compute_dict
        ),
        get_selected_cloud_id_or_default=mock_get_selected_cloud_id_or_default,
    ):
        observed_result = mock_prepare_cluster_block._get_cluster_compute_id(
            "test_project_id", cluster_compute_name, cluster_compute_dict, cloud_name,
        )

    if cluster_compute_name:

        mock_search_compute_templates_api_v2_compute_templates_search_post.assert_called_once_with(
            ComputeTemplateQuery(
                orgwide=True,
                name={"equals": cluster_compute_name},
                include_anonymous=True,
                archive_status=ArchiveStatus.ALL,
            )
        )
        assert observed_result == "mock_cluster_compute_template"
    else:
        if cluster_compute_dict:
            mock_config_obj = mock_config_obj_from_cluster_compute_dict
        else:
            mock_prepare_cluster_block.anyscale_api_client.get_default_compute_config.assert_called_once_with(
                cloud_id
            )
            mock_config_obj = mock_default_config_obj
        mock_prepare_cluster_block._register_compute_template.assert_called_once_with(
            "test_project_id", mock_config_obj
        )
        assert observed_result == "mock_registered_template"


def test_is_equal_cluster_compute(mock_prepare_cluster_block):
    def mock_get_compute_template(cluster_compute_id: str):
        if cluster_compute_id == "cluster_compute_1_id":
            return Mock(result=Mock(config=cluster_compute_1))
        elif cluster_compute_id == "cluster_compute_2_id":
            return Mock(result=Mock(config=cluster_compute_2))

    mock_prepare_cluster_block.anyscale_api_client.get_compute_template = Mock(
        side_effect=mock_get_compute_template
    )

    # Test cluster computes are equal
    cluster_compute_1 = "test_cluster_compute"
    cluster_compute_2 = "test_cluster_compute"
    assert mock_prepare_cluster_block._is_equal_cluster_compute(
        "cluster_compute_1_id", "cluster_compute_2_id"
    )

    # Test cluster_computes are different
    cluster_compute_1 = "test_cluster_compute"
    cluster_compute_2 = "test_diff_cluster_compute"
    assert not mock_prepare_cluster_block._is_equal_cluster_compute(
        "cluster_compute_1_id", "cluster_compute_2_id"
    )


@pytest.mark.parametrize("build_matches", [True, False])
@pytest.mark.parametrize("cluster_compute_matches", [True, False])
@pytest.mark.parametrize("allow_public_internet_traffic_matches", [True, False])
def test_validate_new_cluster_compute_and_env_match_existing_cluster(
    mock_prepare_cluster_block,
    build_matches: bool,
    cluster_compute_matches: bool,
    allow_public_internet_traffic_matches: bool,
):
    mock_cluster = Mock()
    mock_cluster.build_id = "mock_build_id1"
    mock_cluster.allow_public_internet_traffic = True
    mock_prepare_cluster_block.cluster_env_name = "test_cluster_env_name"
    mock_prepare_cluster_block.cluster_env_revision = "test_cluster_env_revision"
    mock_prepare_cluster_block.cluster_compute_name = "test_cluster_compute_name"
    mock_prepare_cluster_block.cluster_compute_dict = "test_cluster_compute_dict"
    mock_prepare_cluster_block.cloud_name = "test_cloud_name"
    mock_prepare_cluster_block.cluster_env_dict = "test_cluster_env_dict"
    mock_prepare_cluster_block._get_cluster_compute_id = Mock()

    if build_matches:
        mock_prepare_cluster_block._get_cluster_build = Mock(
            return_value=Mock(id="mock_build_id1")
        )
    else:
        mock_prepare_cluster_block._get_cluster_build = Mock(
            return_value=Mock(id="mock_build_id2")
        )

    mock_prepare_cluster_block._is_equal_cluster_compute = Mock(
        return_value=cluster_compute_matches
    )

    mock_prepare_cluster_block.allow_public_internet_traffic = (
        allow_public_internet_traffic_matches
    )

    observed_result = mock_prepare_cluster_block._validate_new_cluster_compute_and_env_match_existing_cluster(
        "test_projet_id", mock_cluster,
    )
    if (
        not build_matches
        or cluster_compute_matches
        or not allow_public_internet_traffic_matches
    ):
        assert observed_result


@pytest.mark.parametrize(
    "get_prepare_cluster_action",
    [
        PrepareClusterAction.CREATE,
        PrepareClusterAction.START,
        PrepareClusterAction.NO_OP,
    ],
)
@pytest.mark.parametrize("cluster_compute_name", ["test_cluster_compute_name", None])
@pytest.mark.parametrize("cluster_env_name", ["test_cluster_env_name", None])
def test_init(
    get_prepare_cluster_action: bool,
    cluster_compute_name: Optional[str],
    cluster_env_name: Optional[str],
):
    cluster_name = "test_cluster_name"
    mock_get_prepare_cluster_action = Mock(return_value=get_prepare_cluster_action)
    mock_cluster = Mock(
        cloud_id="mock_cloud_id", compute_template_id="mock_cluster_compute_id"
    )
    mock_cluster.name = "test_cluster_name"
    mock_build_cluster_env_if_needed = Mock(return_value=cluster_env_name)
    mock_get_cluster_build = Mock(return_value=Mock(id="mock_build_id"))
    mock_get_selected_cloud_id_or_default = Mock(return_value="mock_cloud_id")
    mock_get_cluster_compute_id = Mock(return_value="mock_cluster_compute_id")
    mock_wait_for_app_build = Mock()
    mock_start_or_create_cluster = Mock(return_value="test_cluster_name")
    mock_validate_new_cluster_compute_and_env_match_existing_cluster = Mock()
    mock_log_cluster_configs = Mock()
    mock_cluster_compute_dict = Mock()
    mock_force_rebuild = Mock()
    mock_cluster_env_dict = Mock()
    mock_cluster_env_revision = Mock()

    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster.PrepareClusterBlock",
        _log_cluster_configs=mock_log_cluster_configs,
        _validate_new_cluster_compute_and_env_match_existing_cluster=mock_validate_new_cluster_compute_and_env_match_existing_cluster,
        _start_or_create_cluster=mock_start_or_create_cluster,
        _wait_for_app_build=mock_wait_for_app_build,
        _get_cluster_compute_id=mock_get_cluster_compute_id,
        _get_cluster_build=mock_get_cluster_build,
        _build_cluster_env_if_needed=mock_build_cluster_env_if_needed,
        _get_prepare_cluster_action=mock_get_prepare_cluster_action,
    ), patch.multiple(
        "anyscale.connect_utils.prepare_cluster",
        get_cluster=Mock(return_value=mock_cluster),
        get_auth_api_client=Mock(return_value=Mock()),
        get_selected_cloud_id_or_default=mock_get_selected_cloud_id_or_default,
    ):
        prepare_cluster_block = PrepareClusterBlock(
            project_id="test_project_id",
            cluster_name=cluster_name,
            autosuspend_timeout=10,
            allow_public_internet_traffic=None,
            needs_update=False,
            cluster_compute_name=cluster_compute_name,
            cluster_compute_dict=mock_cluster_compute_dict,
            cloud_name="test_cloud_name",
            build_pr=None,
            force_rebuild=mock_force_rebuild,
            build_commit=None,
            cluster_env_name=cluster_env_name,
            cluster_env_dict=mock_cluster_env_dict,
            cluster_env_revision=mock_cluster_env_revision,
            ray=Mock(),
        )
        prepare_cluster_block.prepare()
        assert prepare_cluster_block.cluster_name == "test_cluster_name"

    mock_get_prepare_cluster_action.assert_called_once_with(
        "test_project_id", cluster_name, False
    )
    if get_prepare_cluster_action in {
        PrepareClusterAction.CREATE,
        PrepareClusterAction.START,
    }:
        mock_build_cluster_env_if_needed.assert_called_once_with(
            "test_project_id",
            None,
            None,
            mock_cluster_env_dict,
            cluster_env_name,
            mock_force_rebuild,
        )
        if cluster_env_name or not cluster_name:
            mock_get_cluster_build.assert_called_once_with(
                cluster_env_name, mock_cluster_env_revision
            )
            build_id = "mock_build_id"
        else:
            build_id = mock_cluster.build_id

        if cluster_compute_name:
            mock_get_cluster_compute_id.assert_called_once_with(
                "test_project_id",
                cluster_compute_name,
                mock_cluster_compute_dict,
                "test_cloud_name",
            )
        mock_wait_for_app_build.assert_called_once_with("test_project_id", build_id)
        mock_start_or_create_cluster.assert_called_once_with(
            project_id="test_project_id",
            build_id=build_id,
            compute_template_id="mock_cluster_compute_id",
            cluster_name=cluster_name,
            autosuspend_timeout=10,
            allow_public_internet_traffic=None,
        )
    else:
        mock_validate_new_cluster_compute_and_env_match_existing_cluster.assert_called_once_with(
            project_id="test_project_id", running_cluster=mock_cluster
        )
        mock_log_cluster_configs.assert_called_once_with(
            mock_cluster, mock_cluster.build_id, mock_cluster.compute_template_id, ANY,
        )
        mock_start_or_create_cluster.assert_not_called()


@pytest.mark.parametrize("idle_timeout", [60, -1])
@pytest.mark.parametrize("maximum_uptime_minutes", [60, -1])
def test_log_cluster_configs(
    mock_prepare_cluster_block, idle_timeout: int, maximum_uptime_minutes: int,
) -> None:
    mock_prepare_cluster_block.anyscale_api_client.get_build = Mock(
        return_value=Mock(result=Mock(application_template_id="env_name", revision=1))
    )
    mock_compute_config_config = Mock(
        id="id", config=Mock(maximum_uptime_minutes=maximum_uptime_minutes)
    )
    mock_compute_config_config.name = "config_name"
    mock_prepare_cluster_block.anyscale_api_client.get_compute_template = Mock(
        return_value=Mock(result=mock_compute_config_config)
    )
    mock_cluster = Mock(id="ses_1", idle_timeout=idle_timeout)
    mock_build_id = "build_id"
    mock_compute_template_id = "compute_template_id"
    mock_url = "url"
    mock_prepare_cluster_block._log_cluster_configs(
        mock_cluster, mock_build_id, mock_compute_template_id, mock_url
    )
    mock_prepare_cluster_block.anyscale_api_client.get_build.assert_called_once_with(
        mock_build_id
    )
    mock_prepare_cluster_block.anyscale_api_client.get_compute_template.assert_called_once_with(
        mock_compute_template_id
    )

    def call_args_for_log_line(name: str, value: str) -> _Call:
        return call(f"{' ' * 2}{(name + ':').ljust(30)}{value}", block_label="")

    def get_auto_terminate_output(value: int) -> str:
        return f"{value} minutes" if value > 0 else "disabled"

    mock_prepare_cluster_block.log.info.assert_has_calls(
        [
            call_args_for_log_line("cluster id", "ses_1"),
            call_args_for_log_line("cluster environment", "env_name:1"),
            call_args_for_log_line("cluster environment id", "build_id"),
            call_args_for_log_line("cluster compute", "config_name"),
            call_args_for_log_line("cluster compute id", "compute_template_id"),
            call_args_for_log_line(
                "idle termination", get_auto_terminate_output(idle_timeout)
            ),
            call_args_for_log_line(
                "maximum uptime", get_auto_terminate_output(maximum_uptime_minutes)
            ),
            call_args_for_log_line("link", "url"),
        ]
    )
