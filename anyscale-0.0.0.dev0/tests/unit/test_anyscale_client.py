from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
from typing import Any, DefaultDict, Dict, Generator, IO, List, Optional, Set, Tuple
from unittest.mock import patch
import uuid

from botocore.exceptions import ClientError
from common import OPENAPI_NO_VALIDATION, TestLogger
import pytest
from requests.exceptions import RequestException

from anyscale._private.anyscale_client import (
    AnyscaleClient,
    DEFAULT_PYTHON_VERSION,
    DEFAULT_RAY_VERSION,
)
from anyscale._private.anyscale_client.anyscale_client import (
    AWSS3ClientInterface,
    GCPGCSClientInterface,
)
from anyscale._private.models.image_uri import ImageURI
from anyscale.client.openapi_client.models import (
    ArchiveStatus,
    Cloud as InternalApiCloud,
    CloudDataBucketFileType,
    CloudDataBucketPresignedUploadInfo,
    CloudDataBucketPresignedUploadRequest,
    CloudNameOptions,
    ComputeTemplateConfig,
    ComputeTemplateQuery,
    CreateComputeTemplate,
    CreateInternalProductionJob,
    DecoratedComputeTemplate,
    DecoratedcomputetemplateListResponse,
    FeatureFlagResponse,
    HaJobGoalStates,
    HaJobStates,
    InternalProductionJob,
    ProductionJobConfig,
    ProductionJobStateTransition,
)
from anyscale.client.openapi_client.models.job_status import (
    JobStatus as BackendJobStatus,
)
from anyscale.client.openapi_client.rest import ApiException as InternalApiException
from anyscale.sdk.anyscale_client.models import (
    ApplyServiceModel,
    Cloud,
    Cluster,
    ClusterCompute,
    ClusterComputeConfig,
    ClusterEnvironment,
    ClusterEnvironmentBuild,
    ClusterenvironmentbuildListResponse,
    ClusterEnvironmentBuildOperation,
    ClusterenvironmentbuildoperationResponse,
    ClusterenvironmentListResponse,
    ComputeNodeType,
    ComputeTemplate,
    Job as APIJobRun,
    ListResponseMetadata,
    ProductionServiceV2VersionModel,
    Project,
    RollbackServiceModel,
    ServiceEventCurrentState,
    ServiceGoalStates,
    ServiceModel,
    ServicemodelListResponse,
)
from anyscale.sdk.anyscale_client.models.cluster_environment_build_status import (
    ClusterEnvironmentBuildStatus,
)
from anyscale.sdk.anyscale_client.models.create_cluster_environment import (
    CreateClusterEnvironment,
)
from anyscale.sdk.anyscale_client.models.create_cluster_environment_build import (
    CreateClusterEnvironmentBuild,
)
from anyscale.sdk.anyscale_client.models.job_list_response import JobListResponse
from anyscale.sdk.anyscale_client.models.jobs_query import JobsQuery
from anyscale.sdk.anyscale_client.rest import ApiException as ExternalApiException
from anyscale.utils.workspace_notification import (
    WORKSPACE_NOTIFICATION_ADDRESS,
    WorkspaceNotification,
    WorkspaceNotificationAction,
)


def _get_test_file_path(subpath: str) -> str:
    return os.path.join(os.path.dirname(__file__), "test_files", subpath)


BASIC_WORKING_DIR = _get_test_file_path("working_dirs/basic")
NESTED_WORKING_DIR = _get_test_file_path("working_dirs/nested")
SYMLINK_WORKING_DIR = _get_test_file_path("working_dirs/symlink_to_basic")
TEST_WORKING_DIRS = [BASIC_WORKING_DIR, NESTED_WORKING_DIR, SYMLINK_WORKING_DIR]

TEST_WORKSPACE_REQUIREMENTS_FILE_PATH = _get_test_file_path(
    "requirements_files/test_workspace_requirements.txt"
)

FAKE_WORKSPACE_NOTIFICATION = WorkspaceNotification(
    body="Hello world!",
    action=WorkspaceNotificationAction(
        type="navigate-service", title="fake-title", value="fake-value",
    ),
)


class FakeServiceController:
    pass


@dataclass
class FakeClientResult:
    result: Any


