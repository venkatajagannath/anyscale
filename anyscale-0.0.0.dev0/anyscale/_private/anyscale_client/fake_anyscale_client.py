from collections import defaultdict
from datetime import datetime
import logging
from typing import DefaultDict, Dict, List, Optional, Tuple
import uuid

from anyscale._private.anyscale_client.common import (
    AnyscaleClientInterface,
    WORKSPACE_CLUSTER_NAME_PREFIX,
)
from anyscale._private.models.image_uri import ImageURI
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models import (
    Cloud,
    ComputeTemplateConfig,
    CreateInternalProductionJob,
    DecoratedComputeTemplate,
    HaJobGoalStates,
    HaJobStates,
    InternalProductionJob,
    ProductionJobStateTransition,
)
from anyscale.client.openapi_client.models.production_job import ProductionJob
from anyscale.cluster_compute import parse_cluster_compute_name_version
from anyscale.sdk.anyscale_client.configuration import Configuration
from anyscale.sdk.anyscale_client.models import (
    ApplyServiceModel,
    Cluster,
    ClusterCompute,
    ClusterComputeConfig,
    ComputeNodeType,
    Job as APIJobRun,
    ProductionServiceV2VersionModel,
    ServiceEventCurrentState,
    ServiceModel,
    ServiceVersionState,
)
from anyscale.sdk.anyscale_client.models.cluster_environment_build import (
    ClusterEnvironmentBuild,
)
from anyscale.sdk.anyscale_client.models.cluster_environment_build_status import (
    ClusterEnvironmentBuildStatus,
)
from anyscale.utils.workspace_notification import WorkspaceNotification


block_logger = BlockLogger()
logger = logging.getLogger(__name__)

OPENAPI_NO_VALIDATION = Configuration()
OPENAPI_NO_VALIDATION.client_side_validation = False


