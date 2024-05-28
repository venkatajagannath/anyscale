from unittest.mock import Mock

from anyscale.client.openapi_client.models import (
    ListMachinesResponse,
    MachineAllocationState,
    MachineConnectionState,
    MachineInfo,
)
from anyscale.controllers.machine_controller import MachineController


def test_list_machines(mock_auth_api_client: str) -> None:
    response = ListMachinesResponse(
        machines=[
            MachineInfo(
                machine_id="m-123",
                hostname="dummy",
                machine_shape="lambda-a100-80g",
                connection_state=MachineConnectionState.CONNECTED,
                allocation_state=MachineAllocationState.AVAILABLE,
            )
        ]
    )

    api_response = Mock()
    api_response.result = response

    machine_controller = MachineController()
    machine_controller.api_client.list_machines_api_v2_machines_get = Mock(
        return_value=api_response
    )
    output = machine_controller.list_machines(machine_pool_name="pool1")
    assert output == response
