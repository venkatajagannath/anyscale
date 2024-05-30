from typing import Any, Dict, Optional, Union
from unittest.mock import ANY, Mock, patch

import click
import pytest
import yaml
from yaml.loader import SafeLoader

from anyscale.conf import IDLE_TIMEOUT_DEFAULT_MINUTES
from anyscale.controllers.compute_config_controller import (
    ComputeConfigController,
    CreateClusterComputeConfigModel,
)
from anyscale.sdk.anyscale_client.models.archive_status import ArchiveStatus
from anyscale.sdk.anyscale_client.models.cluster_compute import ClusterCompute
from anyscale.sdk.anyscale_client.models.clustercompute_list_response import (
    ClustercomputeListResponse,
)
from anyscale.sdk.anyscale_client.models.clustercompute_response import (
    ClustercomputeResponse,
)
from anyscale.sdk.anyscale_client.models.compute_template import ComputeTemplate
from anyscale.sdk.anyscale_client.models.compute_template_query import (
    ComputeTemplateQuery,
)
from anyscale.sdk.anyscale_client.models.create_cluster_compute import (
    CreateClusterCompute,
)
from anyscale.utils.entity_arg_utils import EntityType, IdBasedEntity, NameBasedEntity


@pytest.fixture()
def mock_auth_api_client(mock_api_client: Mock, mock_sdk_client: Mock):
    mock_auth_api_client = Mock(
        api_client=mock_api_client, anyscale_api_client=mock_sdk_client,
    )
    with patch.multiple(
        "anyscale.controllers.base_controller",
        get_auth_api_client=Mock(return_value=mock_auth_api_client),
    ):
        yield


@pytest.fixture()
def example_compute_config() -> Dict[str, Any]:

    example_compute_config_str = """

    {
    "cloud_id": "cld_HSrCZdMCYDe1NmMCJhYRgQ4p",
    "max_workers": 20,
    "maximum_uptime_minutes": null,
    "allowed_azs": null,
    "head_node_type": {
        "name": "head-node-type",
        "instance_type": "m5.2xlarge",
        "resources": null,
        "flags": {}
    },
    "worker_node_types": [
        {
        "name": "worker-node-type-0",
        "instance_type": "m5.4xlarge",
        "resources": null,
        "min_workers": null,
        "max_workers": 10,
        "use_spot": false,
        "flags": {}
        },
        {
        "name": "worker-node-type-1",
        "instance_type": "g4dn.4xlarge",
        "resources": null,
        "min_workers": null,
        "max_workers": 10,
        "use_spot": false,
        "flags": {}
        }
    ],
    "aws_advanced_configurations_json": null,
    "gcp_advanced_configurations_json": null,
    "aws": null,
    "gcp": null,
    "azure": null,
    "auto_select_worker_config": false,
    "flags": {},
    }
    """
    return yaml.load(example_compute_config_str, Loader=SafeLoader)


# Used for generating the compute config read model from the write model.
# These fields may have these values if the customer didn't specify them,
# or because of backwards compatibility reasons.
def compute_config_with_default_fields(
    write_compute_config: Dict[str, Any]
) -> Dict[str, Any]:
    default_fields = {
        "idle_termination_minutes": IDLE_TIMEOUT_DEFAULT_MINUTES,
        "region": None,
    }
    return dict(**write_compute_config, **default_fields)


@pytest.fixture()
def mock_api_client() -> Mock:
    mock_api_client = Mock()

    return mock_api_client


@pytest.fixture()
def mock_sdk_client(cluster_compute_test_data: ClusterCompute) -> Mock:
    mock_sdk_client = Mock()

    mock_sdk_client.create_cluster_compute = Mock(
        return_value=ClustercomputeResponse(result=cluster_compute_test_data)
    )
    mock_sdk_client.search_cluster_computes = Mock(
        return_value=ClustercomputeListResponse(results=[cluster_compute_test_data])
    )
    mock_sdk_client.get_cluster_compute = Mock()

    return mock_sdk_client


@pytest.mark.parametrize("cloud_id", [None, "test_cloud_id"])
@pytest.mark.parametrize("cloud", [None, "test_cloud_name"])
def test_create_validation(
    example_compute_config: Dict[str, Any],
    cloud_id: Optional[str],
    cloud: Optional[str],
):
    mock_get_cloud_id_and_name = Mock(return_value=("test_cloud_id", "test_cloud_name"))
    example_compute_config["cloud_id"] = cloud_id
    example_compute_config["cloud"] = cloud
    with patch.multiple(
        "anyscale.controllers.compute_config_controller",
        get_cloud_id_and_name=mock_get_cloud_id_and_name,
    ):
        if bool(cloud_id) + bool(cloud) != 1:
            with pytest.raises(click.ClickException):
                CreateClusterComputeConfigModel(**example_compute_config)
        else:
            CreateClusterComputeConfigModel(**example_compute_config)