class FakeAnyscaleClient(AnyscaleClientInterface):
    BASE_UI_URL = "http://fake.com"
    CLOUD_BUCKET = "s3://fake-bucket/{cloud_id}"
    DEFAULT_CLOUD_ID = "fake-default-cloud-id"
    DEFAULT_CLOUD_NAME = "fake-default-cloud"
    DEFAULT_PROJECT_ID = "fake-default-project-id"
    DEFAULT_CLUSTER_COMPUTE_ID = "fake-default-cluster-compute-id"
    DEFAULT_CLUSTER_ENV_BUILD_ID = "fake-default-cluster-env-build-id"

    WORKSPACE_ID = "fake-workspace-id"
    WORKSPACE_CLOUD_ID = "fake-workspace-cloud-id"
    WORKSPACE_CLUSTER_ID = "fake-workspace-cluster-id"
    WORKSPACE_PROJECT_ID = "fake-workspace-project-id"
    WORKSPACE_CLUSTER_COMPUTE_ID = "fake-workspace-cluster-compute-id"
    WORKSPACE_CLUSTER_ENV_BUILD_ID = "fake-workspace-cluster-env-build-id"

    def __init__(self):
        self._image_uri_to_build_id: Dict[ImageURI, str] = {}
        self._build_id_to_image_uri: Dict[str, ImageURI] = {}
        self._containerfile_to_build_id: Dict[str, str] = {}
        self._compute_config_name_to_ids: DefaultDict[str, List[str]] = defaultdict(
            list
        )
        self._compute_config_id_to_cloud_id: Dict[str, str] = {}
        self._compute_configs: Dict[str, ClusterCompute] = {}
        self._archived_compute_configs: Dict[str, ClusterCompute] = {}
        self._workspace_cluster: Optional[Cluster] = None
        self._workspace_dependency_tracking_enabled: bool = False
        self._services: Dict[str, ServiceModel] = {}
        self._jobs: Dict[str, ProductionJob] = {}
        self._job_runs: Dict[str, List[APIJobRun]] = defaultdict(list)
        self._rolled_out_model: Optional[ApplyServiceModel] = None
        self._sent_workspace_notifications: List[WorkspaceNotification] = []
        self._rolled_back_service: Optional[Tuple[str, Optional[int]]] = None
        self._terminated_service: Optional[str] = None
        self._archived_jobs: Dict[str, ProductionJob] = {}
        self._requirements_path: Optional[str] = None
        self._upload_uri_mapping: Dict[str, str] = {}
        self._submitted_job: Optional[CreateInternalProductionJob] = None
        self._env_vars: Optional[Dict[str, str]] = None

        # Cloud ID -> Cloud.
        self._clouds: Dict[str, Cloud] = {
            self.DEFAULT_CLOUD_ID: Cloud(
                id=self.DEFAULT_CLOUD_ID,
                name=self.DEFAULT_CLOUD_NAME,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        }

        # Cloud ID -> default ClusterCompute.
        compute_config = ClusterCompute(
            id=self.DEFAULT_CLUSTER_COMPUTE_ID,
            config=ClusterComputeConfig(
                cloud_id=self.DEFAULT_CLOUD_ID,
                head_node_type=ComputeNodeType(
                    name="default-head-node",
                    instance_type="m5.2xlarge",
                    resources={"CPU": 8, "GPU": 1},
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )
        self._default_compute_configs: Dict[str, ClusterCompute] = {
            self.DEFAULT_CLOUD_ID: compute_config,
        }
        self.add_compute_config(compute_config)

    def get_job_ui_url(self, job_id: str) -> str:
        return f"{self.BASE_UI_URL}/jobs/{job_id}"

    def get_service_ui_url(self, service_id: str) -> str:
        return f"{self.BASE_UI_URL}/services/{service_id}"

    def get_compute_config_ui_url(
        self, compute_config_id: str, *, cloud_id: str
    ) -> str:
        return f"{self.BASE_UI_URL}/v2/{cloud_id}/compute-configs/{compute_config_id}"

    def set_inside_workspace(
        self,
        inside_workspace: bool,
        *,
        requirements_path: Optional[str] = None,
        cluster_name: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None,
    ):
        self._requirements_path = requirements_path
        self._env_vars = env_vars
        if inside_workspace:
            self._workspace_cluster = Cluster(
                id=self.WORKSPACE_CLUSTER_ID,
                name=cluster_name
                if cluster_name is not None
                else WORKSPACE_CLUSTER_NAME_PREFIX + "test",
                project_id=self.WORKSPACE_PROJECT_ID,
                cluster_compute_id=self.WORKSPACE_CLUSTER_COMPUTE_ID,
                cluster_environment_build_id=self.WORKSPACE_CLUSTER_ENV_BUILD_ID,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        else:
            self._workspace_cluster = None

    def get_current_workspace_id(self) -> Optional[str]:
        return (
            self.WORKSPACE_ID
            if self.get_current_workspace_cluster() is not None
            else None
        )

    def inside_workspace(self) -> bool:
        return self.get_current_workspace_cluster() is not None

    def get_workspace_env_vars(self) -> Optional[Dict[str, str]]:
        return self._env_vars

    def get_workspace_requirements_path(self) -> Optional[str]:
        if self.inside_workspace():
            return self._requirements_path
        return None

    def get_current_workspace_cluster(self) -> Optional[Cluster]:
        return self._workspace_cluster

    @property
    def sent_workspace_notifications(self) -> List[WorkspaceNotification]:
        return self._sent_workspace_notifications

    def send_workspace_notification(self, notification: WorkspaceNotification):
        if self.inside_workspace():
            self._sent_workspace_notifications.append(notification)

    def get_project_id(self, parent_cloud_id: str) -> str:  # noqa: ARG002
        workspace_cluster = self.get_current_workspace_cluster()
        if workspace_cluster is not None:
            return workspace_cluster.project_id

        return self.DEFAULT_PROJECT_ID

    def get_cloud_id(
        self,
        *,
        cloud_name: Optional[str] = None,
        compute_config_id: Optional[str] = None,
    ) -> str:
        assert not (cloud_name and compute_config_id)
        workspace_cluster = self.get_current_workspace_cluster()
        if workspace_cluster is not None:
            return self.WORKSPACE_CLOUD_ID

        if compute_config_id is not None:
            return self._compute_configs[compute_config_id].config.cloud_id

        if cloud_name is None:
            return self.DEFAULT_CLOUD_ID

        for cloud in self._clouds.values():
            if cloud.name == cloud_name:
                return cloud.id

        raise RuntimeError(f"Cloud with name '{cloud_name}' not found.")

    def add_cloud(self, cloud: Cloud):
        self._clouds[cloud.id] = cloud

    def get_cloud(self, *, cloud_id: str) -> Optional[Cloud]:
        return self._clouds.get(cloud_id, None)

    def add_compute_config(self, compute_config: DecoratedComputeTemplate) -> int:
        compute_config.version = (
            len(self._compute_config_name_to_ids[compute_config.name]) + 1
        )
        self._compute_configs[compute_config.id] = compute_config
        self._compute_config_name_to_ids[compute_config.name].append(compute_config.id)

        return compute_config.version

    def create_compute_config(
        self, config: ComputeTemplateConfig, *, name: Optional[str] = None
    ) -> Tuple[str, str]:
        unique_id = str(uuid.uuid4())
        compute_config_id = f"compute-config-id-{unique_id}"
        if name is None:
            anonymous = True
            name = f"anonymous-compute-config-{unique_id}"
        else:
            anonymous = False

        version = self.add_compute_config(
            DecoratedComputeTemplate(
                id=compute_config_id,
                name=name,
                config=config,
                anonymous=anonymous,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        return f"{name}:{version}", compute_config_id

    def get_compute_config(
        self, compute_config_id: str
    ) -> Optional[DecoratedComputeTemplate]:
        if compute_config_id in self._compute_configs:
            return self._compute_configs[compute_config_id]

        if compute_config_id in self._archived_compute_configs:
            return self._archived_compute_configs[compute_config_id]

        return None

    def get_compute_config_id(
        self, compute_config_name: Optional[str] = None, *, include_archived=False
    ) -> Optional[str]:
        if compute_config_name is not None:
            name, version = parse_cluster_compute_name_version(compute_config_name)
            if name not in self._compute_config_name_to_ids:
                return None

            if version is None:
                version = len(self._compute_config_name_to_ids[name])

            compute_config_id = self._compute_config_name_to_ids[name][version - 1]
            if (
                not include_archived
                and compute_config_id in self._archived_compute_configs
            ):
                return None

            return compute_config_id

        workspace_cluster = self.get_current_workspace_cluster()
        if workspace_cluster is not None:
            return workspace_cluster.cluster_compute_id

        return self.get_default_compute_config(cloud_id=self.get_cloud_id()).id

    def archive_compute_config(self, *, compute_config_id: str):
        archived_config = self._compute_configs.pop(compute_config_id)
        archived_config.archived_at = datetime.utcnow()
        self._archived_compute_configs[compute_config_id] = archived_config

    def is_archived_compute_config(self, compute_config_id: str) -> bool:
        return compute_config_id in self._archived_compute_configs

    def set_default_compute_config(
        self, compute_config: ClusterCompute, *, cloud_id: str
    ):
        self._default_compute_configs[cloud_id] = compute_config

    def get_default_compute_config(self, *, cloud_id: str) -> ClusterCompute:
        return self._default_compute_configs[cloud_id]

    def set_image_uri_mapping(self, image_uri: ImageURI, build_id: str):
        self._image_uri_to_build_id[image_uri] = build_id
        self._build_id_to_image_uri[build_id] = image_uri

    def set_containerfile_mapping(self, containerfile: str, build_id: str):
        self._containerfile_to_build_id[containerfile] = build_id

    def get_default_build_id(self) -> str:
        workspace_cluster = self.get_current_workspace_cluster()
        if workspace_cluster is not None:
            return workspace_cluster.cluster_environment_build_id
        return self.DEFAULT_CLUSTER_ENV_BUILD_ID

    def get_cluster_env_build(self, build_id: str) -> Optional[ClusterEnvironmentBuild]:
        if build_id in self._build_id_to_image_uri:
            return ClusterEnvironmentBuild(
                docker_image_name=self._build_id_to_image_uri[build_id],
                status=ClusterEnvironmentBuildStatus.SUCCEEDED,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        return None

    def get_cluster_env_build_id_from_containerfile(
        self, cluster_env_name: str, containerfile: str, anonymous: bool  # noqa: ARG002
    ) -> str:
        if containerfile in self._containerfile_to_build_id:
            return self._containerfile_to_build_id[containerfile]
        else:
            raise ValueError(f"The containerfile '{containerfile}' does not exist.")

    def get_cluster_env_build_id_from_image_uri(self, image_uri: ImageURI) -> str:
        if image_uri in self._image_uri_to_build_id:
            return self._image_uri_to_build_id[image_uri]
        else:
            raise ValueError(f"The image_uri '{image_uri}' does not exist.")

    def get_cluster_env_build_image_uri(
        self, cluster_env_build_id: str
    ) -> Optional[ImageURI]:
        return self._build_id_to_image_uri.get(cluster_env_build_id)

    def update_service(self, model: ServiceModel):
        self._services[model.id] = model

    def get_service(self, name: str) -> Optional[ServiceModel]:
        for service in self._services.values():
            if service.name == name:
                return service

        return None

    def get_job(
        self, name: Optional[str], job_id: Optional[str]
    ) -> Optional[ProductionJob]:
        if job_id is not None:
            return self._jobs.get(job_id, None)
        else:
            result: ProductionJob = None
            for job in self._jobs.values():
                if (
                    job is not None
                    and job.name == name
                    and (result is None or job.created_at > result.created_at)
                ):
                    result = job

        return result

    def get_job_runs(self, job_id: str) -> List[APIJobRun]:
        return self._job_runs.get(job_id, [])

    def update_job(self, model: ProductionJob):
        self._jobs[model.id] = model

    def update_job_run(self, prod_job_id: str, model: APIJobRun):
        self._job_runs[prod_job_id].append(model)

    @property
    def rolled_out_model(self) -> Optional[ApplyServiceModel]:
        return self._rolled_out_model

    def rollout_service(self, model: ApplyServiceModel) -> ServiceModel:
        self._rolled_out_model = model
        existing_service = self.get_service(model.name)
        if existing_service is not None:
            service_id = existing_service.id
        else:
            service_id = f"service-id-{uuid.uuid4()!s}"

        service = ServiceModel(
            id=service_id,
            name=model.name,
            current_state=ServiceEventCurrentState.RUNNING,
            base_url="http://fake-service-url",
            auth_token="fake-auth-token"
            if model.config.access.use_bearer_token
            else None,
            primary_version=ProductionServiceV2VersionModel(
                id=str(uuid.uuid4()),
                version="primary",
                current_state=ServiceVersionState.RUNNING,
                weight=100,
                build_id=model.build_id,
                compute_config_id=model.compute_config_id,
                ray_serve_config=model.ray_serve_config,
                ray_gcs_external_storage_config=model.ray_gcs_external_storage_config,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )

        self.update_service(service)
        return service

    @property
    def rolled_back_service(self) -> Optional[Tuple[str, Optional[int]]]:
        return self._rolled_back_service

    def rollback_service(
        self, service_id: str, *, max_surge_percent: Optional[int] = None
    ):
        self._rolled_back_service = (service_id, max_surge_percent)

    @property
    def terminated_service(self) -> Optional[str]:
        return self._terminated_service

    def terminate_service(self, service_id: str):
        self._terminated_service = service_id
        self._services[service_id].current_state = ServiceEventCurrentState.TERMINATED
        self._services[service_id].canary_version = None
        if self._services[service_id].primary_version is not None:
            # The backend leaves the primary_version populated upon termination.
            self._services[service_id].primary_version.weight = 100
            self._services[
                service_id
            ].primary_version.current_state = ServiceVersionState.TERMINATED

    @property
    def submitted_job(self) -> Optional[CreateInternalProductionJob]:
        return self._submitted_job

    def submit_job(self, model: CreateInternalProductionJob) -> InternalProductionJob:
        self._submitted_job = model

        job = InternalProductionJob(
            id=f"job-{uuid.uuid4()!s}",
            name=model.name,
            config=model.config,
            state=ProductionJobStateTransition(
                current_state=HaJobStates.PENDING,
                goal_state=HaJobGoalStates.SUCCESS,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )

        self.update_job(job)
        return job

    def terminate_job(self, job_id: str):
        self._jobs[job_id].state = HaJobStates.TERMINATED

    def archive_job(self, job_id: str):
        self._archived_jobs[job_id] = self._jobs.pop(job_id)

    def is_archived_job(self, job_id: str) -> bool:
        return job_id in self._archived_jobs

    def upload_local_dir_to_cloud_storage(
        self,
        local_dir: str,  # noqa: ARG002
        *,
        cloud_id: str,
        excludes: Optional[List[str]] = None,  # noqa: ARG002
        overwrite_existing_file: bool = False,  # noqa: ARG002
    ) -> str:
        # Ensure that URIs are consistent for the same passed directory.
        bucket = self.CLOUD_BUCKET.format(cloud_id=cloud_id)
        if local_dir not in self._upload_uri_mapping:
            self._upload_uri_mapping[
                local_dir
            ] = f"{bucket}/fake_pkg_{str(uuid.uuid4())}.zip"

        return self._upload_uri_mapping[local_dir]
