from unittest.mock import Mock

from anyscale.client.openapi_client.models import (
    AttachMachinePoolToCloudRequest,
    CreateMachinePoolResponse,
    DeleteMachinePoolRequest,
    DetachMachinePoolFromCloudRequest,
    ListMachinePoolsResponse,
    MachinePool,
)
from anyscale.client.openapi_client.models.cloud import Cloud
from anyscale.controllers.machine_pool_controller import MachinePoolController


def test_create_machine_pool(mock_auth_api_client) -> None:
    response = CreateMachinePoolResponse(
        machine_pool=MachinePool(
            machine_pool_name="pool1",
            machine_pool_id="mp-123",
            organization_id="org-123",
            cloud_ids=[],
        )
    )
    api_response = Mock()
    api_response.result = response

    machine_pool_controller = MachinePoolController()
    machine_pool_controller.api_client.create_machine_pool_api_v2_machine_pools_create_post = Mock(
        return_value=api_response
    )
    output = machine_pool_controller.create_machine_pool(machine_pool_name="pool1")
    assert output == response


def test_delete_machine_pool(mock_auth_api_client) -> None:
    api_response = Mock()
    api_response.result = ""

    machine_pool_controller = MachinePoolController()
    machine_pool_controller.api_client.delete_machine_pool_api_v2_machine_pools_delete_post = Mock(
        return_value=api_response
    )
    machine_pool_controller.delete_machine_pool(machine_pool_name="pool1")
    machine_pool_controller.api_client.delete_machine_pool_api_v2_machine_pools_delete_post.assert_called_once_with(
        DeleteMachinePoolRequest(machine_pool_name="pool1")
    )


def test_list_machine_pool(mock_auth_api_client) -> None:
    response = ListMachinePoolsResponse(
        machine_pools=[
            MachinePool(
                machine_pool_name="pool1",
                machine_pool_id="mp-123",
                organization_id="org-123",
                cloud_ids=[],
            )
        ]
    )

    api_response = Mock()
    api_response.result = response

    machine_pool_controller = MachinePoolController()
    machine_pool_controller.api_client.list_machine_pools_api_v2_machine_pools_get = Mock(
        return_value=api_response
    )
    output = machine_pool_controller.list_machine_pools()
    assert output == response


def test_attach_machine_pool_to_cloud(mock_auth_api_client) -> None:
    machine_pool_controller = MachinePoolController()
    machine_pool_controller.api_client.attach_machine_pool_to_cloud_api_v2_machine_pools_attach_post = Mock(
        return_value=""
    )

    find_cloud_by_name_response = Mock()
    find_cloud_by_name_response.result = Cloud(
        id="cld_1",
        name="cloud1",
        provider="aws",
        region="us-east-1",
        credentials={},
        type="",
        creator_id="123",
        created_at="123",
        is_default=True,
        customer_aggregated_logs_config_id="calc_fake_id",
    )
    machine_pool_controller.api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post = Mock(
        return_value=find_cloud_by_name_response
    )

    machine_pool_controller.attach_machine_pool_to_cloud(
        machine_pool_name="pool1", cloud="cloud1"
    )
    machine_pool_controller.api_client.attach_machine_pool_to_cloud_api_v2_machine_pools_attach_post.assert_called_once_with(
        AttachMachinePoolToCloudRequest(machine_pool_name="pool1", cloud_id="cld_1")
    )


def test_detach_machine_pool_from_cloud(mock_auth_api_client) -> None:
    machine_pool_controller = MachinePoolController()
    machine_pool_controller.api_client.detach_machine_pool_from_cloud_api_v2_machine_pools_detach_post = Mock(
        return_value=""
    )

    find_cloud_by_name_response = Mock()
    find_cloud_by_name_response.result = Cloud(
        id="cld_1",
        name="cloud1",
        provider="aws",
        region="us-east-1",
        credentials={},
        type="",
        creator_id="123",
        created_at="123",
        is_default=True,
        customer_aggregated_logs_config_id="calc_fake_id",
    )
    machine_pool_controller.api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post = Mock(
        return_value=find_cloud_by_name_response
    )

    machine_pool_controller.detach_machine_pool_from_cloud(
        machine_pool_name="pool1", cloud="cloud1"
    )
    machine_pool_controller.api_client.detach_machine_pool_from_cloud_api_v2_machine_pools_detach_post.assert_called_once_with(
        DetachMachinePoolFromCloudRequest(machine_pool_name="pool1", cloud_id="cld_1")
    )
