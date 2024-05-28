from typing import Optional

from anyscale._private.sdk import sdk_command
from anyscale.compute_config._private.compute_config_sdk import ComputeConfigSDK
from anyscale.compute_config.models import ComputeConfig, ComputeConfigVersion


_COMPUTE_CONFIG_SDK_SINGLETON_KEY = "compute_config_sdk"

_CREATE_EXAMPLE = """
import anyscale
from anyscale.compute_config.models import ComputeConfig, HeadNodeConfig, MarketType, WorkerNodeGroupConfig

config = ComputeConfig(
    head_node=HeadNodeConfig(
        instance_type="m5.8xlarge",
    ),
    worker_nodes=[
        WorkerNodeGroupConfig(
            instance_type="m5.8xlarge",
            min_nodes=5,
            max_nodes=5,
        ),
        WorkerNodeGroupConfig(
            instance_type="m5.4xlarge",
            min_nodes=1,
            max_nodes=10,
            market_type=MarketType.SPOT,
        ),
    ],
)
full_name: str = anyscale.compute_config.create(config, name="my-compute-config")
"""


@sdk_command(
    _COMPUTE_CONFIG_SDK_SINGLETON_KEY,
    ComputeConfigSDK,
    doc_py_example=_CREATE_EXAMPLE,
    arg_docstrings={
        "config": "The config options defining the compute config.",
        "name": "The name of the compute config. This should *not* include a version tag. If a name is not provided, one will be automatically generated.",
    },
)
def create(
    config: ComputeConfig, *, name: Optional[str], _sdk: ComputeConfigSDK,
) -> str:
    """Create a new version of a compute config.

    Returns the full name of the registered compute config, including the version.
    """
    full_name, _ = _sdk.create_compute_config(config, name=name)
    return full_name


_GET_EXAMPLE = """
import anyscale
from anyscale.compute_config.models import ComputeConfig

compute_config: ComputeConfig = anyscale.compute_config.get("my-compute-config")
"""


@sdk_command(
    _COMPUTE_CONFIG_SDK_SINGLETON_KEY,
    ComputeConfigSDK,
    doc_py_example=_GET_EXAMPLE,
    arg_docstrings={
        "name": "The name of the compute config. This can inclue an optional version tag, i.e., 'name:version'. If no version tag is provided, the latest version will be returned.",
        "include_archived": "Whether to consider archived compute configs (defaults to False).",
    },
)
def get(
    name: str,
    *,
    include_archived: bool = False,
    _id: Optional[str] = None,
    _sdk: ComputeConfigSDK,
) -> ComputeConfigVersion:
    """Get the compute config with the specified name.

    The name can contain an optional version tag, i.e., 'name:version'.
    If no version is provided, the latest one will be returned.
    """
    # NOTE(edoakes): I want to avoid exposing fetching by ID in the public API,
    # but it's needed for parity with the existing CLI. Therefore I am adding it
    # as a hidden private API that can be used like: (`name="", _id=id`).
    return _sdk.get_compute_config(
        name=name or None, id=_id, include_archived=include_archived
    )


_ARCHIVE_EXAMPLE = """
import anyscale

anyscale.compute_config.archive(name="my-compute-config")
"""


@sdk_command(
    _COMPUTE_CONFIG_SDK_SINGLETON_KEY,
    ComputeConfigSDK,
    doc_py_example=_ARCHIVE_EXAMPLE,
    arg_docstrings={"name": "Name of the compute config.",},
)
def archive(name: str, *, _id: Optional[str] = None, _sdk: ComputeConfigSDK,) -> str:
    """Archive a compute config and all of its versions.

    The name can contain an optional version, e.g., 'name:version'.
    If no version is provided, the latest one will be archived.

    Once a compute config is archived, its name will no longer be usable in the organization.
    """
    # NOTE(edoakes): I want to avoid exposing fetching by ID in the public API,
    # but it's needed for parity with the existing CLI. Therefore I am adding it
    # as a hidden private API that can be used like: (`name="", _id=id`).
    return _sdk.archive_compute_config(name=name or None, id=_id)
