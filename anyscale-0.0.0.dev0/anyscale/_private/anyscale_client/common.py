from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from anyscale._private.models.image_uri import ImageURI
from anyscale.client.openapi_client.models import (
    Cloud,
    ComputeTemplateConfig,
    CreateInternalProductionJob,
    DecoratedComputeTemplate,
    InternalProductionJob,
)
from anyscale.client.openapi_client.models.production_job import ProductionJob
from anyscale.sdk.anyscale_client.models import (
    ApplyServiceModel,
    Cluster,
    ClusterCompute,
    Job as APIJobRun,
    ServiceModel,
)
from anyscale.sdk.anyscale_client.models.cluster_environment_build import (
    ClusterEnvironmentBuild,
)
from anyscale.utils.workspace_notification import WorkspaceNotification


# TODO(edoakes): figure out a sane policy for this.
# Maybe just make it part of the release process to update it, or fetch the
# default builds and get the latest one. The best thing to do is probably
# to populate this in the backend.
DEFAULT_RAY_VERSION = "2.10.0"
DEFAULT_PYTHON_VERSION = "py310"
RUNTIME_ENV_PACKAGE_FORMAT = "pkg_{content_hash}.zip"

# All workspace cluster names should start with this prefix.
WORKSPACE_CLUSTER_NAME_PREFIX = "workspace-cluster-"


