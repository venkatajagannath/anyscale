from typing import Optional
from unittest.mock import ANY, Mock

import pytest

from anyscale.cluster_compute import (
    get_cluster_compute_from_name,
    get_default_cluster_compute,
    get_selected_cloud_id_or_default,
    parse_cluster_compute_name_version,
    register_compute_template,
)
from anyscale.sdk.anyscale_client import ArchiveStatus, CreateComputeTemplate
from anyscale.sdk.anyscale_client.models.cluster_compute_config import (
    ClusterComputeConfig,
)
from anyscale.sdk.anyscale_client.models.compute_template_query import (
    ComputeTemplateQuery,
)


def test_get_default_cluster_compute():
    mock_api_client = Mock()
    mock_anyscale_api_client = Mock()
    mock_anyscale_api_client.get_default_compute_config = Mock(
        return_value=Mock(result="mock_config_obj")
    )
    mock_default_config_obj = {
        "cloud_id": "cld_1",
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
    mock_anyscale_api_client.get_default_compute_config = Mock(
        return_value=Mock(result=mock_default_config_obj)
    )
    mock_api_client.create_compute_template_api_v2_compute_templates_post = Mock(
        return_value=Mock(result="mock_compute_template")
    )
    mock_api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post = Mock(
        return_value=Mock(result=Mock(id="test_cloud_id"))
    )

    assert (
        get_default_cluster_compute(
            "mock_cloud_name", None, mock_api_client, mock_anyscale_api_client
        )
        == "mock_compute_template"
    )
    mock_anyscale_api_client.get_default_compute_config.assert_called_once_with(
        "test_cloud_id"
    )


def test_register_compute_template():
    mock_api_client = Mock()
    mock_api_client.create_compute_template_api_v2_compute_templates_post = Mock(
        return_value=Mock(result=Mock(id="mock_template_id"))
    )

    assert (
        register_compute_template("mock_template_obj", mock_api_client).id
        == "mock_template_id"
    )
    mock_api_client.create_compute_template_api_v2_compute_templates_post.assert_called_once_with(
        create_compute_template=CreateComputeTemplate(
            name=ANY, config="mock_template_obj", anonymous=True,
        )
    )


@pytest.mark.parametrize(
    "is_archived", [True, False, None],
)
@pytest.mark.parametrize(
    "include_archived", [True, False],
)
@pytest.mark.parametrize(
    (
        "enable_compute_config_versioning",
        "compute_config_name_version",
        "expected_name",
        "expected_version",
    ),
    [
        (True, "mock_name", "mock_name", None),
        (True, "mock_name:2", "mock_name", 2),
        (False, "mock_name", "mock_name", None),
        (False, "mock_name:2", "mock_name:2", None),
    ],
)
def test_get_cluster_compute_from_name(
    is_archived: Optional[bool],
    include_archived: bool,
    enable_compute_config_versioning: bool,
    compute_config_name_version: str,
    expected_name: str,
    expected_version: Optional[int],
):
    mock_api_client = Mock()
    mock_api_client.search_compute_templates_api_v2_compute_templates_search_post = Mock(
        return_value=Mock(
            results=[
                Mock(
                    id="mock_id",
                    archived_at="2021-01-01T00:00:00Z" if is_archived else None,
                )
            ]
        )
    )

    def mock_feature_flag_api(feature_flag: str):
        if feature_flag == "compute-config-versioning":
            return Mock(result=Mock(is_on=enable_compute_config_versioning))

    mock_api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get = Mock(
        side_effect=mock_feature_flag_api
    )

    if is_archived and not include_archived:
        with pytest.raises(ValueError) as e:
            get_cluster_compute_from_name(
                compute_config_name_version,
                mock_api_client,
                include_archived=include_archived,
            )
            assert f"The compute config {expected_name} is archived." in str(e)
    else:
        assert (
            get_cluster_compute_from_name(
                compute_config_name_version,
                mock_api_client,
                include_archived=include_archived,
            ).id
            == "mock_id"
        )

    mock_api_client.search_compute_templates_api_v2_compute_templates_search_post.assert_called_once_with(
        ComputeTemplateQuery(
            orgwide=True,
            name={"equals": expected_name},
            include_anonymous=True,
            archive_status=ArchiveStatus.ALL,
            version=expected_version,
        )
    )


def test_get_selected_cloud_id_or_default():
    mock_api_client = Mock()
    mock_anyscale_api_client = Mock()

    mock_cloud = Mock(id="mock_cloud_id")
    mock_cloud.name = "mock_cloud_name"

    # Test getting cloud from cluster compute id
    assert (
        get_selected_cloud_id_or_default(
            api_client=mock_api_client,
            anyscale_api_client=mock_anyscale_api_client,
            cluster_compute_id="mock_cluster_compute_id",
        )
        == mock_anyscale_api_client.get_cluster_compute(
            "mock_cluster_compute_id"
        ).result.config.cloud_id
    )

    # Test getting cloud from cluster compute config
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
    cluster_compute_config = ClusterComputeConfig(**cluster_compute_dict)
    assert (
        get_selected_cloud_id_or_default(
            api_client=mock_api_client,
            anyscale_api_client=mock_anyscale_api_client,
            cluster_compute_config=cluster_compute_config,
        )
        == "mock_cloud_id"
    )

    # Test getting cloud from cloud_id
    mock_api_client.get_cloud_api_v2_clouds_cloud_id_get = Mock(
        return_value=Mock(result=mock_cloud)
    )
    assert (
        get_selected_cloud_id_or_default(
            api_client=mock_api_client,
            anyscale_api_client=mock_anyscale_api_client,
            cloud_id="mock_cloud_id",
        )
        == "mock_cloud_id"
    )
    mock_api_client.get_cloud_api_v2_clouds_cloud_id_get.assert_called_once_with(
        cloud_id="mock_cloud_id"
    )

    # Test getting cloud from cloud_name
    mock_api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post = Mock(
        return_value=Mock(result=mock_cloud)
    )
    assert (
        get_selected_cloud_id_or_default(
            api_client=mock_api_client,
            anyscale_api_client=mock_anyscale_api_client,
            cloud_name="mock_cloud_name",
        )
        == "mock_cloud_id"
    )
    mock_api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post.assert_called_once_with(
        cloud_name_options={"name": "mock_cloud_name"}
    )

    # Test getting cloud from default cluster compute
    mock_anyscale_api_client.get_default_cluster_compute = Mock(
        return_value=Mock(result=Mock(config=Mock(cloud_id="mock_default_cloud_id")))
    )
    assert (
        get_selected_cloud_id_or_default(
            api_client=mock_api_client, anyscale_api_client=mock_anyscale_api_client
        )
        == "mock_default_cloud_id"
    )
    mock_anyscale_api_client.get_default_cluster_compute.assert_called_once_with()


@pytest.mark.parametrize(
    ("cluster_compute_name_version", "expected_name", "expected_version", "error"),
    [
        ("name", "name", None, False),
        ("1", "1", None, False),
        ("name:0", None, None, True),
        ("name:1", "name", 1, False),
        ("name:2", "name", 2, False),
        ("name:3", "name", 3, False),
        ("name:4", "name", 4, False),
        ("name:5", "name", 5, False),
        ("name:6", "name", 6, False),
        ("name:7", "name", 7, False),
        ("name:8", "name", 8, False),
        ("name:9", "name", 9, False),
        ("name:10", "name", 10, False),
        ("10:10", "10", 10, False),
        ("name:0010", None, None, True),
        ("name with spaces:11", "name with spaces", 11, False),
        ("name with    more   spaces:11", "name with    more   spaces", 11, False),
        ("name-with-tailing-spaces :11", None, None, True),
        ("name-with-tailing-spaces ", None, None, True),
        (" name-with-leading-spaces:11", None, None, True),
        (" name-with-leading-spaces", None, None, True),
        (" name-with-tailing-and-leading-spaces :11", None, None, True),
        (" name-with-tailing-and-leading-spaces ", None, None, True),
        (
            "name-with-special-chars !@#$%^&*()-:123",
            "name-with-special-chars !@#$%^&*()-",
            123,
            False,
        ),
        ("version-with-spaces: 123", None, None, True),
        ("version-with-spaces:123 ", None, None, True),
        ("version-with-spaces:1 23", None, None, True),
        ("version-is-not-integer:_123", None, None, True),
        ("version-is-not-integer:v123", None, None, True),
        ("version-is-not-integer:my-version", None, None, True),
        ("more-than-one-colons:1:2", None, None, True),
        ("more-than-one-colons:abc:2", None, None, True),
        ("more-than-one-colons:::2", None, None, True),
        (":1", None, None, True),
        (":", None, None, True),
    ],
)
def test_parse_cluster_compute_name_version(
    cluster_compute_name_version: str,
    expected_name: str,
    expected_version: int,
    error: bool,
):
    if error:
        with pytest.raises(ValueError) as e:
            parse_cluster_compute_name_version(cluster_compute_name_version)
            assert "Invalid compute config name and version" in str(e)
    else:
        assert parse_cluster_compute_name_version(cluster_compute_name_version) == (
            expected_name,
            expected_version,
        )
