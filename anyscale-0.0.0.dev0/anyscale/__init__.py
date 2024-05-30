import inspect
import logging
import os
from sys import path
from typing import Any, Dict, List

from anyscale import version


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(os.environ.get("ANYSCALE_LOGLEVEL", "WARN"))

anyscale_dir = os.path.dirname(os.path.abspath(__file__))
path.append(os.path.join(anyscale_dir, "client"))
path.append(os.path.join(anyscale_dir, "sdk"))

from anyscale import compute_config, image, integrations, job, service
from anyscale.cluster import get_job_submission_client_cluster_info
from anyscale.cluster_compute import get_cluster_compute_from_name
from anyscale.connect import ClientBuilder
from anyscale.sdk.anyscale_client.sdk import AnyscaleSDK


# Note: indentation here matches that of connect.py::ClientBuilder.
BUILDER_HELP_FOOTER = """
        See ``anyscale.ClientBuilder`` for full documentation of
        this experimental feature."""

# Auto-add all Anyscale connect builder functions to the top-level.
for attr, _ in inspect.getmembers(ClientBuilder, inspect.isfunction):
    if attr.startswith("_"):
        continue

    def _new_builder(attr: str) -> Any:
        target = getattr(ClientBuilder, attr)

        def new_session_builder(*a: List[Any], **kw: Dict[str, Any]) -> Any:
            builder = ClientBuilder()
            return target(builder, *a, **kw)

        new_session_builder.__name__ = attr
        new_session_builder.__doc__ = target.__doc__ + BUILDER_HELP_FOOTER
        new_session_builder.__signature__ = inspect.signature(target)  # type: ignore

        return new_session_builder

    globals()[attr] = _new_builder(attr)

__version__ = version.__version__

ANYSCALE_ENV = os.environ.copy()

import os
from typing import Any, Optional

import anyscale
from anyscale._private.anyscale_client import AnyscaleClient
from anyscale.authenticate import AuthenticationBlock
from anyscale.compute_config._private.compute_config_sdk import (
    ComputeConfigSDK as PrivateComputeConfigSDK,
)
from anyscale.job._private.job_sdk import JobSDK as PrivateJobSDK
from anyscale.service._private.service_sdk import ServiceSDK as PrivateServiceSDK


class ComputeConfigSDK:
    def __init__(self, *, client: AnyscaleClient):
        self._private_sdk = PrivateComputeConfigSDK(client=client)

    def create(self, *args, **kwargs) -> Any:
        return anyscale.compute_config.create(*args, _sdk=self._private_sdk, **kwargs)

    def get(self, *args, **kwargs) -> Any:
        return anyscale.compute_config.get(*args, _sdk=self._private_sdk, **kwargs)

    def archive(self, *args, **kwargs) -> Any:
        return anyscale.compute_config.archive(*args, _sdk=self._private_sdk, **kwargs)


class JobSDK:
    def __init__(self, *, client: AnyscaleClient):
        self._private_sdk = PrivateJobSDK(client=client)

    def submit(self, *args, **kwargs) -> Any:
        return anyscale.job.submit(*args, _sdk=self._private_sdk, **kwargs)

    def status(self, *args, **kwargs) -> Any:
        return anyscale.job.status(*args, _sdk=self._private_sdk, **kwargs)

    def terminate(self, *args, **kwargs) -> Any:
        return anyscale.job.terminate(*args, _sdk=self._private_sdk, **kwargs)

    def archive(self, *args, **kwargs) -> Any:
        return anyscale.job.archive(*args, _sdk=self._private_sdk, **kwargs)

    def wait(self, *args, **kwargs) -> Any:
        return anyscale.job.wait(*args, _sdk=self._private_sdk, **kwargs)

    def logs(self, *args, **kwargs) -> Any:
        return anyscale.job.logs(*args, _sdk=self._private_sdk, **kwargs)


class ServiceSDK:
    def __init__(self, *, client: AnyscaleClient):
        self._private_sdk = PrivateServiceSDK(client=client)

    def deploy(self, *args, **kwargs) -> Any:
        return anyscale.service.deploy(*args, _sdk=self._private_sdk, **kwargs)

    def rollback(self, *args, **kwargs) -> Any:
        return anyscale.service.rollback(*args, _sdk=self._private_sdk, **kwargs)

    def terminate(self, *args, **kwargs) -> Any:
        return anyscale.service.terminate(*args, _sdk=self._private_sdk, **kwargs)

    def wait(self, *args, **kwargs) -> Any:
        return anyscale.service.wait(*args, _sdk=self._private_sdk, **kwargs)
    
    def status(self, *args, **kwargs) -> Any:
        return anyscale.service.status(*args, _sdk=self._private_sdk, **kwargs)


class Anyscale:
    def __init__(
        self, *, auth_token: Optional[str] = None, _host: Optional[str] = None,
    ):
        auth_block = AuthenticationBlock(
            cli_token=auth_token, host=_host, raise_structured_exception=True,
        )
        self._anyscale_client = AnyscaleClient(
            api_clients=(auth_block.anyscale_api_client, auth_block.api_client),
            host=_host,
        )
        self._job_sdk = JobSDK(client=self._anyscale_client)
        self._service_sdk = ServiceSDK(client=self._anyscale_client)
        self._compute_config_sdk = ComputeConfigSDK(client=self._anyscale_client)

    @property
    def job(self) -> JobSDK:  # noqa: F811
        return self._job_sdk

    @property
    def service(self) -> ServiceSDK:  # noqa: F811
        return self._service_sdk

    @property
    def compute_config(self) -> ComputeConfigSDK:  # noqa: F811
        return self._compute_config_sdk
