from abc import ABC, abstractmethod
import asyncio
import io
import logging
import os
import pathlib
import time
from typing import Any, Callable, cast, Dict, IO, List, Optional, Tuple
from urllib.parse import urlparse

import requests

from anyscale._private.anyscale_client.common import (
    AnyscaleClientInterface,
    DEFAULT_PYTHON_VERSION,
    DEFAULT_RAY_VERSION,
    RUNTIME_ENV_PACKAGE_FORMAT,
)
from anyscale._private.models.image_uri import ImageURI
from anyscale.api_utils.job_logs_util import _get_job_logs_from_storage_bucket_streaming
from anyscale.authenticate import AuthenticationBlock, get_auth_api_client
from anyscale.cli_logger import BlockLogger, LogsLogger
from anyscale.client.openapi_client.api.default_api import DefaultApi as InternalApi
from anyscale.client.openapi_client.models import (
    ArchiveStatus,
    Cloud,
    CloudDataBucketFileType,
    CloudDataBucketPresignedUploadInfo,
    CloudDataBucketPresignedUploadRequest,
    CloudNameOptions,
    ComputeTemplate,
    ComputeTemplateConfig,
    ComputeTemplateQuery,
    CreateComputeTemplate,
    CreateInternalProductionJob,
    DecoratedComputeTemplate,
    InternalProductionJob,
)
from anyscale.client.openapi_client.models.production_job import ProductionJob
from anyscale.client.openapi_client.rest import ApiException as InternalApiException
from anyscale.cluster_compute import parse_cluster_compute_name_version
from anyscale.sdk.anyscale_client.api.default_api import DefaultApi as ExternalApi
from anyscale.sdk.anyscale_client.models import (
    ApplyServiceModel,
    Cluster,
    ClusterCompute,
    ClusterComputeConfig,
    ClusterEnvironment,
    ClusterEnvironmentBuild,
    ClusterEnvironmentBuildStatus,
    Job as APIJobRun,
    Project,
    RollbackServiceModel,
    ServiceModel,
)
from anyscale.sdk.anyscale_client.models.create_cluster_environment import (
    CreateClusterEnvironment,
)
from anyscale.sdk.anyscale_client.models.create_cluster_environment_build import (
    CreateClusterEnvironmentBuild,
)
from anyscale.sdk.anyscale_client.models.jobs_query import JobsQuery
from anyscale.sdk.anyscale_client.models.jobs_sort_field import JobsSortField
from anyscale.sdk.anyscale_client.models.page_query import PageQuery
from anyscale.sdk.anyscale_client.models.sort_by_clause_jobs_sort_field import (
    SortByClauseJobsSortField,
)
from anyscale.sdk.anyscale_client.models.sort_order import SortOrder
from anyscale.sdk.anyscale_client.rest import ApiException as ExternalApiException
from anyscale.shared_anyscale_utils.conf import ANYSCALE_HOST
from anyscale.util import (
    get_cluster_model_for_current_workspace,
    get_endpoint,
    is_anyscale_workspace,
)
from anyscale.utils.connect_helpers import search_entities
from anyscale.utils.runtime_env import (
    is_workspace_dependency_tracking_disabled,
    parse_dot_env_file,
    WORKSPACE_REQUIREMENTS_FILE_PATH,
    zip_local_dir,
)
from anyscale.utils.workspace_notification import (
    WORKSPACE_NOTIFICATION_ADDRESS,
    WorkspaceNotification,
)


WORKSPACE_ID_ENV_VAR = "ANYSCALE_EXPERIMENTAL_WORKSPACE_ID"
OVERWRITE_EXISTING_CLOUD_STORAGE_FILES = (
    os.environ.get("ANYSCALE_OVERWRITE_EXISTING_CLOUD_STORAGE_FILES", "0") == "1"
)

# internal_logger is used for logging internal errors or debug messages that we do not expect users to see.
internal_logger = logging.getLogger(__name__)


class AWSS3ClientInterface(ABC):
    @abstractmethod
    def download_fileobj(self, Bucket: str, Key: str, Fileobj: IO[Any],) -> None:
        """Download a file from an S3 bucket to a file-like object."""
        raise NotImplementedError