class AnyscaleClientInterface(ABC):
    @abstractmethod
    def get_job_ui_url(self, job_id: str) -> str:
        """Get a URL to the webpage for a job."""
        raise NotImplementedError

    @abstractmethod
    def get_service_ui_url(self, service_id: str) -> str:
        """Get a URL to the webpage for a service."""
        raise NotImplementedError

    @abstractmethod
    def get_compute_config_ui_url(
        self, compute_config_id: str, *, cloud_id: str
    ) -> str:
        """Get a URL to the webpage for a compute config."""
        raise NotImplementedError

    @abstractmethod
    def get_current_workspace_id(self) -> Optional[str]:
        """Returns the ID of the workspace this is running in (or `None`)."""
        raise NotImplementedError

    @abstractmethod
    def inside_workspace(self) -> bool:
        """Returns true if this code is running inside a workspace."""
        raise NotImplementedError

    @abstractmethod
    def get_workspace_requirements_path(self) -> Optional[str]:
        """Returns the path to the workspace-managed requirements file.

        Returns None if dependency tracking is disable or the file does not exist or is not in a workspace.
        """
        raise NotImplementedError

    @abstractmethod
    def get_workspace_env_vars(self) -> Optional[Dict[str, str]]:
        """Returns the environment variables specified in workspace runtime dependencies."""
        raise NotImplementedError

    @abstractmethod
    def get_current_workspace_cluster(self) -> Optional[Cluster]:
        """Get the cluster model for the workspace this code is running in.

        Returns None if not running in a workspace.
        """
        raise NotImplementedError

    def send_workspace_notification(self, notification: WorkspaceNotification):
        """Send a workspace notification to be displayed to the user.

        This is a no-op if called from outside a workspace.
        """
        raise NotImplementedError

    @abstractmethod
    def get_project_id(self, parent_cloud_id: str) -> str:
        """Get the default project ID for this user.

        If running in a workspace, returns the workspace project ID.
        """
        raise NotImplementedError

    @abstractmethod
    def get_cloud_id(
        self, *, cloud_name: Optional[str] = None, compute_config_id: Optional[str]
    ) -> str:
        """Get the cloud ID for the provided cloud name or compute config ID.

        If both arguments are None:
            - if running in a workspace, get the workspace's cloud ID.
            - else, get the user's default cloud ID.
        """
        raise NotImplementedError

    @abstractmethod
    def get_cloud(self, *, cloud_id: str) -> Optional[Cloud]:
        """Get the cloud model for the provided cloud ID.

        Returns `None` if the cloud ID was not found.
        """
        raise NotImplementedError

    @abstractmethod
    def create_compute_config(
        self, config: ComputeTemplateConfig, *, name: Optional[str] = None
    ) -> Tuple[str, str]:
        """Create a compute config and return its ID.

        If a name is not provided, the compute config will be "anonymous."

        Returns (name, ID).
        """
        raise NotImplementedError

    @abstractmethod
    def get_compute_config_id(
        self, compute_config_name: Optional[str] = None, *, include_archived=False
    ) -> Optional[str]:
        """Get the compute config ID for the provided name.

        If compute_config_name is None:
            - if running in a workspace, get the workspace's compute config ID.
            - else, get the user's default compute config ID.

        Returns None if the compute config name does not exist.
        """
        raise NotImplementedError

    @abstractmethod
    def get_compute_config(
        self, compute_config_id: str
    ) -> Optional[DecoratedComputeTemplate]:
        """Get the compute config for the provided ID.

        Returns None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def archive_compute_config(self, *, compute_config_id: str):
        """Archive the compute config for the provided ID."""
        raise NotImplementedError

    @abstractmethod
    def get_default_compute_config(self, *, cloud_id: str) -> ClusterCompute:
        """Get the default compute config for the provided cloud ID."""
        raise NotImplementedError

    @abstractmethod
    def get_default_build_id(self) -> str:
        """Get the default build id.

        If running in a workspace, it returns the workspace build id.
        Else it returns the default build id.
        """
        raise NotImplementedError

    @abstractmethod
    def get_cluster_env_build(self, build_id: str) -> Optional[ClusterEnvironmentBuild]:
        """Get the cluster env build.
        """
        raise NotImplementedError

    @abstractmethod
    def get_cluster_env_build_id_from_containerfile(
        self, cluster_env_name: str, containerfile: str, anonymous: bool
    ) -> str:
        """Get the cluster environment build ID for the cluster environment with provided containerfile.
        Look for an existing cluster environment with the provided name.
        If found, reuse it. Else, create a new cluster environment. The created cluster environment will be anonymous if anonymous is True.
        Create a new cluster environment build with the provided containerfile or try to reuse one with the same containerfile if exists.
        """
        raise NotImplementedError

    @abstractmethod
    def get_cluster_env_build_id_from_image_uri(
        self, image_uri: ImageURI,
    ):
        """Get the cluster environment build ID for the cluster environment with provided image_uri.

        It maps a image_uri to a cluster env name and then use the name to get the cluster env.
        If there exists a cluster environment for the image_uri, it will reuse the cluster env.
        Else it will create a new cluster environment.
        It will create a new cluster environment build with the provided image_uri or try to reuse one with the same image_uri if exists.

        The same URI should map to the same cluster env name and therefore the build but it is not guaranteed since
        the name format can change.

        """
        raise NotImplementedError

    @abstractmethod
    def get_cluster_env_build_image_uri(
        self, cluster_env_build_id: str
    ) -> Optional[ImageURI]:
        """Get the image URI for the provided build ID.

        Returns None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def get_service(self, name: str) -> Optional[ServiceModel]:
        """Get a service by name.

        Returns None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def get_job(
        self, name: Optional[str], job_id: Optional[str]
    ) -> Optional[ProductionJob]:
        """Get a job by name.

        Returns None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def get_job_runs(self, job_id: str) -> List[APIJobRun]:
        """Returns all job runs for a given job id.

        Returned in ascending order by creation time.
        """
        raise NotImplementedError

    @abstractmethod
    def rollout_service(self, model: ApplyServiceModel) -> ServiceModel:
        """Deploy or update the service to use the provided config.

        Returns the service ID.
        """
        raise NotImplementedError

    @abstractmethod
    def rollback_service(
        self, service_id: str, *, max_surge_percent: Optional[int] = None
    ):
        """Roll the service back to the primary version.

        This can only be used during an active rollout.
        """
        raise NotImplementedError

    @abstractmethod
    def terminate_service(self, service_id: str):
        """Mark the service to be terminated asynchronously."""
        raise NotImplementedError

    @abstractmethod
    def submit_job(self, model: CreateInternalProductionJob) -> InternalProductionJob:
        """Submit the job to run."""
        raise NotImplementedError

    @abstractmethod
    def terminate_job(self, job_id: str):
        """Mark the job to be terminated asynchronously."""
        raise NotImplementedError

    @abstractmethod
    def archive_job(self, job_id: str):
        """Mark the job to be archived asynchronously."""
        raise NotImplementedError

    @abstractmethod
    def upload_local_dir_to_cloud_storage(
        self,
        local_dir: str,
        *,
        cloud_id: str,
        excludes: Optional[List[str]] = None,
        overwrite_existing_file: bool = False
    ) -> str:
        """Upload the provided directory to cloud storage and return a URI for it.

        The directory will be zipped and the resulting URI can be used in a Ray runtime_env.

        The upload is preformed using a pre-signed URL fetched from Anyscale, so no
        local cloud provider authentication is required.

        The URI is content-addressable (containing a hash of the directory contents), so by
        default if the target file URI already exists it will not be overwritten.
        """
        raise NotImplementedError

    @abstractmethod
    def logs_for_job_run(self, job_run_id: str, follow: bool = False) -> str:
        """Returns the logs associated with a particular job run.

        If follow is True, the log will continue printing while the job is producing output.
        """
        raise NotImplementedError
