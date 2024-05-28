from typing import Optional
from unittest.mock import call, Mock

from openapi_client.rest import ApiException
import pytest

from anyscale.client.openapi_client.models import Cloud, CloudResponse
from anyscale.cloud import (
    get_all_clouds,
    get_cloud_id_and_name,
    get_cloud_json_from_id,
    get_last_used_cloud,
    get_organization_default_cloud,
)
from anyscale.sdk.anyscale_client.models import ListResponseMetadata
from anyscale.sdk.anyscale_client.models.cloud_list_response import CloudListResponse


def test_get_cloud_json_from_id(cloud_test_data: Cloud) -> None:
    mock_api_client = Mock()
    mock_api_client.get_cloud_api_v2_clouds_cloud_id_get.return_value = CloudResponse(
        result=cloud_test_data
    )
    cloud_json = get_cloud_json_from_id(cloud_test_data.id, api_client=mock_api_client)
    expected_json = {
        "id": cloud_test_data.id,
        "name": cloud_test_data.name,
        "provider": cloud_test_data.provider,
        "region": cloud_test_data.region,
        "credentials": cloud_test_data.credentials,
        "config": cloud_test_data.config,
        "state": "ACTIVE",
    }
    assert cloud_json == expected_json
    mock_api_client.get_cloud_api_v2_clouds_cloud_id_get.assert_called_once_with(
        cloud_id=cloud_test_data.id
    )


def test_get_cloud_json_from_id_api_error(base_mock_api_client: Mock) -> None:
    base_mock_api_client.get_cloud_api_v2_clouds_cloud_id_get = Mock(
        side_effect=ApiException()
    )
    cloud_json = get_cloud_json_from_id("cld_1234", base_mock_api_client)
    expected_json = {
        "error": {
            "cloud_id": "cld_1234",
            "message": "The cloud with id, cld_1234 has been deleted. Please create a new cloud with `anyscale cloud setup`.",
        }
    }
    assert cloud_json == expected_json


def test_get_cloud_id_and_name_no_args(
    base_mock_api_client: Mock, cloud_test_data: Cloud
) -> None:
    with pytest.raises(Exception):  # noqa: PT011
        get_cloud_id_and_name(base_mock_api_client)


def test_get_cloud_id_and_name_two_args(
    base_mock_api_client: Mock, cloud_test_data: Cloud
) -> None:
    with pytest.raises(Exception):  # noqa: PT011
        get_cloud_id_and_name(
            base_mock_api_client, cloud_test_data.id, cloud_test_data.name
        )


def test_get_cloud_id_and_name_id_only(
    base_mock_api_client: Mock, cloud_test_data: Cloud
) -> None:
    base_mock_api_client.get_cloud_api_v2_clouds_cloud_id_get = Mock(
        return_value=CloudResponse(result=cloud_test_data)
    )
    result_id, result_name = get_cloud_id_and_name(
        base_mock_api_client, cloud_id=cloud_test_data.id
    )
    assert result_id == cloud_test_data.id
    assert result_name == cloud_test_data.name
    base_mock_api_client.get_cloud_api_v2_clouds_cloud_id_get.assert_called_once()


def test_get_cloud_id_and_name_name_only(
    base_mock_api_client: Mock, cloud_test_data: Cloud
) -> None:
    base_mock_api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post = Mock(
        return_value=CloudResponse(result=cloud_test_data)
    )
    result_id, result_name = get_cloud_id_and_name(
        base_mock_api_client, cloud_name=cloud_test_data.name
    )
    assert result_id == cloud_test_data.id
    assert result_name == cloud_test_data.name
    base_mock_api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post.assert_called_once()


@pytest.mark.parametrize("default_cloud_exists", [True, False])
@pytest.mark.parametrize("default_cloud_permissions_exist", [True, False])
def test_get_organization_default_cloud(
    default_cloud_exists: bool, default_cloud_permissions_exist: bool,
):
    mock_api_client = Mock()
    mock_user = Mock(
        organizations=[
            Mock(
                default_cloud_id="test_default_cloud_id"
                if default_cloud_exists
                else None
            )
        ]
    )
    mock_api_client.get_user_info_api_v2_userinfo_get = Mock(
        return_value=Mock(result=mock_user)
    )
    mock_cloud = Mock(id="test_default_cloud_id")
    mock_cloud.name = "test_default_cloud_name"
    if not default_cloud_permissions_exist:
        mock_api_client.get_cloud_api_v2_clouds_cloud_id_get = Mock(
            return_value=Mock(result=None)
        )
    else:
        mock_api_client.get_cloud_api_v2_clouds_cloud_id_get = Mock(
            return_value=Mock(result=mock_cloud)
        )

    if not default_cloud_exists or not default_cloud_permissions_exist:
        assert get_organization_default_cloud(mock_api_client) is None
    else:
        assert (
            get_organization_default_cloud(mock_api_client) == "test_default_cloud_name"
        )
    mock_api_client.get_user_info_api_v2_userinfo_get.assert_called_once_with()
    if default_cloud_exists:
        mock_api_client.get_cloud_api_v2_clouds_cloud_id_get.assert_called_once_with(
            cloud_id="test_default_cloud_id"
        )


@pytest.mark.parametrize("cloud_id", ["test_cloud_id", None])
def test_get_last_used_cloud(cloud_id: Optional[str]):
    mock_anyscale_api_client = Mock()
    mock_anyscale_api_client.get_project = Mock(
        return_value=Mock(result=Mock(last_used_cloud_id=cloud_id))
    )
    mock_cloud = Mock(id="test_cloud_id")
    mock_cloud.name = "test_cloud_name"
    mock_anyscale_api_client.get_cloud = Mock(return_value=Mock(result=mock_cloud))
    mock_anyscale_api_client.search_clouds = Mock(
        return_value=Mock(results=[mock_cloud], metadata=Mock(next_paging_token=None))
    )

    assert (
        get_last_used_cloud("test_project_id", mock_anyscale_api_client)
        == "test_cloud_name"
    )
    mock_anyscale_api_client.get_project.assert_called_once_with("test_project_id")
    if cloud_id:
        mock_anyscale_api_client.get_cloud.assert_called_once_with("test_cloud_id")
    else:
        mock_anyscale_api_client.search_clouds.assert_called_once_with(
            {"paging": {"count": 50}}
        )


def test_get_all_clouds() -> None:
    mock_cloud_1 = Mock()
    mock_cloud_1.name = "cloud_1"
    mock_cloud_2 = Mock()
    mock_cloud_2.name = "cloud_2"

    mock_anyscale_api_client = Mock()
    mock_anyscale_api_client.search_clouds.side_effect = [
        CloudListResponse(
            results=[mock_cloud_1],
            metadata=ListResponseMetadata(
                total=2, next_paging_token="next_paging_token"
            ),
        ),
        CloudListResponse(
            results=[mock_cloud_2], metadata=ListResponseMetadata(total=2),
        ),
    ]

    all_clouds = get_all_clouds(mock_anyscale_api_client)
    assert all_clouds == [mock_cloud_1, mock_cloud_2]
    mock_anyscale_api_client.search_clouds.assert_has_calls(
        [
            call({"paging": {"count": 50}}),
            call({"paging": {"count": 50, "paging_token": "next_paging_token"}}),
        ]
    )