class GCSBlobInterface(ABC):
    @abstractmethod
    def download_to_file(self, fileobj: IO[Any]) -> None:
        """Download the blob to a file-like object."""
        raise NotImplementedError

    @abstractmethod
    def exists(self) -> bool:
        """Check if the blob exists."""
        raise NotImplementedError


class GCSBucketInterface(ABC):
    @abstractmethod
    def blob(self, object_name: str) -> GCSBlobInterface:
        """Get a blob object for the given object name."""
        raise NotImplementedError


class GCPGCSClientInterface(ABC):
    @abstractmethod
    def bucket(self, bucket: str) -> GCSBucketInterface:
        """Get a bucket object for the given bucket name."""
        raise NotImplementedError


class AnyscaleClient(AnyscaleClientInterface):
    # Number of entries to fetch per request for list endpoints.
    LIST_ENDPOINT_COUNT = 50

    def __init__(
        self,
        *,
        api_clients: Optional[Tuple[ExternalApi, InternalApi]] = None,
        sleep: Optional[Callable[[float], None]] = None,
        workspace_requirements_file_path: str = WORKSPACE_REQUIREMENTS_FILE_PATH,
        logger: Optional[BlockLogger] = None,
        host: Optional[str] = None,
        s3_client: Optional[AWSS3ClientInterface] = None,
        gcs_client: Optional[GCPGCSClientInterface] = None,
    ):
        if api_clients is None:
            auth_block: AuthenticationBlock = get_auth_api_client(
                raise_structured_exception=True
            )
            api_clients = (auth_block.anyscale_api_client, auth_block.api_client)

        self._external_api_client, self._internal_api_client = api_clients
        self._workspace_requirements_file_path = workspace_requirements_file_path
        self._sleep = sleep or time.sleep
        self._s3_client = s3_client
        self._gcs_client = gcs_client

        # Cached IDs and models to avoid duplicate lookups.
        self._default_project_id_from_cloud_id: Dict[str, str] = {}
        self._cloud_id_cache: Dict[Optional[str], str] = {}
        self._current_workspace_cluster: Optional[Cluster] = None
        self._logger = logger or BlockLogger()
        self._host = host or ANYSCALE_HOST

    @property
    def s3_client(self) -> AWSS3ClientInterface:
        if self._s3_client is None:
            # initialize the s3 client lazily so that we import the boto3 library only when needed.
            try:
                import boto3
                import botocore.config
            except ImportError:
                raise RuntimeError(
                    "Could not import the Amazon S3 Python API via `import boto3`.  Please check your installation or try running `pip install boto3`."
                )
            self._s3_client = boto3.client(  # type: ignore
                "s3", config=botocore.config.Config(signature_version="s3v4")
            )
        return self._s3_client  # type: ignore

    @property
    def gcs_client(self) -> GCPGCSClientInterface:
        if self._gcs_client is None:
            # initialize the gcs client lazily so that we import the google cloud storage library only when needed.
            try:
                from google.cloud import storage
            except ImportError:
                raise RuntimeError(
                    "Could not import the Google Storage Python API via `from google.cloud import storage`.  Please check your installation or try running `pip install --upgrade google-cloud-storage`."
                )
            self._gcs_client = storage.Client()
        return self._gcs_client  # type: ignore

    @property
    def host(self) -> str:
        return self._host

    @property
    def logger(self) -> BlockLogger:
        return self._logger

    def get_job_ui_url(self, job_id: str) -> str:
        return get_endpoint(f"/jobs/{job_id}", host=self.host)

    def get_service_ui_url(self, service_id: str) -> str:
        return get_endpoint(f"/services/{service_id}", host=self.host)

    def get_compute_config_ui_url(
        self, compute_config_id: str, *, cloud_id: str
    ) -> str:
        return get_endpoint(
            f"/v2/{cloud_id}/compute-configs/{compute_config_id}", host=self.host
        )

    def get_build_ui_url(self, cluster_env_id, build_id: str) -> str:
        return get_endpoint(
            f"v2/container-images/{cluster_env_id}/versions/{build_id}", host=self.host
        )

    def get_current_workspace_id(self) -> Optional[str]:
        return os.environ.get(WORKSPACE_ID_ENV_VAR, None)

    def inside_workspace(self) -> bool:
        return self.get_current_workspace_id() is not None

    def get_workspace_requirements_path(self) -> Optional[str]:
        if (
            not self.inside_workspace()
            or is_workspace_dependency_tracking_disabled()
            or not pathlib.Path(self._workspace_requirements_file_path).is_file()
        ):
            return None

        return self._workspace_requirements_file_path

    def _download_file_from_google_cloud_storage(
        self, bucket: str, object_name: str
    ) -> Optional[bytes]:
        try:
            bucket_obj = self.gcs_client.bucket(bucket)
            blob = bucket_obj.blob(object_name)
            fileobj = io.BytesIO()
            if blob.exists():
                blob.download_to_file(fileobj)
                return fileobj.getvalue()
            return None
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(
                f"Failed to download the working directory from Google Cloud Storage. Error {e!r}"
                "Please validate you have exported cloud credentials with the correct read permissions and the intended bucket exists in your Cloud Storage account. "
            ) from e

    def _download_file_from_s3(self, bucket: str, object_key: str) -> Optional[bytes]:
        try:
            from botocore.exceptions import ClientError
        except Exception:  # noqa: BLE001
            raise RuntimeError(
                "Could not download file from S3: Could not import the Amazon S3 Python API via `import boto3`.  Please check your installation or try running `pip install boto3`."
            )
        try:
            fileobj = io.BytesIO()
            self.s3_client.download_fileobj(bucket, object_key, fileobj)
            return fileobj.getvalue()
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return None
            raise
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(
                f"Failed to download the working directory from S3. Error {e!r}"
                "Please validate you have exported cloud credentials with the correct read permissions and the intended bucket exists in your S3 account. "
            ) from e

    def _download_file_from_remote_storage(self, remote_uri: str) -> Optional[bytes]:
        parsed_uri = urlparse(remote_uri)
        service = parsed_uri.scheme
        bucket = parsed_uri.netloc
        object_name = parsed_uri.path.lstrip("/")
        if service == "s3":
            return self._download_file_from_s3(bucket, object_name)
        if service == "gs":
            return self._download_file_from_google_cloud_storage(bucket, object_name)
        return None

    def get_workspace_env_vars(self) -> Optional[Dict[str, str]]:
        system_storage_path = os.environ.get("ANYSCALE_INTERNAL_SYSTEM_STORAGE", "")
        workspace_id = os.environ.get("ANYSCALE_EXPERIMENTAL_WORKSPACE_ID", "")
        workspace_artifact_path = (
            os.path.join(
                system_storage_path, "workspace_tracking_dependencies", workspace_id,
            )
            if workspace_id and system_storage_path
            else ""
        )
        workspace_dot_env_path = (
            os.path.join(workspace_artifact_path, ".env")
            if workspace_artifact_path
            else ""
        )

        if not self.inside_workspace() or not workspace_dot_env_path:
            return None

        dot_env = self._download_file_from_remote_storage(workspace_dot_env_path)
        if dot_env:
            parsed_dot_env = parse_dot_env_file(dot_env)
            if parsed_dot_env:
                self.logger.info(
                    f"Using workspace runtime dependencies env vars: {parsed_dot_env}."
                )
            return parsed_dot_env
        return None

    def get_current_workspace_cluster(self) -> Optional[Cluster]:
        # Checks for the existence of the ANYSCALE_EXPERIMENTAL_WORKSPACE_ID env var.
        if not is_anyscale_workspace():
            return None

        if self._current_workspace_cluster is None:
            # Picks up the cluster ID from the ANYSCALE_SESSION_ID env var.
            self._current_workspace_cluster = get_cluster_model_for_current_workspace(
                self._external_api_client
            )

        return self._current_workspace_cluster

    def get_project_id(self, parent_cloud_id: str) -> str:
        workspace_cluster = self.get_current_workspace_cluster()
        if workspace_cluster is not None:
            return workspace_cluster.project_id

        if self._default_project_id_from_cloud_id.get(parent_cloud_id) is None:
            # Cloud isolation organizations follow the permissions model in https://docs.anyscale.com/organization-and-user-account/access-controls
            # TODO(nikita): Remove this FF check after completing the cloud isolation migration in Q2 2024
            cloud_isolation_ff_on = self._internal_api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get(
                "cloud-isolation-phase-1"
            ).result.is_on
            default_project: Project = self._external_api_client.get_default_project(
                parent_cloud_id=(parent_cloud_id if cloud_isolation_ff_on else None)
            ).result
            self._default_project_id_from_cloud_id[parent_cloud_id] = default_project.id

        return self._default_project_id_from_cloud_id[parent_cloud_id]

    def _get_cloud_id_for_compute_config_id(self, compute_config_id: str) -> str:
        cluster_compute: ClusterCompute = self._external_api_client.get_cluster_compute(
            compute_config_id
        ).result
        cluster_compute_config: ClusterComputeConfig = cluster_compute.config
        return cluster_compute_config.cloud_id

    def _get_cloud_id_by_name(self, cloud_name: str) -> Optional[str]:
        try:
            return self._internal_api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post(
                CloudNameOptions(name=cloud_name),
            ).result.id
        except InternalApiException as e:
            if e.status == 404:
                return None

            raise e from None

    def get_cloud_id(
        self, cloud_name: Optional[str] = None, compute_config_id: Optional[str] = None
    ) -> str:
        if cloud_name is not None and compute_config_id is not None:
            raise ValueError(
                "Only one of cloud_name or compute_config_id should be provided."
            )

        if compute_config_id is not None:
            return self._get_cloud_id_for_compute_config_id(compute_config_id)

        if cloud_name in self._cloud_id_cache:
            return self._cloud_id_cache[cloud_name]

        if cloud_name is not None:
            cloud_id = self._get_cloud_id_by_name(cloud_name)
            if cloud_id is None:
                raise RuntimeError(f"Cloud '{cloud_name}' not found.")
        elif self.inside_workspace():
            workspace_cluster = self.get_current_workspace_cluster()
            assert workspace_cluster is not None
            # NOTE(edoakes): the Cluster model has a compute_config_config model that includes
            # its cloud ID, but it's not always populated.
            # TODO(edoakes): add cloud_id to the Cluster model to avoid a second RTT.
            cloud_id = self._get_cloud_id_for_compute_config_id(
                workspace_cluster.cluster_compute_id
            )
        else:
            cloud_id = self._external_api_client.get_default_cloud().result.id

        assert cloud_id is not None
        self._cloud_id_cache[cloud_name] = cloud_id
        return cloud_id

    def get_cloud(self, *, cloud_id: str) -> Optional[Cloud]:
        try:
            cloud: Cloud = self._internal_api_client.get_cloud_api_v2_clouds_cloud_id_get(
                cloud_id
            ).result
            return cloud
        except InternalApiException as e:
            if e.status == 404:
                return None

            raise e from None

    def create_compute_config(
        self, config: ComputeTemplateConfig, *, name: Optional[str] = None
    ) -> Tuple[str, str]:
        result: ComputeTemplate = self._internal_api_client.create_compute_template_api_v2_compute_templates_post(
            create_compute_template=CreateComputeTemplate(
                config=config, name=name, anonymous=name is None, new_version=True
            )
        ).result
        return f"{result.name}:{result.version}", result.id

    def get_compute_config(
        self, compute_config_id: str
    ) -> Optional[DecoratedComputeTemplate]:
        try:
            return self._internal_api_client.get_compute_template_api_v2_compute_templates_template_id_get(
                compute_config_id
            ).result
        except InternalApiException as e:
            if e.status == 404:
                return None

            raise e from None

    def get_compute_config_id(
        self,
        compute_config_name: Optional[str] = None,
        *,
        include_archived: bool = False,
    ) -> Optional[str]:
        if compute_config_name is not None:
            name, version = parse_cluster_compute_name_version(compute_config_name)
            if version is None:
                # Setting `version=-1` will return only the latest version if there are multiple.
                version = -1
            cluster_computes = self._internal_api_client.search_compute_templates_api_v2_compute_templates_search_post(
                ComputeTemplateQuery(
                    orgwide=True,
                    name={"equals": name},
                    include_anonymous=True,
                    archive_status=ArchiveStatus.ALL
                    if include_archived
                    else ArchiveStatus.NOT_ARCHIVED,
                    version=version,
                )
            ).results

            if len(cluster_computes) == 0:
                return None

            compute_template: DecoratedComputeTemplate = cluster_computes[0]
            return compute_template.id

        # If the compute config name is not provided, we pick an appropriate default.
        #
        #   - If running in a workspace:
        #       * If auto_select_worker_config enabled: we switch over to a standardized
        #         default compute config (copying over any cluster-level attributes, e.g.
        #         max-gpus).
        #       * Otherwise, we use the workspace's compute config.
        #
        #   - Otherwise, we use the default compute config provided by the API.

        workspace_cluster = self.get_current_workspace_cluster()
        if workspace_cluster is not None:
            workspace_compute_config: DecoratedComputeTemplate = self.get_compute_config(
                workspace_cluster.cluster_compute_id
            )
            workspace_config: ClusterComputeConfig = workspace_compute_config.config
            if workspace_config.auto_select_worker_config:
                standard_template = self._build_standard_compute_template_from_existing_auto_config(
                    workspace_config
                )
                _, compute_config_id = self.create_compute_config(standard_template)
                return compute_config_id
            else:
                return workspace_cluster.cluster_compute_id

        return self.get_default_compute_config(cloud_id=self.get_cloud_id()).id

    def archive_compute_config(self, *, compute_config_id):
        self._internal_api_client.archive_compute_template_api_v2_compute_templates_compute_template_id_archive_post(
            compute_config_id
        )

    def get_default_compute_config(self, *, cloud_id: str) -> ClusterCompute:
        return self._external_api_client.get_default_cluster_compute(
            cloud_id=cloud_id,
        ).result

    def _build_standard_compute_template_from_existing_auto_config(
        self, compute_config: ClusterComputeConfig
    ) -> ComputeTemplateConfig:
        """
        Build a standard compute template config from an existing compute config.

        1. Pull the default compute template config.
        2. Disable scheduling on the head node.
        3. Enable auto_select_worker_config.
        4. Copy any cluster-level flags from the provided compute config to the template.
        """
        # Retrieve the default cluster compute config for the cloud.
        default_compute_template: DecoratedComputeTemplate = self._external_api_client.get_default_cluster_compute(
            cloud_id=compute_config.cloud_id,
        ).result.config

        # Disable head node scheduling.
        if default_compute_template.head_node_type.resources is None:
            default_compute_template.head_node_type.resources = {}
        default_compute_template.head_node_type.resources["CPU"] = 0

        # Ensure auto_select_worker_config is enabled.
        default_compute_template.auto_select_worker_config = True

        # Copy flags set at a cluster level over to the workspace.
        #
        # NOTE (shomilj): If there are more attributes we want to
        # persist from the provided compute config --> the compute
        # config used for deploying the service, we should copy them
        # over here.
        default_compute_template.flags = compute_config.flags

        return default_compute_template

    def get_cluster_env_build(self, build_id: str) -> Optional[ClusterEnvironmentBuild]:
        return self._external_api_client.get_cluster_environment_build(build_id).result

    def get_cluster_env_build_image_uri(
        self, cluster_env_build_id: str
    ) -> Optional[ImageURI]:
        try:
            build: ClusterEnvironmentBuild = self._external_api_client.get_cluster_environment_build(
                cluster_env_build_id
            ).result
            cluster_env = self._external_api_client.get_cluster_environment(
                build.cluster_environment_id
            ).result
            return ImageURI.from_cluster_env_build(cluster_env, build)
        except ExternalApiException as e:
            if e.status == 404:
                return None

            raise e from None

    def get_default_build_id(self) -> str:
        workspace_cluster = self.get_current_workspace_cluster()
        if workspace_cluster is not None:
            return workspace_cluster.cluster_environment_build_id
        result: ClusterEnvironmentBuild = self._external_api_client.get_default_cluster_environment_build(
            DEFAULT_PYTHON_VERSION, DEFAULT_RAY_VERSION,
        ).result
        return result.id

    def _get_cluster_env_by_name(self, name: str) -> Optional[ClusterEnvironment]:
        cluster_envs = self._external_api_client.search_cluster_environments(
            {
                "name": {"equals": name},
                "paging": {"count": 1},
                "include_anonymous": True,
            }
        ).results
        return cluster_envs[0] if cluster_envs else None

    def _wait_for_build_to_succeed(
        self, build_id: str, poll_interval_seconds=3, timeout_secs=3600,
    ):
        """Periodically check the status of the build operation until it completes.
        Raise a RuntimeError if the build fails or cancelled.
        Raise a TimeoutError if the build does not complete within the timeout.
        """
        elapsed_secs = 0
        while elapsed_secs < timeout_secs:
            build = self._external_api_client.get_cluster_environment_build(
                build_id
            ).result
            if build.status == ClusterEnvironmentBuildStatus.SUCCEEDED:
                self.logger.info("")
                return
            elif build.status == ClusterEnvironmentBuildStatus.FAILED:
                raise RuntimeError(f"Image build {build_id} failed.")
            elif build.status == ClusterEnvironmentBuildStatus.CANCELED:
                raise RuntimeError(f"Image build {build_id} unexpectedly cancelled.")

            elapsed_secs += poll_interval_seconds
            self.logger.info(
                f"Waiting for image build to complete. Elapsed time: {elapsed_secs} seconds.",
                end="\r",
            )
            self._sleep(poll_interval_seconds)
        raise TimeoutError(
            f"Timed out waiting for image build {build_id} to complete after {timeout_secs}s."
        )

    def _find_or_create_cluster_env(
        self, cluster_env_name: str, anonymous: bool
    ) -> ClusterEnvironment:
        existing_cluster_env = self._get_cluster_env_by_name(cluster_env_name)
        if existing_cluster_env is not None:
            return existing_cluster_env

        # this creates a cluster env only and it does not trigger a build to avoid the race condition
        # when creating a cluster environment and a build at the same time and then list builds for the cluster environment later.
        # ```
        #     cluster_env == self._external_api_client.create_cluster_environment(..., image_uri=image_uri)
        #     build == self._external_api_client.create_cluster_environment_build(..., cluster_env_id=cluster_env.id)
        # ```
        # The race condition can happen if another build for the same cluster envrionment is created between the two calls.
        cluster_environment = self._external_api_client.create_cluster_environment(
            CreateClusterEnvironment(name=cluster_env_name, anonymous=anonymous)
        ).result
        return cluster_environment

    def get_cluster_env_build_id_from_containerfile(
        self, cluster_env_name: str, containerfile: str, anonymous: bool = True
    ) -> str:
        cluster_env = self._find_or_create_cluster_env(
            cluster_env_name, anonymous=anonymous
        )
        cluster_env_builds = self._external_api_client.list_cluster_environment_builds(
            cluster_environment_id=cluster_env.id, count=self.LIST_ENDPOINT_COUNT
        ).results
        for build in cluster_env_builds:
            if (
                build.status == ClusterEnvironmentBuildStatus.SUCCEEDED
                and build.containerfile == containerfile
            ):
                return build.id

        build_op = self._external_api_client.create_cluster_environment_build(
            CreateClusterEnvironmentBuild(
                cluster_environment_id=cluster_env.id, containerfile=containerfile,
            )
        ).result

        build_url = self.get_build_ui_url(
            cluster_env.id, build_op.cluster_environment_build_id
        )
        self.logger.info(f"Building image... See details: {build_url}.")
        self._wait_for_build_to_succeed(build_op.cluster_environment_build_id)
        self.logger.info("Image build succeeded.")

        return build_op.cluster_environment_build_id

    def get_cluster_env_build_id_from_image_uri(self, image_uri: ImageURI) -> str:
        if image_uri.is_cluster_env_image():
            identifier = image_uri.to_cluster_env_identifier()
            try:
                build = self._external_api_client.find_cluster_environment_build_by_identifier(
                    identifier=identifier
                ).result
                if build.status == ClusterEnvironmentBuildStatus.SUCCEEDED:
                    return build.id
                else:
                    raise RuntimeError(
                        f"Legacy cluster environment build '{identifier}' is not a successful build."
                    )
            except ExternalApiException as e:
                if e.status == 404:
                    raise RuntimeError(
                        f"Legacy cluster environment '{identifier}' is not found."
                    )

        cluster_env_name = image_uri.to_cluster_env_name()
        cluster_env = self._find_or_create_cluster_env(cluster_env_name, anonymous=True)
        image_uri_str = str(image_uri)

        # since we encode the image_uri into the cluster env name, there should exist one and only one build that matches the image_uri.
        cluster_env_builds = self._external_api_client.list_cluster_environment_builds(
            cluster_environment_id=cluster_env.id, count=1
        ).results
        build = cluster_env_builds[0] if cluster_env_builds else None
        if (
            build is not None
            and build.docker_image_name == image_uri_str
            and build.status == ClusterEnvironmentBuildStatus.SUCCEEDED
        ):
            return build.id

        # Still create a new build if the cluster env already exists but the build does not match the image_uri.
        result = self._external_api_client.create_cluster_environment_build(
            CreateClusterEnvironmentBuild(
                # For historical reasons, we have to use docker_image_name instead of image_uri; but it is just a URI to the image.
                cluster_environment_id=cluster_env.id,
                docker_image_name=image_uri_str,
            )
        ).result

        assert result.completed
        return result.cluster_environment_build_id

    def send_workspace_notification(
        self, notification: WorkspaceNotification,
    ):
        if not self.inside_workspace():
            return

        try:
            r = requests.post(WORKSPACE_NOTIFICATION_ADDRESS, json=notification.dict())
            r.raise_for_status()
        except Exception:
            internal_logger.exception(
                "Failed to send workspace notification. "
                "This should not happen, so please contact Anyscale support."
            )

    def get_service(self, name: str) -> Optional[ServiceModel]:
        # TODO(edoakes): this endpoint is very slow and there's no reason we should need
        # to use this complex list endpoint just to fetch a service by name.
        paging_token = None
        cloud_id = self.get_cloud_id()
        project_id = self.get_project_id(parent_cloud_id=cloud_id)
        service: Optional[ServiceModel] = None
        while True:
            resp = self._external_api_client.list_services(
                project_id=project_id,
                name=name,
                count=self.LIST_ENDPOINT_COUNT,
                paging_token=paging_token,
            )
            for result in resp.results:
                if result.name == name:
                    service = result
                    break

            paging_token = resp.metadata.next_paging_token
            if service is not None or paging_token is None:
                break

        return service

    def get_job(
        self, name: Optional[str], job_id: Optional[str]
    ) -> Optional[ProductionJob]:
        if job_id is not None:
            try:
                return self._external_api_client.get_production_job(job_id).result
            except ExternalApiException as e:
                if e.status == 404:
                    return None
                raise e from None
        else:
            paging_token = None
            cloud_id = self.get_cloud_id()
            project_id = self.get_project_id(parent_cloud_id=cloud_id)
            result: Optional[ProductionJob] = None
            while True:
                resp = self._external_api_client.list_production_jobs(
                    project_id=project_id,
                    name=name,
                    count=self.LIST_ENDPOINT_COUNT,
                    paging_token=paging_token,
                )
                for job in resp.results:
                    if (
                        job is not None
                        and job.name == name
                        and (result is None or job.created_at > result.created_at)
                    ):
                        result = job

                paging_token = resp.metadata.next_paging_token
                if paging_token is None:
                    break

            return result

    def get_job_runs(self, job_id: str) -> List[APIJobRun]:
        job_runs: List[APIJobRun] = search_entities(
            self._external_api_client.search_jobs,
            JobsQuery(
                ha_job_id=job_id,
                show_ray_client_runs_only=False,
                sort_by_clauses=[
                    SortByClauseJobsSortField(
                        sort_field=JobsSortField.CREATED_AT, sort_order=SortOrder.ASC,
                    )
                ],
                paging=PageQuery(),
            ),
        )
        return job_runs

    def rollout_service(self, model: ApplyServiceModel) -> ServiceModel:
        result: ServiceModel = self._external_api_client.rollout_service(model).result
        return result

    def rollback_service(
        self, service_id: str, *, max_surge_percent: Optional[int] = None
    ) -> ServiceModel:
        result: ServiceModel = self._external_api_client.rollback_service(
            service_id,
            rollback_service_model=RollbackServiceModel(
                max_surge_percent=max_surge_percent
            ),
        )
        return result

    def terminate_service(self, service_id: str) -> ServiceModel:
        result: ServiceModel = self._external_api_client.terminate_service(service_id)
        return result

    def submit_job(self, model: CreateInternalProductionJob) -> InternalProductionJob:
        job: InternalProductionJob = self._internal_api_client.create_job_api_v2_decorated_ha_jobs_create_post(
            model,
        ).result
        return job

    def terminate_job(self, job_id: str):
        self._external_api_client.terminate_job(job_id)

    def archive_job(self, job_id: str):
        self._internal_api_client.archive_job_api_v2_decorated_ha_jobs_production_job_id_archive_post(
            job_id
        )

    def upload_local_dir_to_cloud_storage(
        self,
        local_dir: str,
        *,
        cloud_id: str,
        excludes: Optional[List[str]] = None,
        overwrite_existing_file: bool = OVERWRITE_EXISTING_CLOUD_STORAGE_FILES,
    ) -> str:
        if not pathlib.Path(local_dir).is_dir():
            raise RuntimeError(f"Path '{local_dir}' is not a valid directory.")

        with zip_local_dir(local_dir, excludes=excludes) as (
            _,
            zip_file_bytes,
            content_hash,
        ):
            file_name = RUNTIME_ENV_PACKAGE_FORMAT.format(content_hash=content_hash)
            request = CloudDataBucketPresignedUploadRequest(
                file_type=CloudDataBucketFileType.RUNTIME_ENV_PACKAGES,
                file_name=file_name,
            )
            info: CloudDataBucketPresignedUploadInfo = self._internal_api_client.generate_cloud_data_bucket_presigned_upload_url_api_v2_clouds_cloud_id_generate_cloud_data_bucket_presigned_upload_url_post(
                cloud_id, request
            ).result

            # Skip the upload entirely if the zip file already exists.
            if not info.file_exists or overwrite_existing_file:
                internal_logger.debug(f"Uploading file '{file_name}' to cloud storage.")
                requests.put(info.upload_url, data=zip_file_bytes).raise_for_status()
            else:
                internal_logger.debug(
                    f"Skipping file upload for '{file_name}' because it already exists in cloud storage."
                )

        return info.file_uri

    def logs_for_job_run(
        self, job_run_id: str, follow: bool = False  # noqa: ARG002
    ) -> str:
        """Retrieves logs from the streaming job logs folder in S3/GCS"""
        logs = ""
        next_page_token = None
        cluster_journal_events_start_line = 0
        # Keep track of if any logs have been printed yet,
        # If not, we assume the cluster recently launched and we
        # give more leeway for the logs to be available.
        self.logger.info("Retrieving logs...")
        (
            logs,
            next_page_token,
            cluster_journal_events_start_line,
            job_finished,
        ) = asyncio.run(
            _get_job_logs_from_storage_bucket_streaming(
                self._internal_api_client,
                cast(
                    LogsLogger, self.logger
                ),  # self.logger is a BlockLogger, cast to LogsLogger subclass
                job_run_id=job_run_id,
                remove_escape_chars=False,
                next_page_token=next_page_token,
                cluster_journal_events_start_line=cluster_journal_events_start_line,
                no_cluster_journal_events=True,
            )
        )

        # if len(logs):
        #     have_jobs_started_producing_logs = True

        # Continuously poll for logs.
        # terminal_state_count = 0
        # while follow:
        #     start = time.monotonic()
        #     if job_finished:
        #         # Let's wait before terminating the loop to give the logs a chance to catch up.
        #         terminal_state_count += 1
        #         # Once jobs produce logs, we know we do not have to wait as long for those logs
        #         # to be uploaded to S3 since the cluster is already running.
        #         max_iterations = 4 if have_jobs_started_producing_logs else 6
        #         if terminal_state_count >= max_iterations:
        #             self.logger.info("Job run reached terminal state.")
        #             return logs

        #     (
        #         additional_logs,
        #         next_page_token,
        #         cluster_journal_events_start_line,
        #         job_finished,
        #     ) = asyncio.run(
        #         _get_job_logs_from_storage_bucket_streaming(
        #             self._internal_api_client,
        #             cast(
        #                 LogsLogger, self.logger
        #             ),  # self.logger is a BlockLogger, cast to LogsLogger subclass
        #             job_run_id=job_run_id,
        #             remove_escape_chars=False,
        #             next_page_token=next_page_token,
        #             cluster_journal_events_start_line=cluster_journal_events_start_line,
        #             no_cluster_journal_events=True,
        #         )
        #     )

        #     logs += additional_logs

        #     # Wait at least 5 seconds between iterations.
        #     time.sleep(max(0, 5 - (time.monotonic() - start)))

        return logs
