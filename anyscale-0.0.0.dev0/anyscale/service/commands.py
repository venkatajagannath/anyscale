from typing import Optional, Union

from anyscale._private.sdk import sdk_command
from anyscale.service._private.service_sdk import ServiceSDK
from anyscale.service.models import ServiceConfig, ServiceState, ServiceStatus


_SERVICE_SDK_SINGLETON_KEY = "service_sdk"

_DEPLOY_EXAMPLE = """
import anyscale
from anyscale.service.models import ServiceConfig

anyscale.service.deploy(
    ServiceConfig(
        name="my-service",
        applications=[
            {"import_path": "main:app"},
        ],
        working_dir=".",
    ),
    canary_percent=50,
)
"""


@sdk_command(
    _SERVICE_SDK_SINGLETON_KEY,
    ServiceSDK,
    doc_py_example=_DEPLOY_EXAMPLE,
    arg_docstrings={
        "config": "The config options defining the service.",
        "in_place": "Perform an in-place upgrade without starting a new cluster. This can be used for faster iteration during development but is *not* currently recommended for production deploys. This *cannot* be used to change cluster-level options such as image and compute config (they will be ignored).",
        "canary_percent": "The percentage of traffic to send to the canary version of the service (0-100). This can be used to manually shift traffic toward (or away from) the canary version. If not provided, traffic will be shifted incrementally toward the canary version until it reaches 100. Not supported when using --in-place.",
        "max_surge_percent": "Amount of excess capacity allowed to be used while updating the service (0-100). Defaults to 100. Not supported when using --in-place.",
    },
)
def deploy(
    config: ServiceConfig,
    *,
    in_place: bool = False,
    canary_percent: Optional[int] = None,
    max_surge_percent: Optional[int] = None,
    _sdk: ServiceSDK,
) -> str:
    """Deploy a service.

    If no service with the provided name is running, one will be created, else the existing service will be updated.

    This command is asynchronous, so it always returns immediately.

    Returns the id of the deployed service.
    """
    return _sdk.deploy(
        config,
        in_place=in_place,
        canary_percent=canary_percent,
        max_surge_percent=max_surge_percent,
    )


_ROLLBACK_EXAMPLE = """
import anyscale

anyscale.service.rollback(name="my-service")
"""


@sdk_command(
    _SERVICE_SDK_SINGLETON_KEY,
    ServiceSDK,
    doc_py_example=_ROLLBACK_EXAMPLE,
    arg_docstrings={
        "name": "Name of the service. When running in a workspace, this defaults to the workspace name.",
        "max_surge_percent": "Amount of excess capacity allowed to be used while rolling back to the primary version of the service (0-100). Defaults to 100.",
    },
)
def rollback(
    name: Optional[str], *, max_surge_percent: Optional[int] = None, _sdk: ServiceSDK,
) -> str:
    """Rollback to the primary version of the service.

    This command can only be used when there is an active rollout in progress. The
    rollout will be cancelled and the service will revert to the primary version.

    This command is asynchronous, so it always returns immediately.

    Returns the id of the rolled back service.
    """
    return _sdk.rollback(name=name, max_surge_percent=max_surge_percent)


_TERMINATE_EXAMPLE = """
import anyscale

anyscale.service.terminate(name="my-service")
"""


@sdk_command(
    _SERVICE_SDK_SINGLETON_KEY,
    ServiceSDK,
    doc_py_example=_TERMINATE_EXAMPLE,
    arg_docstrings={
        "name": "Name of the service. When running in a workspace, this defaults to the workspace name.",
    },
)
def terminate(name: Optional[str], *, _sdk: ServiceSDK) -> str:
    """Terminate a service.

    This command is asynchronous, so it always returns immediately.

    Returns the id of the terminated service.
    """
    return _sdk.terminate(name=name)


_STATUS_EXAMPLE = """
import anyscale
from anyscale.service.models import ServiceStatus

status: ServiceStatus = anyscale.service.status(name="my-service")
"""


@sdk_command(
    _SERVICE_SDK_SINGLETON_KEY,
    ServiceSDK,
    doc_py_example=_STATUS_EXAMPLE,
    arg_docstrings={"name": "Name of the service.",},
)
def status(name: str, *, _sdk: ServiceSDK) -> ServiceStatus:
    """Get the status of a service."""
    return _sdk.status(name=name)


_WAIT_EXAMPLE = """
import anyscale
from anyscale.service.models import ServiceState

anyscale.service.wait(name="my-service", state=ServiceState.RUNNING)
"""


@sdk_command(
    _SERVICE_SDK_SINGLETON_KEY,
    ServiceSDK,
    doc_py_example=_WAIT_EXAMPLE,
    arg_docstrings={
        "name": "Name of the service.",
        "state": "The state to wait for the service to reach.",
        "timeout_s": "Timeout to wait for the service to reach the target state.",
    },
)
def wait(
    name: str,
    *,
    state: Union[str, ServiceState] = ServiceState.RUNNING,
    timeout_s: float = 600,
    _sdk: ServiceSDK,
    _interval_s: float = 5,
):
    """Wait for a service to reach a target state."""
    _sdk.wait(
        name=name,
        state=ServiceState(state),
        timeout_s=timeout_s,
        interval_s=_interval_s,
    )