@pytest.mark.parametrize("name", [None, "test_name"])
@pytest.mark.parametrize("enable_compute_config_versioning", [True, False])
def test_create(
    mock_auth_api_client,
    name: Optional[str],
    enable_compute_config_versioning: bool,
    example_compute_config: Dict[str, Any],
) -> None:
    compute_config_controller = ComputeConfigController()

    mock_load = Mock(return_value=example_compute_config)
    mock_cluster_compute_io = Mock()
    compute_config_controller.api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get = Mock(
        return_value=Mock(result=Mock(is_on=enable_compute_config_versioning))
    )
    with patch.multiple("yaml", load=mock_load):
        compute_config_controller.create(mock_cluster_compute_io, name)

    compute_config_controller.anyscale_api_client.create_cluster_compute.assert_called_once_with(
        CreateClusterCompute(
            name=ANY,
            config=compute_config_with_default_fields(example_compute_config),
            new_version=enable_compute_config_versioning,
        )
    )


@pytest.mark.parametrize(
    "cluster_compute_entity",
    [IdBasedEntity(id="cpt_123"), NameBasedEntity(name="compute_config_name"),],
)
def test_archive(
    mock_auth_api_client,
    cluster_compute_entity: Union[IdBasedEntity, NameBasedEntity],
    compute_template_test_data: ComputeTemplate,
) -> None:
    compute_config_controller = ComputeConfigController()

    if cluster_compute_entity.type is EntityType.NAME:
        compute_config_controller.api_client.search_compute_templates_api_v2_compute_templates_search_post = Mock(
            return_value=Mock(results=[compute_template_test_data])
        )
        compute_config_controller.archive(cluster_compute_entity)
        compute_config_controller.api_client.search_compute_templates_api_v2_compute_templates_search_post.assert_called_once_with(
            ComputeTemplateQuery(
                orgwide=True,
                name={"equals": cluster_compute_entity.name},
                include_anonymous=True,
                archive_status=ArchiveStatus.ALL,
            )
        )
        compute_config_controller.api_client.archive_compute_template_api_v2_compute_templates_compute_template_id_archive_post.assert_called_once_with(
            compute_template_test_data.id
        )
    elif cluster_compute_entity.type is EntityType.ID:
        compute_config_controller.archive(cluster_compute_entity)
        compute_config_controller.anyscale_api_client.get_compute_template.assert_called_once_with(
            cluster_compute_entity.id
        )
        compute_config_controller.api_client.archive_compute_template_api_v2_compute_templates_compute_template_id_archive_post.assert_called_once_with(
            cluster_compute_entity.id
        )


@pytest.mark.parametrize("cluster_compute_name", [None, "test_cluster_compute_name"])
@pytest.mark.parametrize("cluster_compute_id", [None, "test_cluster_compute_id"])
def test_get(
    mock_auth_api_client,
    cluster_compute_name: Optional[str],
    cluster_compute_id: Optional[str],
    compute_template_test_data: ComputeTemplate,
):
    compute_config_controller = ComputeConfigController()
    if (cluster_compute_name is None and cluster_compute_id is None) or (
        cluster_compute_name is not None and cluster_compute_id is not None
    ):
        with pytest.raises(click.ClickException):
            compute_config_controller.get(
                cluster_compute_name=cluster_compute_name,
                cluster_compute_id=cluster_compute_id,
            )
            return
    else:
        with patch.multiple(
            "anyscale.controllers.compute_config_controller",
            get_cluster_compute_from_name=Mock(
                return_value=Mock(id=cluster_compute_id)
            ),
        ):
            compute_config_controller.anyscale_api_client.get_cluster_compute = Mock(
                return_value=Mock(result=compute_template_test_data)
            )
            compute_config_controller.get(
                cluster_compute_name=cluster_compute_name,
                cluster_compute_id=cluster_compute_id,
            )
            compute_config_controller.anyscale_api_client.get_cluster_compute.assert_called_once_with(
                cluster_compute_id
            )


@pytest.mark.parametrize("cluster_compute_name", [None, "test_cluster_compute_name"])
@pytest.mark.parametrize("cluster_compute_id", [None, "test_cluster_compute_id"])
@pytest.mark.parametrize("include_shared", [True, False])
def test_list(
    mock_auth_api_client,
    cluster_compute_name: Optional[str],
    cluster_compute_id: Optional[str],
    include_shared: bool,
):
    compute_config_controller = ComputeConfigController()
    compute_config_controller.anyscale_api_client.search_cluster_computes = Mock(
        return_value=Mock(results=[Mock()], metadata=Mock(next_paging_token=None))
    )
    compute_config_controller.list(
        cluster_compute_name=cluster_compute_name,
        cluster_compute_id=cluster_compute_id,
        include_shared=include_shared,
        max_items=50,
    )

    if cluster_compute_id:
        compute_config_controller.anyscale_api_client.get_cluster_compute.assert_called_once_with(
            cluster_compute_id
        )
    elif cluster_compute_name:
        compute_config_controller.anyscale_api_client.search_cluster_computes.assert_called_once_with(
            {"name": {"equals": cluster_compute_name}, "paging": {"count": 1}}
        )
    elif not include_shared:
        compute_config_controller.api_client.get_user_info_api_v2_userinfo_get.assert_called_once_with()
        compute_config_controller.anyscale_api_client.search_cluster_computes.assert_called_once_with(
            {"creator_id": ANY, "paging": {"count": 20}}
        )