class FakeExternalAPIClient:
    """Fake implementation of the "external" Anyscale REST API.

    Should mimic the behavior and return values of the client defined at:
    `anyscale.sdk.anyscale_client`.
    """

    DEFAULT_CLOUD_ID = "fake-default-cloud-id"
    DEFAULT_PROJECT_ID = "fake-default-project-id"
    DEFAULT_CLUSTER_COMPUTE_ID = "fake-default-cluster-compute-id"
    DEFAULT_CLUSTER_COMPUTE_HEAD_NODE_INSTANCE_TYPE = (
        "fake-default-cluster-compute-head-node-instance-type"
    )
    DEFAULT_CLUSTER_ENV_BUILD_ID = "fake-default-cluster-env-build-id"

    WORKSPACE_CLOUD_ID = "fake-workspace-cloud-id"
    WORKSPACE_CLUSTER_ID = "fake-workspace-cluster-id"
    WORKSPACE_PROJECT_ID = "fake-workspace-project-id"
    WORKSPACE_CLUSTER_COMPUTE_ID = "fake-workspace-cluster-compute-id"
    WORKSPACE_CLUSTER_ENV_BUILD_ID = "fake-workspace-cluster-env-build-id"

    def __init__(self):
        self._num_get_cloud_calls: int = 0
        self._num_get_project_calls: int = 0
        self._num_get_cluster_calls: int = 0
        self._num_get_cluster_compute_calls: int = 0

        # Cluster environment ID to ClusterEnvironment.
        self._cluster_envs: Dict[str, ClusterEnvironment] = {}
        # Cluster environment build ID to ClusterEnvironmentBuild.
        self._cluster_env_builds: Dict[str, ClusterEnvironmentBuild] = {}
        self._cluster_env_builds_to_fail: Dict[str, Tuple[int, int]] = {}

        # Cluster compute ID to name. Populate workspace mapping by default.
        self._cluster_computes: Dict[str, ClusterCompute] = {
            self.WORKSPACE_CLUSTER_COMPUTE_ID: ClusterCompute(
                id=self.WORKSPACE_CLUSTER_COMPUTE_ID,
                config=ClusterComputeConfig(
                    cloud_id=self.WORKSPACE_CLOUD_ID,
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        }

        # Service name to model.
        self._services: Dict[str, ServiceModel] = {}

        # Used to emulate multi-page list endpoint behavior.
        self._next_services_list_paging_token: Optional[str] = None

        # Used to emulate returns from search_jobs
        self._job_runs: Dict[str, List[APIJobRun]] = defaultdict(list)

    def _get_service_by_id(self, service_id: str) -> Optional[ServiceModel]:
        service = None
        for s in self._services.values():
            if s.id == service_id:
                service = s

        return service

    @property
    def num_get_cloud_calls(self) -> int:
        return self._num_get_cloud_calls

    def get_default_cloud(self) -> FakeClientResult:
        self._num_get_cloud_calls += 1
        return FakeClientResult(
            result=Cloud(
                id=self.DEFAULT_CLOUD_ID,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

    @property
    def num_get_project_calls(self) -> int:
        return self._num_get_project_calls

    def get_default_project(
        self, parent_cloud_id: Optional[str] = None
    ) -> FakeClientResult:
        self._num_get_project_calls += 1
        return FakeClientResult(
            result=Project(
                id=self.DEFAULT_PROJECT_ID,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

    def get_default_cluster_compute(
        self, cloud_id: Optional[str] = None
    ) -> FakeClientResult:
        return FakeClientResult(
            result=ComputeTemplate(
                id=self.DEFAULT_CLUSTER_COMPUTE_ID,
                config=ClusterComputeConfig(
                    cloud_id=cloud_id or self.DEFAULT_CLOUD_ID,
                    head_node_type=ComputeNodeType(
                        instance_type=self.DEFAULT_CLUSTER_COMPUTE_HEAD_NODE_INSTANCE_TYPE,
                        local_vars_configuration=OPENAPI_NO_VALIDATION,
                    ),
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

    def get_default_cluster_environment_build(
        self, python_version: str, ray_version: str
    ) -> FakeClientResult:
        assert ray_version == DEFAULT_RAY_VERSION
        assert python_version == DEFAULT_PYTHON_VERSION

        return FakeClientResult(
            result=ClusterEnvironmentBuild(
                id=self.DEFAULT_CLUSTER_ENV_BUILD_ID,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

    @property
    def num_get_cluster_calls(self) -> int:
        return self._num_get_cluster_calls

    def get_cluster(self, cluster_id: str) -> FakeClientResult:
        self._num_get_cluster_calls += 1
        assert (
            cluster_id == self.WORKSPACE_CLUSTER_ID
        ), "`get_cluster` should only be used to get the workspace cluster."
        return FakeClientResult(
            result=Cluster(
                id=self.WORKSPACE_CLUSTER_ID,
                project_id=self.WORKSPACE_PROJECT_ID,
                cluster_compute_id=self.WORKSPACE_CLUSTER_COMPUTE_ID,
                cluster_environment_build_id=self.WORKSPACE_CLUSTER_ENV_BUILD_ID,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

    @property
    def num_get_cluster_compute_calls(self) -> int:
        return self._num_get_cluster_compute_calls

    def set_cluster_compute_mapping(
        self, cluster_compute_id: str, cluster_compute: ClusterCompute
    ):
        self._cluster_computes[cluster_compute_id] = cluster_compute

    def get_cluster_compute(self, cluster_compute_id: str) -> FakeClientResult:
        self._num_get_cluster_compute_calls += 1
        if cluster_compute_id not in self._cluster_computes:
            raise ExternalApiException(status=404)
        return FakeClientResult(result=self._cluster_computes[cluster_compute_id],)

    def create_cluster_environment(
        self, cluster_environment: CreateClusterEnvironment
    ) -> FakeClientResult:
        cluster_env_id = str(f"apt_{len(self._cluster_envs) + 1}")
        self._cluster_envs[cluster_env_id] = ClusterEnvironment(
            id=cluster_env_id,
            name=cluster_environment.name,
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )
        return FakeClientResult(result=self._cluster_envs[cluster_env_id])

    def list_cluster_environment_builds(
        self,
        *,
        cluster_environment_id: str,
        count: int,
        paging_token: Optional[str] = None,
    ) -> ClusterenvironmentbuildListResponse:
        results = []
        for _, v in self._cluster_env_builds.items():
            if v.cluster_environment_id == cluster_environment_id:
                results.append(v)

        return ClusterenvironmentbuildListResponse(results=results)

    def mark_cluster_env_build_to_fail(
        self, cluster_env_build_id: str, *, after_iterations: int = 0
    ):
        self._cluster_env_builds_to_fail[cluster_env_build_id] = (0, after_iterations)

    def create_cluster_environment_build(
        self, cluster_environment_build: CreateClusterEnvironmentBuild
    ) -> ClusterenvironmentbuildoperationResponse:
        build_id = str(f"bld_{len(self._cluster_env_builds) + 1}")
        self._cluster_env_builds[build_id] = ClusterEnvironmentBuild(
            id=build_id,
            cluster_environment_id=cluster_environment_build.cluster_environment_id,
            docker_image_name=cluster_environment_build.docker_image_name,
            containerfile=cluster_environment_build.containerfile,
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )
        return ClusterenvironmentbuildoperationResponse(
            result=ClusterEnvironmentBuildOperation(
                id=f"op_{uuid.uuid4()}",
                completed=True,
                cluster_environment_build_id=build_id,
            )
        )

    def search_cluster_environments(
        self, query: Dict[str, Any]
    ) -> ClusterenvironmentListResponse:
        # support name equals only now
        assert "name" in query
        assert "equals" in query["name"]
        name = query["name"]["equals"]
        results = []
        for _, v in self._cluster_envs.items():
            if v.name == name:
                results.append(v)
        return ClusterenvironmentListResponse(results=results,)

    def set_cluster_env(
        self, cluster_environment_id: str, cluster_env: ClusterEnvironment
    ):
        self._cluster_envs[cluster_environment_id] = cluster_env

    def get_cluster_environment(self, cluster_environment_id: str,) -> FakeClientResult:
        if cluster_environment_id not in self._cluster_envs:
            raise ExternalApiException(status=404)

        return FakeClientResult(result=self._cluster_envs[cluster_environment_id])

    def set_cluster_env_build(
        self,
        cluster_environment_build_id: str,
        cluster_environment_build: ClusterEnvironmentBuild,
    ):
        self._cluster_env_builds[
            cluster_environment_build_id
        ] = cluster_environment_build

    def find_cluster_environment_build_by_identifier(
        self, identifier: str
    ) -> FakeClientResult:
        for _, v in self._cluster_env_builds.items():
            cluster_env = self._cluster_envs.get(v.cluster_environment_id)
            assert cluster_env is not None
            if f"{cluster_env.name}:{v.revision}" == identifier:
                return FakeClientResult(result=v)
        raise ExternalApiException(status=404)

    def get_cluster_environment_build(
        self, cluster_environment_build_id: str
    ) -> FakeClientResult:
        if cluster_environment_build_id not in self._cluster_env_builds:
            raise ExternalApiException(status=404)

        # if the build id exists in the fail map, increment the iteration
        if cluster_environment_build_id in self._cluster_env_builds_to_fail:
            counters = self._cluster_env_builds_to_fail[cluster_environment_build_id]
            if counters[0] == counters[1]:
                self._cluster_env_builds[
                    cluster_environment_build_id
                ].status = ClusterEnvironmentBuildStatus.FAILED
            else:
                self._cluster_env_builds_to_fail[cluster_environment_build_id] = (
                    counters[0] + 1,
                    counters[1],
                )
        else:
            # mark the build succeeded
            self._cluster_env_builds[
                cluster_environment_build_id
            ].status = ClusterEnvironmentBuildStatus.SUCCEEDED

        return FakeClientResult(
            result=self._cluster_env_builds[cluster_environment_build_id],
        )

    def complete_rollout(self, name: str):
        service = self._services.get(name, None)
        assert service is not None, f"Service {name} not found."
        assert service.current_state in {
            ServiceEventCurrentState.STARTING,
            ServiceEventCurrentState.ROLLING_OUT,
        }, f"Service {name} not rolling out."

        if service.current_state == ServiceEventCurrentState.STARTING:
            assert service.canary_version is None
            service.current_state = ServiceEventCurrentState.RUNNING
        elif service.current_state == ServiceEventCurrentState.ROLLING_OUT:
            assert service.canary_version is not None
            service.primary_version = service.canary_version
            service.canary_version = None
            service.current_state = ServiceEventCurrentState.RUNNING
        else:
            raise RuntimeError(f"Service {name} not rolling out.")

    def rollout_service(self, model: ApplyServiceModel) -> FakeClientResult:
        if model.name in self._services:
            service = self._services[model.name]
        else:
            service = ServiceModel(
                id=str(uuid.uuid4()),
                cloud_id="fake-service-cloud-id",
                name=model.name,
                current_state=ServiceEventCurrentState.TERMINATED,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )

        service.goal_state = ServiceGoalStates.RUNNING
        if service.current_state == ServiceEventCurrentState.TERMINATED:
            service.current_state = ServiceEventCurrentState.STARTING
        else:
            service.current_state = ServiceEventCurrentState.ROLLING_OUT

        new_version = ProductionServiceV2VersionModel(
            version=model.version or str(uuid.uuid4()),
            build_id=model.build_id,
            compute_config_id=model.compute_config_id,
            ray_serve_config=model.ray_serve_config,
            ray_gcs_external_storage_config=model.ray_gcs_external_storage_config,
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )

        if service.primary_version is None:
            new_version.weight = 100
            service.primary_version = new_version
        else:
            # TODO: reject rollouts to a new version while one is in flight.
            new_version.weight = (
                model.canary_percent if model.canary_percent is not None else 100
            )
            service.canary_version = new_version

        self._services[model.name] = service
        return FakeClientResult(result=service)

    def complete_rollback(self, name: str):
        service = self._services.get(name, None)
        assert service is not None, f"Service {name} not found."
        assert service.current_state in {
            ServiceEventCurrentState.ROLLING_BACK
        }, f"Service {name} not rolling back."

        service.current_state = ServiceEventCurrentState.RUNNING

    def rollback_service(
        self, service_id: str, rollback_service_model: RollbackServiceModel
    ):
        service = self._get_service_by_id(service_id)
        assert service is not None, f"Service {service_id} not found."
        assert service.current_state in {
            ServiceEventCurrentState.ROLLING_OUT
        }, f"Service {service_id} not rolling out."

        service.current_state = ServiceEventCurrentState.ROLLING_BACK
        service.canary_version = None
        service.primary_version.weight = 100

        return service

    def complete_termination(self, name: str):
        service = self._services.get(name, None)
        assert service is not None, f"Service {name} not found."
        assert service.current_state in {
            ServiceEventCurrentState.TERMINATING
        }, f"Service {name} not terminating."

        service.current_state = ServiceEventCurrentState.TERMINATED

    def terminate_service(self, service_id: str):
        service = self._get_service_by_id(service_id)
        assert service is not None, f"Service {service_id} not found."
        service.current_state = ServiceEventCurrentState.TERMINATING
        service.canary_version = None
        service.primary_version = None

        return service

    def list_services(
        self, *, project_id: str, name: str, count: int, paging_token: Optional[str]
    ) -> ServicemodelListResponse:
        assert paging_token == self._next_services_list_paging_token
        int_paging_token = 0 if paging_token is None else int(paging_token)

        services_list = list(self._services.values())

        slice_begin = int_paging_token * count
        slice_end = min((int_paging_token + 1) * count, len(services_list))
        if slice_end == len(services_list):
            self._next_services_list_paging_token = None
        else:
            self._next_services_list_paging_token = str(int_paging_token + 1)

        return ServicemodelListResponse(
            results=services_list[slice_begin:slice_end],
            metadata=ListResponseMetadata(
                next_paging_token=self._next_services_list_paging_token,
                total=len(services_list),
            ),
        )

    def search_jobs(self, query: JobsQuery) -> JobListResponse:
        assert len(query.sort_by_clauses) == 1
        assert query.sort_by_clauses[0].sort_field == "CREATED_AT"
        assert query.sort_by_clauses[0].sort_order == "ASC"
        assert query.ha_job_id is not None
        assert query.paging is not None and query.paging.paging_token is None

        job_runs = self._job_runs.get(query.ha_job_id, [])

        job_runs = sorted(job_runs, key=lambda x: x.created_at)

        return JobListResponse(
            results=job_runs,
            metadata=ListResponseMetadata(next_paging_token=None, total=len(job_runs)),
        )


class FakeInternalAPIClient:
    """Fake implementation of the "internal" Anyscale REST API.

    Should mimic the behavior and return values of the client defined at:
    `anyscale.client.openai_client`.
    """

    FAKE_FILE_URI = "s3://some-bucket/{file_name}"
    FAKE_UPLOAD_URL_PREFIX = "http://some-domain.com/upload-magic-file/"

    def __init__(self):
        # Compute template ID to compute template.
        self._compute_templates: Dict[str, DecoratedComputeTemplate] = {}
        # Compute template name to latest version int.
        self._compute_template_versions: DefaultDict[str, int] = defaultdict(int)
        # Job ID to job.
        self._jobs: Dict[str, InternalProductionJob] = {}
        # Set of URIs that have already been uploaded.
        self._uploaded_presigned_file_names: Set[str] = set()
        # Cloud name to cloud.
        self._clouds: Dict[str, InternalApiCloud] = {}
        self._num_get_cloud_calls: int = 0

    def check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get(
        self, key: str
    ) -> FakeClientResult:
        ff_on = False
        if key == "cloud-isolation-phase-1":
            ff_on = True
        return FakeClientResult(result=FeatureFlagResponse(is_on=ff_on),)

    def generate_cloud_data_bucket_presigned_upload_url_api_v2_clouds_cloud_id_generate_cloud_data_bucket_presigned_upload_url_post(
        self, cloud_id: str, request: CloudDataBucketPresignedUploadRequest
    ) -> FakeClientResult:
        assert request.file_type == CloudDataBucketFileType.RUNTIME_ENV_PACKAGES
        assert isinstance(request.file_name, str)

        # The first time a file name is requested, it will return that the file doesn't exist.
        # On subsequent requests, it will return that the file exists.
        file_exists = request.file_name in self._uploaded_presigned_file_names
        self._uploaded_presigned_file_names.add(request.file_name)
        return FakeClientResult(
            result=CloudDataBucketPresignedUploadInfo(
                upload_url=self.FAKE_UPLOAD_URL_PREFIX + request.file_name,
                file_uri=self.FAKE_FILE_URI.format(file_name=request.file_name),
                file_exists=file_exists,
            ),
        )

    def add_compute_template(self, compute_template: DecoratedComputeTemplate) -> int:
        assert compute_template.version is None, "Version is populated by the backend."
        self._compute_template_versions[compute_template.name] += 1
        compute_template.version = self._compute_template_versions[
            compute_template.name
        ]
        self._compute_templates[compute_template.id] = compute_template
        return self._compute_template_versions[compute_template.name]

    def create_compute_template_api_v2_compute_templates_post(
        self, create_compute_template: CreateComputeTemplate,
    ) -> FakeClientResult:
        compute_config_id = f"compute-template-{uuid.uuid4()!s}"
        if create_compute_template.anonymous:
            assert not create_compute_template.name
            name = f"anonymous-{compute_config_id}"
        else:
            assert create_compute_template.name
            name = create_compute_template.name

        compute_template = DecoratedComputeTemplate(
            id=compute_config_id,
            name=name,
            anonymous=create_compute_template.anonymous,
            config=create_compute_template.config,
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )
        compute_template.version = self.add_compute_template(compute_template)
        return FakeClientResult(result=compute_template)

    def get_compute_template_api_v2_compute_templates_template_id_get(
        self, compute_config_id: str
    ) -> FakeClientResult:
        if compute_config_id not in self._compute_templates:
            raise InternalApiException(status=404)

        return FakeClientResult(result=self._compute_templates[compute_config_id])

    def archive_compute_template_api_v2_compute_templates_compute_template_id_archive_post(
        self, compute_config_id: str
    ):
        if compute_config_id not in self._compute_templates:
            raise InternalApiException(status=404)

        # TODO(edoakes): verify that this API is idempotent and this is the correct behavior.
        if self._compute_templates[compute_config_id].archived_at is None:
            self._compute_templates[compute_config_id].archived_at = datetime.now()

    def search_compute_templates_api_v2_compute_templates_search_post(
        self, query: ComputeTemplateQuery
    ) -> DecoratedcomputetemplateListResponse:
        """Get compute templates matching the query.

        Version semantics are:
            None: get all versions.
            -1: get latest version.
            >= 0: match a specific version.
        """
        assert query.orgwide
        assert query.include_anonymous

        assert len(query.name) == 1
        assert next(iter(query.name.keys())) == "equals"
        name = next(iter(query.name.values()))

        results = []
        latest_version_found = -1
        for compute_template in self._compute_templates.values():
            is_archived = compute_template.archived_at is not None
            if is_archived and query.archive_status == ArchiveStatus.NOT_ARCHIVED:
                continue
            elif not is_archived and query.archive_status == ArchiveStatus.ARCHIVED:
                continue

            if name == compute_template.name:
                if query.version is None:
                    results.append(compute_template)
                elif query.version == -1:
                    if compute_template.version > latest_version_found:
                        latest_version_found = compute_template.version
                        results = [compute_template]
                elif compute_template.version == query.version:
                    results.append(compute_template)

        assert len(results) <= 1
        return DecoratedcomputetemplateListResponse(results=results)

    def get_job(self, job_id: str) -> Optional[InternalProductionJob]:
        return self._jobs[job_id]

    def create_job_api_v2_decorated_ha_jobs_create_post(
        self, model: CreateInternalProductionJob
    ) -> FakeClientResult:
        job_id = f"job-{uuid.uuid4()!s}"
        job = InternalProductionJob(
            id=job_id,
            name=model.name,
            config=model.config,
            state=ProductionJobStateTransition(
                current_state=HaJobStates.PENDING,
                goal_state=HaJobGoalStates.SUCCESS,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )
        self._jobs[job_id] = job
        return FakeClientResult(result=job)

    def add_cloud(self, cloud: InternalApiCloud):
        self._clouds[cloud.name] = cloud

    @property
    def num_get_cloud_calls(self) -> int:
        return self._num_get_cloud_calls

    def find_cloud_by_name_api_v2_clouds_find_by_name_post(
        self, options: CloudNameOptions
    ) -> FakeClientResult:
        self._num_get_cloud_calls += 1
        assert options.name
        if options.name not in self._clouds:
            raise InternalApiException(status=404)

        return FakeClientResult(result=self._clouds[options.name])


class FakeAWSS3Client(AWSS3ClientInterface):
    def __init__(self):
        self._uploaded_files: Dict[str, bytes] = {}

    def upload_file(self, bucket: str, key: str, file_contents: bytes):
        self._uploaded_files[f"{bucket}/{key}"] = file_contents

    def download_fileobj(self, Bucket: str, Key: str, Fileobj: IO[Any]):
        file_name = f"{Bucket}/{Key}"
        if file_name not in self._uploaded_files:
            raise ClientError(
                error_response={"Error": {"Code": "404"}}, operation_name="GetObject"
            )
        Fileobj.write(self._uploaded_files[file_name])


class FakeGCSBlob:
    def __init__(self, name: str, file_contents: bytes, exists: bool = True):
        self.name = name
        self.file_contents = file_contents
        self._exists = exists

    def exists(self):
        return self._exists

    def download_to_file(self, fileobj: IO[Any]):
        fileobj.write(self.file_contents)


class FakeGCSBucket:
    def __init__(self, name: str):
        self.name = name
        self._blobs: Dict[str, FakeGCSBlob] = {}

    def upload_blob(self, name: str, file_contents: bytes):
        self._blobs[name] = FakeGCSBlob(name, file_contents)

    def blob(self, name: str):
        if name not in self._blobs:
            return FakeGCSBlob(name, b"", exists=False)
        return self._blobs[name]


class FakeGCPGCSClient(GCPGCSClientInterface):
    def __init__(self):
        self._buckets: Dict[str, FakeGCSBucket] = {}

    def bucket(self, bucket: str):
        if bucket not in self._buckets:
            self._buckets[bucket] = FakeGCSBucket(bucket)
        return self._buckets[bucket]

    def create_bucket(self, name: str):
        self._buckets[name] = FakeGCSBucket(name)


@pytest.fixture()
def setup_anyscale_client(
    request,
) -> Generator[
    Tuple[
        AnyscaleClient,
        FakeExternalAPIClient,
        FakeInternalAPIClient,
        TestLogger,
        FakeAWSS3Client,
        FakeGCPGCSClient,
    ],
    None,
    None,
]:
    if not hasattr(request, "param"):
        request.param = {}

    # Mimic running in a workspace by setting expected environment variables.
    mock_os_environ: Dict[str, str] = {}
    if request.param.get("inside_workspace", False):
        mock_os_environ.update(
            ANYSCALE_SESSION_ID=FakeExternalAPIClient.WORKSPACE_CLUSTER_ID,
            ANYSCALE_EXPERIMENTAL_WORKSPACE_ID="fake-workspace-id",
        )

        if request.param.get("cloud_vendor", "aws"):
            mock_os_environ.update(ANYSCALE_INTERNAL_SYSTEM_STORAGE="s3://fake-bucket",)
        else:
            mock_os_environ.update(ANYSCALE_INTERNAL_SYSTEM_STORAGE="gs://fake-bucket",)

        mock_os_environ.update(ANYSCALE_WORKSPACE_DYNAMIC_DEPENDENCY_TRACKING="1",)
        if request.param.get("workspace_dependency_tracking_disabled", False):
            mock_os_environ.update(ANYSCALE_SKIP_PYTHON_DEPENDENCY_TRACKING="1")

    sleep = request.param.get("sleep", None)

    fake_external_client = FakeExternalAPIClient()
    fake_internal_client = FakeInternalAPIClient()
    fake_s3_client = FakeAWSS3Client()
    fake_gcs_client = FakeGCPGCSClient()
    logger = TestLogger()
    anyscale_client = AnyscaleClient(
        api_clients=(fake_external_client, fake_internal_client),
        workspace_requirements_file_path=TEST_WORKSPACE_REQUIREMENTS_FILE_PATH,
        sleep=sleep,
        logger=logger,
        host="https://anyscale-test.com",
        s3_client=fake_s3_client,
        gcs_client=fake_gcs_client,
    )

    with patch.dict(os.environ, mock_os_environ):
        yield anyscale_client, fake_external_client, fake_internal_client, logger, fake_s3_client, fake_gcs_client


class FakeRequestsResponse:
    def __init__(self, *, should_raise: bool):
        self._should_raise = should_raise

    def raise_for_status(self):
        if self._should_raise:
            raise RequestException("Fake request error!")


class FakeRequests:
    def __init__(self):
        self._should_raise = False
        self.reset()

    def reset(self):
        self.sent_json: Optional[Dict] = None
        self.sent_data: Optional[bytes] = None
        self.called_url: Optional[str] = None
        self.called_method: Optional[str] = None

    def set_should_raise(self, should_raise: bool):
        self._should_raise = should_raise

    def _do_request(
        self,
        method: str,
        url: str,
        *,
        data: Optional[bytes] = None,
        json: Optional[Dict] = None,
    ) -> FakeRequestsResponse:
        self.called_method = method
        self.called_url = url
        self.sent_data = data
        self.sent_json = json

        return FakeRequestsResponse(should_raise=self._should_raise)

    def put(self, url: str, *, data: Optional[bytes] = None) -> FakeRequestsResponse:
        return self._do_request("PUT", url, data=data)

    def post(self, url: str, *, json: Optional[Dict] = None) -> FakeRequestsResponse:
        return self._do_request("POST", url, json=json)


@pytest.fixture()
def fake_requests() -> Generator[FakeRequests, None, None]:
    fake_requests = FakeRequests()
    with patch("requests.post", new=fake_requests.post), patch(
        "requests.put", new=fake_requests.put
    ):
        yield fake_requests


class TestWorkspaceMethods:
    @pytest.mark.parametrize(
        "setup_anyscale_client", [{"inside_workspace": False}], indirect=True
    )
    def test_call_inside_workspace_outside_workspace(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client
        assert not anyscale_client.inside_workspace()

    @pytest.mark.parametrize(
        "setup_anyscale_client", [{"inside_workspace": True}], indirect=True
    )
    def test_call_inside_workspace_inside_workspace(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client
        assert anyscale_client.inside_workspace()

    @pytest.mark.parametrize(
        "setup_anyscale_client",
        [
            {"inside_workspace": True, "cloud_vendor": "aws"},
            {"inside_workspace": True, "cloud_vendor": "gcp"},
        ],
        indirect=True,
    )
    @pytest.mark.parametrize("not_found", [True, False])
    def test_get_workspace_env_vars(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
        not_found: bool,
    ):
        (
            anyscale_client,
            _,
            _,
            _,
            fake_s3_client,
            fake_gcs_client,
        ) = setup_anyscale_client
        raw_env_vars = b"K1=V1\0K2=V2\0"
        if not not_found:
            fake_s3_client.upload_file(
                "fake-bucket",
                "workspace_tracking_dependencies/fake-workspace-id/.env",
                raw_env_vars,
            )
            fake_gcs_client.bucket("fake-bucket").upload_blob(
                "workspace_tracking_dependencies/fake-workspace-id/.env", raw_env_vars,
            )
            expected = {
                "K1": "V1",
                "K2": "V2",
            }
        else:
            expected = None
        assert anyscale_client.get_workspace_env_vars() == expected

    @pytest.mark.parametrize(
        "setup_anyscale_client", [{"inside_workspace": False}], indirect=True
    )
    def test_call_get_current_workspace_cluster_outside_workspace(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client
        assert anyscale_client.get_current_workspace_cluster() is None
        assert fake_external_client.num_get_cluster_calls == 0

    @pytest.mark.parametrize(
        "setup_anyscale_client", [{"inside_workspace": True}], indirect=True
    )
    def test_call_get_current_workspace_cluster_inside_workspace(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client

        # The cluster model should be cached so we only make one API call.
        for _ in range(100):
            cluster = anyscale_client.get_current_workspace_cluster()
            assert cluster is not None
            assert cluster.id == FakeExternalAPIClient.WORKSPACE_CLUSTER_ID
            assert cluster.project_id == FakeExternalAPIClient.WORKSPACE_PROJECT_ID
            assert (
                cluster.cluster_compute_id
                == FakeExternalAPIClient.WORKSPACE_CLUSTER_COMPUTE_ID
            )
            assert (
                cluster.cluster_environment_build_id
                == FakeExternalAPIClient.WORKSPACE_CLUSTER_ENV_BUILD_ID
            )

            assert fake_external_client.num_get_cluster_calls == 1

    @pytest.mark.parametrize(
        "setup_anyscale_client", [{"inside_workspace": False,}], indirect=True
    )
    def test_call_get_workspace_requirements_path_outside_workspace(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client

        # Should return None even if the file path exists.
        assert anyscale_client.get_workspace_requirements_path() is None

    @pytest.mark.parametrize(
        "setup_anyscale_client", [{"inside_workspace": True}], indirect=True
    )
    def test_call_get_workspace_requirements_path_inside_workspace(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client
        assert (
            anyscale_client.get_workspace_requirements_path()
            == TEST_WORKSPACE_REQUIREMENTS_FILE_PATH
        )

    @pytest.mark.parametrize(
        "setup_anyscale_client",
        [{"inside_workspace": True, "workspace_dependency_tracking_disabled": True}],
        indirect=True,
    )
    def test_call_get_workspace_requirements_path_inside_workspace_disabled(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client
        assert anyscale_client.get_workspace_requirements_path() is None

    @pytest.mark.parametrize(
        "setup_anyscale_client", [{"inside_workspace": False}], indirect=True,
    )
    def test_send_notification_outside_workspace(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
        fake_requests: FakeRequests,
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client
        anyscale_client.send_workspace_notification(FAKE_WORKSPACE_NOTIFICATION)

        # Nothing should be sent because we're not in a workspace.
        assert fake_requests.called_url is None

    @pytest.mark.parametrize(
        "setup_anyscale_client", [{"inside_workspace": True}], indirect=True,
    )
    def test_send_notification_inside_workspace(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
        fake_requests: FakeRequests,
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client
        anyscale_client.send_workspace_notification(FAKE_WORKSPACE_NOTIFICATION)

        assert fake_requests.called_method == "POST"
        assert fake_requests.called_url == WORKSPACE_NOTIFICATION_ADDRESS
        assert fake_requests.sent_json == FAKE_WORKSPACE_NOTIFICATION.dict()

    @pytest.mark.parametrize(
        "setup_anyscale_client", [{"inside_workspace": True}], indirect=True,
    )
    def test_send_notification_fails(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
        fake_requests: FakeRequests,
    ):
        """Failing to send a notification should *not* raise an exception."""
        anyscale_client, _, _, _, _, _ = setup_anyscale_client
        fake_requests.set_should_raise(True)
        anyscale_client.send_workspace_notification(FAKE_WORKSPACE_NOTIFICATION)

        assert fake_requests.called_method == "POST"
        assert fake_requests.called_url == WORKSPACE_NOTIFICATION_ADDRESS
        assert fake_requests.sent_json == FAKE_WORKSPACE_NOTIFICATION.dict()


class TestGetCloudID:
    def test_get_default(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client

        # The cloud ID should be cached so we only make one API call.
        for _ in range(100):
            assert (
                anyscale_client.get_cloud_id() == FakeExternalAPIClient.DEFAULT_CLOUD_ID
            )
            assert fake_external_client.num_get_cloud_calls == 1
            assert fake_external_client.num_get_cluster_calls == 0
            assert fake_external_client.num_get_cluster_compute_calls == 0

    @pytest.mark.parametrize(
        "setup_anyscale_client", [{"inside_workspace": True}], indirect=True
    )
    def test_get_from_workspace(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client
        # The cloud ID should be cached so we only make one API call.
        for _ in range(100):
            assert (
                anyscale_client.get_cloud_id()
                == FakeExternalAPIClient.WORKSPACE_CLOUD_ID
            )
            # get_cloud isn't called because it's from the workspace instead.
            assert fake_external_client.num_get_cloud_calls == 0
            assert fake_external_client.num_get_cluster_calls == 1
            assert fake_external_client.num_get_cluster_compute_calls == 1

    def test_get_from_compute_config_id(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client
        fake_external_client.set_cluster_compute_mapping(
            "fake-compute-config-id",
            ClusterCompute(
                name="fake-compute-config",
                id="fake-compute-config-id",
                config=ClusterComputeConfig(
                    cloud_id="compute-config-cloud-id",
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

        assert (
            anyscale_client.get_cloud_id(compute_config_id="fake-compute-config-id")
            == "compute-config-cloud-id"
        )

    def test_get_by_name(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, fake_internal_client, _, _, _ = setup_anyscale_client
        with pytest.raises(RuntimeError, match="Cloud 'does-not-exist' not found."):
            anyscale_client.get_cloud_id(cloud_name="does-not-exist")

        fake_internal_client.add_cloud(
            Cloud(
                name="test-cloud",
                id="test-cloud-id",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

        # The cloud ID should be cached so we only make one API call.
        num_get_cloud_calls_before = fake_internal_client.num_get_cloud_calls
        for _ in range(100):
            assert (
                anyscale_client.get_cloud_id(cloud_name="test-cloud") == "test-cloud-id"
            )
            assert (
                fake_internal_client.num_get_cloud_calls
                == num_get_cloud_calls_before + 1
            )


class TestGetProjectID:
    def test_get_default(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client

        # The project ID should be cached so we only make one API call.
        for _ in range(100):
            cloud_id = anyscale_client.get_cloud_id()
            assert (
                anyscale_client.get_project_id(parent_cloud_id=cloud_id)
                == FakeExternalAPIClient.DEFAULT_PROJECT_ID
            )
            assert fake_external_client.num_get_project_calls == 1

        # Calling with a different parent_cloud_id triggers an API call
        assert (
            anyscale_client.get_project_id(parent_cloud_id="new_cloud_id")
            == FakeExternalAPIClient.DEFAULT_PROJECT_ID
        )
        assert fake_external_client.num_get_project_calls == 2

        # Calling with original cloud_id doesn't trigger any new API call because the
        # associated default project ID is already cached from first get_project_id call
        assert (
            anyscale_client.get_project_id(parent_cloud_id=cloud_id)
            == FakeExternalAPIClient.DEFAULT_PROJECT_ID
        )
        assert fake_external_client.num_get_project_calls == 2

    @pytest.mark.parametrize(
        "setup_anyscale_client", [{"inside_workspace": True}], indirect=True
    )
    def test_get_from_workspace(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client
        cloud_id = anyscale_client.get_cloud_id()
        assert (
            anyscale_client.get_project_id(parent_cloud_id=cloud_id)
            == FakeExternalAPIClient.WORKSPACE_PROJECT_ID
        )


class TestComputeConfig:
    def test_get_default_compute_config_id(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client
        assert (
            anyscale_client.get_compute_config_id()
            == FakeExternalAPIClient.DEFAULT_CLUSTER_COMPUTE_ID
        )

    @pytest.mark.parametrize(
        "setup_anyscale_client", [{"inside_workspace": True}], indirect=True,
    )
    def test_get_compute_config_id_from_workspace(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, fake_internal_client, _, _, _ = setup_anyscale_client
        fake_internal_client.add_compute_template(
            DecoratedComputeTemplate(
                id=FakeExternalAPIClient.WORKSPACE_CLUSTER_COMPUTE_ID,
                config=ClusterComputeConfig(
                    head_node_type=ComputeNodeType(
                        instance_type="g4dn.4xlarge",
                        local_vars_configuration=OPENAPI_NO_VALIDATION,
                    ),
                    auto_select_worker_config=False,
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )
        assert (
            anyscale_client.get_compute_config_id()
            == FakeExternalAPIClient.WORKSPACE_CLUSTER_COMPUTE_ID
        )

    @pytest.mark.parametrize(
        "setup_anyscale_client", [{"inside_workspace": True}], indirect=True,
    )
    def test_get_compute_config_id_from_workspace_with_auto_select_override(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, fake_internal_client, _, _, _ = setup_anyscale_client

        # Configure the workspace to run with a compute configuration with
        # auto_select_worker_config enabled & a head node that is a GPU.
        fake_internal_client.add_compute_template(
            DecoratedComputeTemplate(
                id=FakeExternalAPIClient.WORKSPACE_CLUSTER_COMPUTE_ID,
                config=ClusterComputeConfig(
                    head_node_type=ComputeNodeType(
                        instance_type="g4dn.4xlarge",
                        local_vars_configuration=OPENAPI_NO_VALIDATION,
                    ),
                    auto_select_worker_config=True,
                    flags={"max-gpus": 10,},
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        compute_config_id = anyscale_client.get_compute_config_id()

        # We expect that the resolved ID is not the default compute config ID
        # and is not the workspace compute config ID (it should be a new anon
        # compute config).
        assert compute_config_id is not None
        assert compute_config_id != FakeExternalAPIClient.DEFAULT_CLUSTER_COMPUTE_ID
        assert compute_config_id != FakeExternalAPIClient.WORKSPACE_CLUSTER_COMPUTE_ID

        # Retrieve the newly created compute config.
        compute_config = anyscale_client.get_compute_config(compute_config_id)
        assert compute_config is not None

        # Assert that we have switched over to a standard compute config.
        #   - Auto select worker config has been enabled.
        #   - The head node type should be standardized.
        #   - Scheduling should be disabled on the head node.
        assert compute_config.config.auto_select_worker_config
        assert (
            compute_config.config.head_node_type.instance_type
            == FakeExternalAPIClient.DEFAULT_CLUSTER_COMPUTE_HEAD_NODE_INSTANCE_TYPE
        )
        assert compute_config.config.head_node_type.resources["CPU"] == 0

    def test_get_compute_config_id_by_name_not_found(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, fake_internal_client, _, _, _ = setup_anyscale_client
        assert (
            anyscale_client.get_compute_config_id(compute_config_name="fake-news")
            is None
        )

    def test_get_compute_config_id_by_name(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, fake_internal_client, _, _, _ = setup_anyscale_client
        fake_internal_client.add_compute_template(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        assert (
            anyscale_client.get_compute_config_id("fake-compute-config-name")
            == "fake-compute-config-id"
        )

        assert anyscale_client.get_compute_config_id("does-not-exist") is None

    def test_get_compute_config_id_by_name_versioned(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, fake_internal_client, _, _, _ = setup_anyscale_client
        fake_internal_client.add_compute_template(
            DecoratedComputeTemplate(
                id="fake-compute-config-id-1",
                name="fake-compute-config-name",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        fake_internal_client.add_compute_template(
            DecoratedComputeTemplate(
                id="fake-compute-config-id-2",
                name="fake-compute-config-name",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

        # Get `version=1` by name.
        assert (
            anyscale_client.get_compute_config_id("fake-compute-config-name:1")
            == "fake-compute-config-id-1"
        )

        # Get latest version (no version string passed).
        assert (
            anyscale_client.get_compute_config_id("fake-compute-config-name")
            == "fake-compute-config-id-2"
        )

    def test_get_compute_config(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, fake_internal_client, _, _, _ = setup_anyscale_client
        fake_internal_client.add_compute_template(
            DecoratedComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config-name",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        assert anyscale_client.get_compute_config("does-not-exist") is None
        assert (
            anyscale_client.get_compute_config("fake-compute-config-id").name
            == "fake-compute-config-name"
        )

    def test_create_compute_config(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client

        config = ComputeTemplateConfig(
            cloud_id="fake-cloud-id", local_vars_configuration=OPENAPI_NO_VALIDATION,
        )

        # Name provided.
        _, compute_config_id_1 = anyscale_client.create_compute_config(
            config, name="test-name"
        )
        compute_config_1 = anyscale_client.get_compute_config(compute_config_id_1)
        assert compute_config_1 is not None
        assert not compute_config_1.anonymous
        assert compute_config_1.name == "test-name"
        assert compute_config_1.id == compute_config_id_1
        assert compute_config_1.config == config

        # No name provided -- anonymous compute config.
        _, compute_config_id_2 = anyscale_client.create_compute_config(config)
        assert compute_config_id_2 != compute_config_id_1
        compute_config_2 = anyscale_client.get_compute_config(compute_config_id_2)
        assert compute_config_2 is not None
        assert compute_config_2.anonymous
        assert compute_config_2.name.startswith("anonymous-")
        assert compute_config_2.id == compute_config_id_2
        assert compute_config_2.config == config

    def test_create_compute_config_versioning(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client

        config = ComputeTemplateConfig(
            cloud_id="fake-cloud-id", local_vars_configuration=OPENAPI_NO_VALIDATION,
        )

        # Create first version.
        full_name_1, compute_config_id_1 = anyscale_client.create_compute_config(
            config, name="test-name"
        )
        assert full_name_1 == "test-name:1"

        compute_config_1 = anyscale_client.get_compute_config(compute_config_id_1)
        assert compute_config_1 is not None
        assert not compute_config_1.anonymous
        assert compute_config_1.name == "test-name"
        assert compute_config_1.id == compute_config_id_1
        assert compute_config_1.config == config
        assert compute_config_1.version == 1

        # Create second version.
        full_name_2, compute_config_id_2 = anyscale_client.create_compute_config(
            config, name="test-name"
        )
        assert full_name_2 == "test-name:2"

        compute_config_2 = anyscale_client.get_compute_config(compute_config_id_2)
        assert compute_config_2 is not None
        assert not compute_config_2.anonymous
        assert compute_config_2.name == "test-name"
        assert compute_config_2.id == compute_config_id_2
        assert compute_config_2.config == config
        assert compute_config_2.version == 2

    def test_archive_compute_config(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client

        config = ComputeTemplateConfig(
            cloud_id="fake-cloud-id", local_vars_configuration=OPENAPI_NO_VALIDATION,
        )

        full_name, compute_config_id = anyscale_client.create_compute_config(
            config, name="test-name"
        )
        assert full_name == "test-name:1"
        assert anyscale_client.get_compute_config_id("test-name") == compute_config_id
        assert anyscale_client.get_compute_config_id(full_name) == compute_config_id

        compute_config = anyscale_client.get_compute_config(compute_config_id)
        assert compute_config is not None
        assert not compute_config.anonymous
        assert compute_config.name == "test-name"
        assert compute_config.id == compute_config_id
        assert compute_config.config == config
        assert compute_config.version == 1
        assert compute_config.archived_at is None

        # Archive the compute config.
        anyscale_client.archive_compute_config(compute_config_id=compute_config_id)

        # Compute config should no longer be found by name unless include_archived is passed.
        assert anyscale_client.get_compute_config_id(full_name) is None
        assert (
            anyscale_client.get_compute_config_id(full_name, include_archived=True)
            == compute_config_id
        )

        # Compute config should be able to be fetched by ID.
        archived_compute_config = anyscale_client.get_compute_config(compute_config_id)
        assert archived_compute_config is not None
        assert not archived_compute_config.anonymous
        assert archived_compute_config.name == "test-name"
        assert archived_compute_config.id == compute_config_id
        assert archived_compute_config.config == config
        assert archived_compute_config.version == 1
        assert archived_compute_config.archived_at is not None


class TestClusterEnv:
    def test_get_cluster_env_build_id_from_containerfile_reused_cluster_env(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, logger, _, _ = setup_anyscale_client
        containerfile = "FROM anyscale/ray:2.9.3\nRUN pip install -U flask\n"
        existing_cluster_env_name = "fake-cluster-env"
        existing_cluster_env_id = "fake-cluster-env-id"
        fake_external_client.set_cluster_env(
            existing_cluster_env_id,
            ClusterEnvironment(
                id=existing_cluster_env_id,
                name=existing_cluster_env_name,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        build_id = anyscale_client.get_cluster_env_build_id_from_containerfile(
            cluster_env_name=existing_cluster_env_name, containerfile=containerfile
        )

        build = fake_external_client.get_cluster_environment_build(build_id).result
        assert build.containerfile == containerfile
        assert build.cluster_environment_id == existing_cluster_env_id
        assert "Building image..." not in logger.info_messages

    def test_get_cluster_env_build_id_from_containerfile_reused_both_cluster_env_and_build(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, logger, _, _ = setup_anyscale_client
        containerfile = "FROM anyscale/ray:2.9.3\nRUN pip install -U flask\n"
        existing_build_id = "fake-cluster-env-build-id"
        existing_cluster_env_name = "fake-cluster-env"
        existing_cluster_env_id = "fake-cluster-env-id"
        fake_external_client.set_cluster_env(
            existing_cluster_env_id,
            ClusterEnvironment(
                id=existing_cluster_env_id,
                name=existing_cluster_env_name,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        fake_external_client.set_cluster_env_build(
            existing_build_id,
            ClusterEnvironmentBuild(
                id=existing_build_id,
                cluster_environment_id=existing_cluster_env_id,
                containerfile=containerfile,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
                status=ClusterEnvironmentBuildStatus.SUCCEEDED,
            ),
        )
        build_id = anyscale_client.get_cluster_env_build_id_from_containerfile(
            cluster_env_name=existing_cluster_env_name, containerfile=containerfile
        )

        build = fake_external_client.get_cluster_environment_build(build_id).result
        assert build.containerfile == containerfile
        assert build.cluster_environment_id == existing_cluster_env_id
        assert build.id == existing_build_id
        assert "Building image..." not in logger.info_messages

    @pytest.mark.parametrize("mark_build_fail", [True, False])
    @pytest.mark.parametrize(
        "setup_anyscale_client",
        [{"sleep": lambda x: print(f"Mock sleep {x} seconds.")},],
        indirect=True,
    )
    def test_get_cluster_env_build_id_from_containerfile(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
        mark_build_fail: bool,
    ):
        build_id = "bld_1"  # fake external client implements the build id by simply incrementing the number.
        anyscale_client, fake_external_client, _, logger, _, _ = setup_anyscale_client
        containerfile = "FROM anyscale/ray:2.9.3\nRUN pip install -U flask\n"

        if mark_build_fail:
            fake_external_client.mark_cluster_env_build_to_fail(
                build_id, after_iterations=10,
            )
            with pytest.raises(
                RuntimeError, match="Image build bld_1 failed.",
            ):
                build_id = anyscale_client.get_cluster_env_build_id_from_containerfile(
                    cluster_env_name="fake-cluster-env", containerfile=containerfile
                )
            assert (
                "Building image... See details: https://anyscale-test.com/v2/container-images/apt_1/versions/bld_1."
                in logger.info_messages
            )
        else:
            build_id = anyscale_client.get_cluster_env_build_id_from_containerfile(
                cluster_env_name="fake-cluster-env", containerfile=containerfile
            )

            build = fake_external_client.get_cluster_environment_build(build_id).result
            assert build.containerfile == containerfile
            assert build.status == ClusterEnvironmentBuildStatus.SUCCEEDED
            assert (
                "Building image... See details: https://anyscale-test.com/v2/container-images/apt_1/versions/bld_1."
                in logger.info_messages
            )
            assert "Image build succeeded." in logger.info_messages

    def test_get_cluster_env_build_id_image_uri(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client
        image_uri = ImageURI.from_str("docker.us.com/my/fakeimage:latest")
        build_id = anyscale_client.get_cluster_env_build_id_from_image_uri(image_uri)

        build = fake_external_client.get_cluster_environment_build(build_id).result
        assert build.docker_image_name == str(image_uri)
        assert (
            fake_external_client.get_cluster_environment(
                build.cluster_environment_id
            ).result.name
            == image_uri.to_cluster_env_name()
        )

    def test_get_cluster_env_build_id_image_uri_build_same_cluster_env_reused(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        image_uri = ImageURI.from_str("my/fakeimage:latest")
        build_id = "fake-cluster-env-build-id"
        cluster_env_id = "fake-cluster-env-id"
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client
        fake_external_client.set_cluster_env_build(
            build_id,
            ClusterEnvironmentBuild(
                id=build_id,
                cluster_environment_id="fake-cluster-env-id",
                docker_image_name=image_uri,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        fake_external_client.set_cluster_env(
            cluster_env_id,
            ClusterEnvironment(
                id=cluster_env_id,
                name=image_uri.to_cluster_env_name(),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        build_id = anyscale_client.get_cluster_env_build_id_from_image_uri(image_uri)

        build = fake_external_client.get_cluster_environment_build(build_id).result
        assert build.id == build_id  # it should match the existing build id
        assert build.docker_image_name == str(
            image_uri
        )  # it should match the existing image uri
        assert (
            build.cluster_environment_id == cluster_env_id
        )  # it should match the existing cluster env id

    def test_get_cluster_env_build_id_image_uri_same_cluster_env_but_diff_image_uri(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client
        cluster_env_id = "fake-cluster-env-id"
        image_uri = ImageURI.from_str("docker.us.com/my/fakeimage:latest")
        existing_build_id = "fake-cluster-env-build-id"

        fake_external_client.set_cluster_env(
            cluster_env_id,
            ClusterEnvironment(
                id=cluster_env_id,
                name=image_uri.to_cluster_env_name(),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

        fake_external_client.set_cluster_env_build(
            existing_build_id,
            ClusterEnvironmentBuild(
                id=existing_build_id,
                cluster_environment_id=cluster_env_id,
                docker_image_name="different_image_uri",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

        build_id = anyscale_client.get_cluster_env_build_id_from_image_uri(image_uri)

        assert build_id != existing_build_id

        build = fake_external_client.get_cluster_environment_build(build_id).result
        assert build.docker_image_name == str(image_uri)
        assert (
            fake_external_client.get_cluster_environment(
                build.cluster_environment_id
            ).result.name
            == image_uri.to_cluster_env_name()
        )

    @pytest.mark.parametrize(
        ("found", "successful_build"),
        [
            (True, True),
            (True, False),
            (False, False),  # if not found, successful_build is not used
        ],
    )
    def test_get_cluster_env_build_id_from_image_uri_legacy_cluster_env(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
        found: bool,
        successful_build: bool,
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client
        legacy_image_uri = ImageURI.from_str("anyscale/image/fake-cluster-env-name:5")
        assert legacy_image_uri.is_cluster_env_image()
        if found:
            fake_external_client.set_cluster_env(
                "fake-cluster-env-id",
                ClusterEnvironment(
                    name="fake-cluster-env-name",
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
            )
            fake_external_client.set_cluster_env_build(
                "fake-cluster-env-build-id",
                ClusterEnvironmentBuild(
                    id="fake-cluster-env-build-id",
                    cluster_environment_id="fake-cluster-env-id",
                    revision=5,
                    docker_image_name="anyscale/ray:2.9.3",
                    status=ClusterEnvironmentBuildStatus.SUCCEEDED
                    if successful_build
                    else ClusterEnvironmentBuildStatus.FAILED,
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
            )
            if successful_build:
                build_id = anyscale_client.get_cluster_env_build_id_from_image_uri(
                    legacy_image_uri
                )
                assert build_id == "fake-cluster-env-build-id"
            else:
                with pytest.raises(
                    RuntimeError,
                    match="Legacy cluster environment build 'fake-cluster-env-name:5' is not a successful build.",
                ):
                    anyscale_client.get_cluster_env_build_id_from_image_uri(
                        legacy_image_uri
                    )
        else:
            with pytest.raises(
                RuntimeError,
                match="Legacy cluster environment 'fake-cluster-env-name:5' is not found.",
            ):
                anyscale_client.get_cluster_env_build_id_from_image_uri(
                    legacy_image_uri
                )

    def test_get_default_build_id(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client
        assert (
            anyscale_client.get_default_build_id()
            == FakeExternalAPIClient.DEFAULT_CLUSTER_ENV_BUILD_ID
        )

    @pytest.mark.parametrize(
        "setup_anyscale_client",
        [{"inside_workspace": True, "workspace_dependency_tracking_disabled": True},],
        indirect=True,
    )
    def test_get_default_build_id_from_workspace(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client
        assert (
            anyscale_client.get_default_build_id()
            == FakeExternalAPIClient.WORKSPACE_CLUSTER_ENV_BUILD_ID
        )

    def test_get_cluster_env_name(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client
        fake_external_client.set_cluster_env(
            "fake-cluster-env-id",
            ClusterEnvironment(
                name="fake-cluster-env-name",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        fake_external_client.set_cluster_env_build(
            "fake-cluster-env-build-id",
            ClusterEnvironmentBuild(
                cluster_environment_id="fake-cluster-env-id",
                revision=5,
                docker_image_name="anyscale/ray:2.9.3",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )
        assert anyscale_client.get_cluster_env_build_image_uri("does-not-exist") is None
        assert anyscale_client.get_cluster_env_build_image_uri(
            "fake-cluster-env-build-id"
        ) == ImageURI.from_str("anyscale/image/fake-cluster-env-name:5")


class TestUploadLocalDirToCloudStorage:
    @pytest.mark.parametrize("working_dir", TEST_WORKING_DIRS)
    def test_basic(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
        fake_requests: FakeRequests,
        working_dir: str,
    ):
        anyscale_client, _, fake_internal_client, _, _, _ = setup_anyscale_client
        uri = anyscale_client.upload_local_dir_to_cloud_storage(
            working_dir, cloud_id="test-cloud-id",
        )
        assert isinstance(uri, str) and len(uri) > 0
        assert fake_requests.called_method == "PUT"
        assert (
            fake_requests.called_url is not None
            and fake_requests.called_url.startswith(
                fake_internal_client.FAKE_UPLOAD_URL_PREFIX
            )
        )
        assert fake_requests.sent_data is not None and len(fake_requests.sent_data) > 0

    def test_missing_dir(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client
        with pytest.raises(
            RuntimeError, match="Path 'does_not_exist' is not a valid directory."
        ):
            anyscale_client.upload_local_dir_to_cloud_storage(
                "does_not_exist", cloud_id="test-cloud-id",
            )

    def test_uri_content_addressed(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
        fake_requests: FakeRequests,
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client

        # Uploading the same directory contents should result in the same content-addressed URI.
        uri1 = anyscale_client.upload_local_dir_to_cloud_storage(
            BASIC_WORKING_DIR, cloud_id="test-cloud-id",
        )
        uri2 = anyscale_client.upload_local_dir_to_cloud_storage(
            BASIC_WORKING_DIR, cloud_id="test-cloud-id",
        )
        assert uri1 == uri2

        # Uploading a different directory should not result in the same content-addressed URI.
        uri3 = anyscale_client.upload_local_dir_to_cloud_storage(
            NESTED_WORKING_DIR, cloud_id="test-cloud-id",
        )
        assert uri3 not in (uri1, uri2)

    @pytest.mark.parametrize("overwrite", [False, True])
    def test_overwrite_existing_file(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
        fake_requests: FakeRequests,
        overwrite: bool,
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client

        uri1 = anyscale_client.upload_local_dir_to_cloud_storage(
            BASIC_WORKING_DIR,
            cloud_id="test-cloud-id",
            overwrite_existing_file=overwrite,
        )
        uri1_data = fake_requests.sent_data
        assert uri1_data is not None and len(uri1_data) > 0

        fake_requests.reset()

        # Re-upload the same directory (which will have the same content-addressable URI).
        # If `overwrite_existing_file` is true, it should be re-uploaded, else it shouldn't be.
        uri2 = anyscale_client.upload_local_dir_to_cloud_storage(
            BASIC_WORKING_DIR,
            cloud_id="test-cloud-id",
            overwrite_existing_file=overwrite,
        )
        assert uri2 == uri1

        uri2_data = fake_requests.sent_data
        if overwrite:
            assert uri2_data == uri1_data
        else:
            assert uri2_data is None

    def test_excludes(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
        fake_requests: FakeRequests,
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client

        # No exclusions.
        uri1 = anyscale_client.upload_local_dir_to_cloud_storage(
            NESTED_WORKING_DIR, cloud_id="test-cloud-id",
        )

        # Exclusions that don't match anything.
        uri2 = anyscale_client.upload_local_dir_to_cloud_storage(
            NESTED_WORKING_DIR, cloud_id="test-cloud-id", excludes=["does-not-exist"],
        )

        assert uri1 == uri2

        # Exclude a subdirectory.
        uri3 = anyscale_client.upload_local_dir_to_cloud_storage(
            NESTED_WORKING_DIR, cloud_id="test-cloud-id", excludes=["subdir"],
        )

        assert uri3 != uri1

        # Exclude requirements.txt by name.
        uri4 = anyscale_client.upload_local_dir_to_cloud_storage(
            NESTED_WORKING_DIR, cloud_id="test-cloud-id", excludes=["requirements.txt"],
        )

        assert uri4 not in (uri3, uri1)

        # Exclude requirements.txt by wildcard.
        uri5 = anyscale_client.upload_local_dir_to_cloud_storage(
            NESTED_WORKING_DIR, cloud_id="test-cloud-id", excludes=["*.txt"],
        )

        assert uri5 == uri4


def _make_apply_service_model(
    name: str,
    *,
    version: Optional[str] = None,
    canary_percent: int = 100,
    build_id: str = "fake-build-id",
    compute_config_id: str = "fake-compute-config-id",
) -> ServiceModel:
    return ApplyServiceModel(
        name=name,
        version=version,
        canary_percent=canary_percent,
        build_id=build_id,
        compute_config_id=compute_config_id,
        local_vars_configuration=OPENAPI_NO_VALIDATION,
    )


class TestGetService:
    def test_get_service_none_returned(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, _, _, _, _ = setup_anyscale_client
        assert anyscale_client.get_service("test-service-name") is None

    def test_get_service_one_returned_matches(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client
        fake_external_client.rollout_service(
            _make_apply_service_model("test-service-name")
        )

        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model is not None
        assert returned_model.name == "test-service-name"

    def test_get_service_multiple_returned_one_matches(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client
        fake_external_client.rollout_service(
            _make_apply_service_model("test-service-name")
        )
        for i in range(5):
            fake_external_client.rollout_service(
                _make_apply_service_model(f"other-service-name-{i}")
            )

        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model is not None
        assert returned_model.name == "test-service-name"

    def test_get_service_many_pages(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client
        fake_external_client.rollout_service(
            _make_apply_service_model("test-service-name")
        )
        for i in range((10 * anyscale_client.LIST_ENDPOINT_COUNT) + 5):
            fake_external_client.rollout_service(
                _make_apply_service_model(f"other-service-name-{i}")
            )

        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model is not None
        assert returned_model.name == "test-service-name"


class TestRolloutAndRollback:
    def test_basic_rollout(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client

        # First rollout a new service and complete the rollout.
        fake_external_client.rollout_service(
            _make_apply_service_model("test-service-name", build_id="build-id-1")
        )
        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model.name == "test-service-name"
        assert returned_model.primary_version.build_id == "build-id-1"
        assert returned_model.current_state == ServiceEventCurrentState.STARTING

        fake_external_client.complete_rollout("test-service-name")
        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model.name == "test-service-name"
        assert returned_model.primary_version.build_id == "build-id-1"
        assert returned_model.current_state == ServiceEventCurrentState.RUNNING

        # Now rollout to a new version and complete the rollout.
        fake_external_client.rollout_service(
            _make_apply_service_model("test-service-name", build_id="build-id-2")
        )
        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model.name == "test-service-name"
        assert returned_model.primary_version.build_id == "build-id-1"
        assert returned_model.canary_version.build_id == "build-id-2"
        assert returned_model.current_state == ServiceEventCurrentState.ROLLING_OUT

        fake_external_client.complete_rollout("test-service-name")
        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model.name == "test-service-name"
        assert returned_model.primary_version.build_id == "build-id-2"
        assert returned_model.current_state == ServiceEventCurrentState.RUNNING

    def test_basic_rollback(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client

        # First rollout a new service and complete the rollout.
        fake_external_client.rollout_service(
            _make_apply_service_model("test-service-name", build_id="build-id-1")
        )
        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model.name == "test-service-name"
        assert returned_model.primary_version.build_id == "build-id-1"
        assert returned_model.current_state == ServiceEventCurrentState.STARTING

        fake_external_client.complete_rollout("test-service-name")
        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model.name == "test-service-name"
        assert returned_model.primary_version.build_id == "build-id-1"
        assert returned_model.current_state == ServiceEventCurrentState.RUNNING

        # Now rollout to a new version and then rollback.
        fake_external_client.rollout_service(
            _make_apply_service_model("test-service-name", build_id="build-id-2")
        )
        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model.name == "test-service-name"
        assert returned_model.primary_version.build_id == "build-id-1"
        assert returned_model.canary_version.build_id == "build-id-2"
        assert returned_model.current_state == ServiceEventCurrentState.ROLLING_OUT

        returned_model = anyscale_client.rollback_service(returned_model.id)
        assert returned_model.name == "test-service-name"
        assert returned_model.primary_version.build_id == "build-id-1"
        assert returned_model.primary_version.weight == 100
        assert returned_model.current_state == ServiceEventCurrentState.ROLLING_BACK

        fake_external_client.complete_rollback("test-service-name")
        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model.name == "test-service-name"
        assert returned_model.primary_version.build_id == "build-id-1"
        assert returned_model.primary_version.weight == 100
        assert returned_model.current_state == ServiceEventCurrentState.RUNNING

    def test_terminate(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client

        # First rollout a new service and complete the rollout.
        fake_external_client.rollout_service(
            _make_apply_service_model("test-service-name", build_id="build-id-1")
        )
        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model.name == "test-service-name"
        assert returned_model.primary_version.build_id == "build-id-1"
        assert returned_model.current_state == ServiceEventCurrentState.STARTING

        fake_external_client.complete_rollout("test-service-name")
        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model.name == "test-service-name"
        assert returned_model.primary_version.build_id == "build-id-1"
        assert returned_model.current_state == ServiceEventCurrentState.RUNNING

        # Now terminate the service.
        returned_model = anyscale_client.terminate_service(returned_model.id)
        assert returned_model.name == "test-service-name"
        assert returned_model.primary_version is None
        assert returned_model.current_state == ServiceEventCurrentState.TERMINATING

        fake_external_client.complete_termination("test-service-name")
        returned_model = anyscale_client.get_service("test-service-name")
        assert returned_model.name == "test-service-name"
        assert returned_model.primary_version is None
        assert returned_model.current_state == ServiceEventCurrentState.TERMINATED


def _make_create_job_model(
    name: str,
    entrypoint: str,
    *,
    max_retries: int = 1,
    runtime_env: Optional[Dict[str, Any]] = None,
    project_id: str = "fake-project-id",
    workspace_id: Optional[str] = None,
    build_id: str = "fake-build-id",
    compute_config_id: str = "fake-compute-config-id",
) -> CreateInternalProductionJob:
    return CreateInternalProductionJob(
        name=name,
        project_id=project_id,
        workspace_id=workspace_id,
        config=ProductionJobConfig(
            entrypoint=entrypoint,
            build_id=build_id,
            compute_config_id=compute_config_id,
            max_retries=max_retries,
            runtime_env=runtime_env,
        ),
        local_vars_configuration=OPENAPI_NO_VALIDATION,
    )


class TestSubmitJob:
    def test_basic(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, _, fake_internal_client, _, _, _ = setup_anyscale_client

        job = anyscale_client.submit_job(
            _make_create_job_model(name="test-job", entrypoint="python main.py"),
        )
        assert job

        created_job = fake_internal_client.get_job(job.id)
        assert created_job is not None
        assert created_job.id == job.id
        assert created_job.name == "test-job"
        assert created_job.config.entrypoint == "python main.py"


class TestJobRunStatus:
    def test_basic(
        self,
        setup_anyscale_client: Tuple[
            AnyscaleClient,
            FakeExternalAPIClient,
            FakeInternalAPIClient,
            TestLogger,
            FakeAWSS3Client,
            FakeGCPGCSClient,
        ],
    ):
        anyscale_client, fake_external_client, _, _, _, _ = setup_anyscale_client

        FAILED_JOB_RUN = APIJobRun(
            id="job-run-id-1",
            ray_session_name="job-run-ray-session-id",
            ray_job_id="job-run-ray-job-id-1",
            status=BackendJobStatus.FAILED,
            created_at=datetime.now(),
            cluster_id="job-run-cluster-id",
            runtime_environment_id="job-run-runtime-environment-id",
            creator_id="job-run-creator-id",
            name="job-run-name-1",
        )
        SUCCEEDED_JOB_RUN = APIJobRun(
            id="job-run-id-2",
            ray_session_name="job-run-ray-session-id",
            ray_job_id="job-run-ray-job-id-2",
            status=BackendJobStatus.SUCCEEDED,
            created_at=FAILED_JOB_RUN.created_at + timedelta(minutes=5),
            cluster_id="job-run-cluster-id",
            runtime_environment_id="job-run-runtime-environment-id",
            creator_id="job-run-creator-id",
            name="job-run-name-2",
        )

        job_runs = [
            SUCCEEDED_JOB_RUN,
            FAILED_JOB_RUN,
        ]

        ha_job_id = "test-job-id"
        fake_external_client._job_runs[ha_job_id] = job_runs

        result = anyscale_client.get_job_runs(ha_job_id)
        assert len(result) == 2
        assert result[0] == FAILED_JOB_RUN
        assert result[1] == SUCCEEDED_JOB_RUN
