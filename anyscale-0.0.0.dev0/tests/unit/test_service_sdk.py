import copy
from dataclasses import dataclass
import pathlib
import re
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid

from common import (
    MULTI_LINE_REQUIREMENTS,
    OPENAPI_NO_VALIDATION,
    RequirementsFile,
    SINGLE_LINE_REQUIREMENTS,
    TEST_COMPUTE_CONFIG_DICT,
    TEST_CONTAINERFILE,
    TEST_REQUIREMENTS_FILES,
    TestLogger,
)
import pytest

from anyscale._private.anyscale_client import (
    FakeAnyscaleClient,
    WORKSPACE_CLUSTER_NAME_PREFIX,
)
from anyscale._private.models.image_uri import ImageURI
from anyscale._private.sdk.timer import FakeTimer
from anyscale.client.openapi_client.models import (
    Cloud,
    ComputeNodeType,
    ComputeTemplate,
    ComputeTemplateConfig,
)
from anyscale.compute_config import ComputeConfig, HeadNodeConfig
from anyscale.sdk.anyscale_client.models import (
    AccessConfig,
    ApplyServiceModel,
    ProductionServiceV2VersionModel,
    RayGCSExternalStorageConfig as ExternalAPIRayGCSExternalStorageConfig,
    ServiceConfig as ExternalAPIServiceConfig,
    ServiceEventCurrentState,
    ServiceModel,
    ServiceVersionState as ExternalAPIServiceVersionState,
)
from anyscale.service._private.service_sdk import ServiceSDK
from anyscale.service.models import (
    RayGCSExternalStorageConfig,
    ServiceConfig,
    ServiceState,
    ServiceStatus,
    ServiceVersionState,
    ServiceVersionStatus,
)
from anyscale.utils.workspace_notification import (
    WorkspaceNotification,
    WorkspaceNotificationAction,
)


@pytest.fixture()
def sdk_with_fakes() -> Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer]:
    timer = FakeTimer()
    logger = TestLogger()
    fake_client = FakeAnyscaleClient()
    return (
        ServiceSDK(client=fake_client, logger=logger, timer=timer),
        fake_client,
        logger,
        timer,
    )


class TestDeploy:
    def test_validation(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}], name="test-service-name"
        )

        with pytest.raises(TypeError):
            sdk.deploy(config, in_place="in_place")

        with pytest.raises(TypeError):
            sdk.deploy(config, canary_percent="10")

        with pytest.raises(ValueError):
            sdk.deploy(config, canary_percent=-1)

        with pytest.raises(ValueError):
            sdk.deploy(config, canary_percent=101)

        with pytest.raises(TypeError):
            sdk.deploy(config, max_surge_percent="10")

        with pytest.raises(ValueError):
            sdk.deploy(config, max_surge_percent=-1)

        with pytest.raises(ValueError):
            sdk.deploy(config, max_surge_percent=101)

    def test_basic(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}], name="test-service-name"
        )
        sdk.deploy(config)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ray_serve_config={"applications": config.applications},
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

    def test_custom_image_from_containerfile(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_containerfile = pathlib.Path(TEST_CONTAINERFILE).read_text()
        fake_client.set_containerfile_mapping(fake_containerfile, "bld_1234")
        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            containerfile=TEST_CONTAINERFILE,
        )
        sdk.deploy(config)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id="bld_1234",
            compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ray_serve_config={"applications": config.applications},
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

    def test_custom_image_from_image_uri(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_image_uri_mapping(
            ImageURI.from_str("docker.io/user/my-custom-image:latest"), "bld_123"
        )

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            image_uri="docker.io/user/my-custom-image:latest",
        )
        sdk.deploy(config)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id="bld_123",
            compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ray_serve_config={"applications": config.applications},
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

        with pytest.raises(
            ValueError,
            match="The image_uri 'docker.io/user/does-not-exist:latest' does not exist.",
        ):
            sdk.deploy(config.options(image_uri="docker.io/user/does-not-exist:latest"))

    def test_custom_compute_config_name(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        fake_client.add_compute_config(
            ComputeTemplate(
                id="compute_id123",
                name="my-custom-compute-config",
                config=ComputeTemplateConfig(
                    cloud_id="test-cloud-id",
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )
        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            compute_config="my-custom-compute-config",
        )
        sdk.deploy(config)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id="compute_id123",
            ray_serve_config={"applications": config.applications},
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

        with pytest.raises(
            ValueError, match="The compute config 'does-not-exist' does not exist."
        ):
            sdk.deploy(config.options(compute_config="does-not-exist"))

    def test_custom_compute_config_dict(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        fake_client.add_cloud(
            Cloud(
                id=str(uuid.uuid4()),
                name=TEST_COMPUTE_CONFIG_DICT["cloud"],
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

        # Specify a compute config as a dictionary (anonymous).
        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            compute_config=TEST_COMPUTE_CONFIG_DICT,
        )
        sdk.deploy(config)
        anonymous_compute_config_id = fake_client.rolled_out_model.compute_config_id
        anonymous_compute_config = fake_client.get_compute_config(
            anonymous_compute_config_id
        )
        assert anonymous_compute_config.anonymous
        assert anonymous_compute_config.id == anonymous_compute_config_id
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id=anonymous_compute_config_id,
            ray_serve_config={"applications": config.applications},
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

        # Test an invalid dict.
        with pytest.raises(
            TypeError,
            match=re.escape("__init__() got an unexpected keyword argument 'bad'"),
        ):
            config = ServiceConfig(
                applications=[{"import_path": "main:app"}],
                name="test-service-name",
                compute_config={"bad": "config"},
            )
            sdk.deploy(config)

    def test_reject_changed_cloud(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        fake_client.add_cloud(
            Cloud(
                id="test-cloud-id",
                name="test-cloud",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )
        fake_client.add_compute_config(
            ComputeTemplate(
                id="compute_id123",
                name="my-custom-compute-config",
                config=ComputeTemplateConfig(
                    cloud_id="test-cloud-id",
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        fake_client.add_cloud(
            Cloud(
                id="test-other-cloud-id",
                name="test-other-cloud",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )
        fake_client.add_compute_config(
            ComputeTemplate(
                id="compute_id456",
                name="my-other-compute-config",
                config=ComputeTemplateConfig(
                    cloud_id="test-other-cloud-id",
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            compute_config="my-custom-compute-config",
        )
        sdk.deploy(config)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id="compute_id123",
            ray_serve_config={"applications": config.applications},
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

        with pytest.raises(
            ValueError,
            match="The cloud for a service cannot be changed once it's created. Service 'test-service-name' was created on cloud 'test-cloud', but the provided config is for cloud 'test-other-cloud'.",
        ):
            sdk.deploy(config.options(compute_config="my-other-compute-config"))

    def test_http_options(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            http_options={"request_timeout_s": 10.0},
        )
        sdk.deploy(config)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ray_serve_config={
                "applications": config.applications,
                "http_options": {"request_timeout_s": 10.0},
            },
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

    def test_grpc_options(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            grpc_options={"grpc_servicer_functions": ["hello.world"]},
        )
        sdk.deploy(config)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ray_serve_config={
                "applications": config.applications,
                "grpc_options": {"grpc_servicer_functions": ["hello.world"]},
            },
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

    def test_logging_config(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            logging_config={"log_level": "DEBUG"},
        )
        sdk.deploy(config)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ray_serve_config={
                "applications": config.applications,
                "logging_config": {"log_level": "DEBUG"},
            },
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

    def test_in_place(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}], name="test-service-name"
        )

        sdk.deploy(config, in_place=False)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ray_serve_config={"applications": [{"import_path": "main:app"}]},
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

        config = config.options(applications=[{"import_path": "other:app"}])
        sdk.deploy(config, in_place=True)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ray_serve_config={"applications": [{"import_path": "other:app"}]},
            rollout_strategy="IN_PLACE",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

        # Cluster-level options should be ignored, but application-level options should be applied.
        config = config.options(
            # These should be applied.
            applications=[{"import_path": "yet_other:app"}],
            working_dir="s3://remote.zip",
            requirements=["test"],
            logging_config={"log_level": "DEBUG"},
            # These should all be ignored.
            image_uri="docker.io/user/my-custom-image:latest",
            compute_config="foobar:123",
            ray_gcs_external_storage_config=RayGCSExternalStorageConfig(
                address="test.com:8000"
            ),
            query_auth_token_enabled=False,
        )
        sdk.deploy(config, in_place=True)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ray_serve_config={
                "applications": [
                    {
                        "import_path": "yet_other:app",
                        "runtime_env": {
                            "working_dir": "s3://remote.zip",
                            "pip": ["test"],
                        },
                    }
                ],
                "logging_config": {"log_level": "DEBUG"},
            },
            rollout_strategy="IN_PLACE",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

    def test_in_place_service_does_not_exist(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}], name="test-service-name"
        )

        # in_place should fail if the service doesn't already exist.
        with pytest.raises(
            RuntimeError,
            match="in_place can only be used to update running services, but no service was found with name 'test-service-name'",
        ):
            sdk.deploy(config, in_place=True)

    def test_in_place_service_terminated(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        config = ServiceConfig(
            applications=[{"import_path": "main:app"}], name="test-service-name"
        )
        sdk.deploy(config)

        sdk.terminate(name="test-service-name")
        assert sdk.status(name="test-service-name").state == ServiceState.TERMINATED

        with pytest.raises(
            RuntimeError,
            match="in_place can only be used to update running services, but service 'test-service-name' is terminated",
        ):
            sdk.deploy(config, in_place=True)

    def test_in_place_during_rollout(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        # Service must exist before in_place is allowed.
        config = ServiceConfig(
            applications=[{"import_path": "main:app"}], name="test-service-name"
        )
        sdk.deploy(config, in_place=False)

        # Update the service to mimic an ongoing rollout (canary_version is populated).
        service = fake_client.get_service(name="test-service-name")
        service.canary_version = ProductionServiceV2VersionModel(
            version="canary",
            current_state=ExternalAPIServiceVersionState.STARTING,
            weight=0,
            build_id=service.primary_version.build_id,
            compute_config_id=service.primary_version.compute_config_id,
            ray_serve_config=service.primary_version.ray_serve_config,
            ray_gcs_external_storage_config=service.primary_version.ray_gcs_external_storage_config,
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )

        with pytest.raises(
            RuntimeError,
            match="in_place updates cannot be used while a rollout is in progress. Complete the rollout or roll back first.",
        ):
            sdk.deploy(config, in_place=True)

    def test_in_place_rejects_rollout_options(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        # Service must exist before in_place is allowed.
        config = ServiceConfig(
            applications=[{"import_path": "main:app"}], name="test-service-name"
        )
        sdk.deploy(config, in_place=False)

        # in_place does not support canary_percent or max_surge_percent.
        with pytest.raises(
            ValueError,
            match="canary_percent cannot be specified when doing an in_place update",
        ):
            sdk.deploy(config, in_place=True, canary_percent=50)

        with pytest.raises(
            ValueError,
            match="max_surge_percent cannot be specified when doing an in_place update",
        ):
            sdk.deploy(config, in_place=True, max_surge_percent=50)

    def test_canary_percent(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}], name="test-service-name"
        )
        sdk.deploy(config, canary_percent=50)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ray_serve_config={"applications": config.applications},
            rollout_strategy="ROLLOUT",
            canary_percent=50,
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

    def test_max_surge_percent(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}], name="test-service-name"
        )
        sdk.deploy(config, max_surge_percent=50)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ray_serve_config={"applications": config.applications},
            rollout_strategy="ROLLOUT",
            max_surge_percent=50,
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )

    def test_disable_query_auth_token(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, logger, _ = sdk_with_fakes

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            query_auth_token_enabled=False,
        )
        sdk.deploy(config)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ray_serve_config={"applications": config.applications},
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=False),
            ),
        )

        assert not any("Bearer: " in info_msg for info_msg in logger.info_messages)

    def test_ray_gcs_external_storage_config(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            ray_gcs_external_storage_config=RayGCSExternalStorageConfig(
                address="test.com:8000"
            ),
        )
        sdk.deploy(config)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ray_serve_config={"applications": config.applications},
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
            ray_gcs_external_storage_config=ExternalAPIRayGCSExternalStorageConfig(
                enable=True,
                address="test.com:8000",
                redis_certificate_path="/etc/ssl/certs/ca-certificates.crt",
            ),
        )

    def test_workspace_notification_is_sent(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_inside_workspace(True)

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}], name="test-service-name"
        )
        sdk.deploy(config)

        service_id = fake_client.get_service("test-service-name").id
        assert fake_client.sent_workspace_notifications == [
            WorkspaceNotification(
                body="Service 'test-service-name' deployed.",
                action=WorkspaceNotificationAction(
                    type="navigate-service", title="View Service", value=service_id,
                ),
            )
        ]

    @pytest.mark.parametrize(
        ("state", "expected_prefix"),
        [
            (None, "Starting new service"),
            (ServiceEventCurrentState.TERMINATED, "Restarting existing service"),
            (ServiceEventCurrentState.RUNNING, "Updating existing service"),
        ],
    )
    def test_existing_service_logs(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        state: Optional[ServiceEventCurrentState],
        expected_prefix: str,
    ):
        sdk, fake_client, logger, _ = sdk_with_fakes

        if state is not None:
            fake_client.update_service(
                ServiceModel(
                    id="test-service-id",
                    name="test-service-name",
                    current_state=state,
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                )
            )

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}], name="test-service-name"
        )
        sdk.deploy(config)

        assert any(
            info_log.startswith(expected_prefix) for info_log in logger.info_messages
        )


class TestDeployWorkspaceDefaults:
    def test_name_defaults_to_workspace_name(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        # Happy path: workspace cluster name has the expected prefix.
        fake_client.set_inside_workspace(
            True,
            cluster_name=WORKSPACE_CLUSTER_NAME_PREFIX + "super-special-workspace-name",
        )
        config = ServiceConfig(applications=[{"import_path": "main:app"}])
        sdk.deploy(config)
        assert fake_client.rolled_out_model.name == "super-special-workspace-name"

        # Defensive path: workspace cluster name doesn't have the expected prefix.
        fake_client.set_inside_workspace(
            True, cluster_name="not-sure-how-this-happened"
        )
        config = ServiceConfig(applications=[{"import_path": "main:app"}])
        sdk.deploy(config)
        assert fake_client.rolled_out_model.name == "not-sure-how-this-happened"

    def test_pick_up_cluster_configs(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_inside_workspace(True)

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            working_dir="s3://remote.zip",
        )
        sdk.deploy(config)
        assert fake_client.rolled_out_model == ApplyServiceModel(
            name="test-service-name",
            project_id=fake_client.WORKSPACE_PROJECT_ID,
            build_id=fake_client.WORKSPACE_CLUSTER_ENV_BUILD_ID,
            compute_config_id=fake_client.WORKSPACE_CLUSTER_COMPUTE_ID,
            ray_serve_config={
                "applications": [
                    {
                        "import_path": "main:app",
                        "runtime_env": {"working_dir": "s3://remote.zip",},
                    }
                ],
            },
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=True),
            ),
        )


class TestOverrideApplicationRuntimeEnvs:
    @pytest.mark.parametrize(
        "new_py_modules", [None, [], ["A"], ["C", "D"]],
    )
    @pytest.mark.parametrize("existing_py_modules", [None, [], ["A"], ["B"]])
    def test_update_py_modules(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        new_py_modules: Optional[List[str]],
        existing_py_modules: Optional[List[str]],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        app: Dict[str, Any] = {"import_path": "main:app"}
        if existing_py_modules:
            app["runtime_env"] = {"py_modules": existing_py_modules}
        config = ServiceConfig(
            applications=[app], name="test-service-name", py_modules=new_py_modules,
        )
        sdk.deploy(config)
        applications = fake_client.rolled_out_model.ray_serve_config["applications"]

        if new_py_modules or existing_py_modules:
            if existing_py_modules is None:
                existing_py_modules = []
            if new_py_modules is None:
                new_py_modules = []
            uploaded_py_modules = [
                fake_client._upload_uri_mapping[local_dir]
                for local_dir in existing_py_modules + new_py_modules
            ]
        else:
            uploaded_py_modules = None

        if uploaded_py_modules:
            for app in applications:
                assert app["runtime_env"].get("py_modules") == uploaded_py_modules
        else:
            assert "py_modules" not in app.get("runtime_env", {})

    @pytest.mark.parametrize(
        "new_env_vars",
        [None, {}, {"A": "B"}, {"C": "D", "E": "F"}, {"K": "V1", "C": "D"}],
    )
    @pytest.mark.parametrize("existing_env_vars", [None, {}, {"K": "V"}, {"A": "B"}])
    @pytest.mark.parametrize("inside_workspace", [False, True])
    def test_update_env_vars(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        new_env_vars: Optional[Dict[str, str]],
        existing_env_vars: Optional[Dict[str, str]],
        inside_workspace: bool,
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_inside_workspace(inside_workspace)
        app: Dict[str, Any] = {"import_path": "main:app"}
        if existing_env_vars:
            app["runtime_env"] = {"env_vars": existing_env_vars}

        config = ServiceConfig(
            applications=[app], name="test-service-name", env_vars=new_env_vars,
        )
        sdk.deploy(config)
        applications = fake_client.rolled_out_model.ray_serve_config["applications"]
        for app in applications:
            if new_env_vars or existing_env_vars:
                if existing_env_vars is None:
                    existing_env_vars = {}
                if new_env_vars is None:
                    new_env_vars = {}
                assert app["runtime_env"].get("env_vars") == {
                    **existing_env_vars,
                    **new_env_vars,
                }
            else:
                assert "env_vars" not in app.get("runtime_env", {})

    @pytest.mark.parametrize("excludes_override", [None, ["override"]])
    @pytest.mark.parametrize(
        "working_dir_override", [None, "./some-local-path", "s3://some-remote-path.zip"]
    )
    @pytest.mark.parametrize("inside_workspace", [False, True])
    def test_override_working_dir_excludes(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        inside_workspace: bool,
        working_dir_override: Optional[str],
        excludes_override: Optional[List[str]],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_inside_workspace(inside_workspace)

        config = ServiceConfig(
            name="test-service-name",
            applications=[
                {"name": "no-runtime-env", "import_path": "main:app"},
                {
                    "name": "empty-runtime-env",
                    "import_path": "main:app",
                    "runtime_env": {},
                },
                {
                    "name": "other-working-dir",
                    "import_path": "main:app",
                    "runtime_env": {
                        "working_dir": "other-path/",
                        "excludes": ["existing"],
                    },
                },
                {
                    "name": "working-dir-none",
                    "import_path": "main:app",
                    # `None` should avoid workspace overriding.
                    "runtime_env": {"working_dir": None, "excludes": None},
                },
            ],
            working_dir=working_dir_override,
            excludes=excludes_override,
        )

        sdk.deploy(config)
        applications = fake_client.rolled_out_model.ray_serve_config["applications"]
        assert len(applications) == 4

        cloud_id = (
            FakeAnyscaleClient.WORKSPACE_CLOUD_ID
            if inside_workspace
            else FakeAnyscaleClient.DEFAULT_CLOUD_ID
        )
        cwd_uri = fake_client.upload_local_dir_to_cloud_storage(".", cloud_id=cloud_id)

        if working_dir_override is None and not inside_workspace:
            assert "working_dir" not in applications[0].get("runtime_env", {})
            assert "working_dir" not in applications[1]["runtime_env"]
            assert applications[2]["runtime_env"][
                "working_dir"
            ] == fake_client.upload_local_dir_to_cloud_storage(
                "other-path/", cloud_id=cloud_id,
            )
            assert applications[3]["runtime_env"]["working_dir"] is None
        elif working_dir_override is None and inside_workspace:
            assert applications[0]["runtime_env"]["working_dir"] == cwd_uri
            assert applications[1]["runtime_env"]["working_dir"] == cwd_uri
            assert applications[2]["runtime_env"][
                "working_dir"
            ] == fake_client.upload_local_dir_to_cloud_storage(
                "other-path/", cloud_id=cloud_id,
            )
            assert applications[3]["runtime_env"]["working_dir"] is None
        elif working_dir_override is not None and working_dir_override.startswith("s3"):
            assert applications[0]["runtime_env"]["working_dir"] == working_dir_override
            assert applications[1]["runtime_env"]["working_dir"] == working_dir_override
            assert applications[2]["runtime_env"]["working_dir"] == working_dir_override
            assert applications[3]["runtime_env"]["working_dir"] == working_dir_override
        else:
            override_uri = fake_client.upload_local_dir_to_cloud_storage(
                "./some-local-path", cloud_id=cloud_id
            )
            assert applications[0]["runtime_env"]["working_dir"] == override_uri
            assert applications[1]["runtime_env"]["working_dir"] == override_uri
            assert applications[2]["runtime_env"]["working_dir"] == override_uri
            assert applications[3]["runtime_env"]["working_dir"] == override_uri

        if excludes_override is None:
            assert "excludes" not in applications[0].get("runtime_env", {})
            assert "excludes" not in applications[1]["runtime_env"]
            assert applications[2]["runtime_env"]["excludes"] == ["existing"]
            assert applications[3]["runtime_env"]["excludes"] is None
        else:
            assert applications[0]["runtime_env"]["excludes"] == ["override"]
            assert applications[1]["runtime_env"]["excludes"] == ["override"]
            assert applications[2]["runtime_env"]["excludes"] == [
                "existing",
                "override",
            ]
            assert applications[3]["runtime_env"]["excludes"] == ["override"]

    @pytest.mark.parametrize(
        "enable_image_build_for_tracked_requirements", [False, True]
    )
    @pytest.mark.parametrize(
        "requirements_override",
        [None, MULTI_LINE_REQUIREMENTS.get_path(), ["override"]],
    )
    @pytest.mark.parametrize("workspace_tracking_enabled", [False, True])
    @pytest.mark.parametrize("inside_workspace", [False, True])
    def test_override_requirements(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        inside_workspace: bool,
        workspace_tracking_enabled: bool,
        requirements_override: Union[None, str, List[str]],
        enable_image_build_for_tracked_requirements: bool,
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_inside_workspace(
            inside_workspace,
            requirements_path=SINGLE_LINE_REQUIREMENTS.get_path()
            if workspace_tracking_enabled
            else None,
        )
        sdk._image_sdk._enable_image_build_for_tracked_requirements = (
            enable_image_build_for_tracked_requirements
        )
        if inside_workspace and enable_image_build_for_tracked_requirements:
            fake_client.set_image_uri_mapping(
                ImageURI.from_str("docker.io/user/my-default-image:latest"),
                fake_client.WORKSPACE_CLUSTER_ENV_BUILD_ID,
            )
            fake_client.set_containerfile_mapping(
                '# syntax=docker/dockerfile:1\nFROM docker.io/user/my-default-image:latest\nRUN pip install "pip-install-test"',
                "bld_123",
            )

        config = ServiceConfig(
            name="test-service-name",
            applications=[
                {"name": "no-runtime-env", "import_path": "main:app",},
                {
                    "name": "empty-runtime-env",
                    "import_path": "main:app",
                    "runtime_env": {},
                },
                {
                    "name": "other-requirements-file",
                    "import_path": "main:app",
                    "runtime_env": {"pip": MULTI_LINE_REQUIREMENTS.get_path()},
                },
                {
                    "name": "other-requirements-list",
                    "import_path": "main:app",
                    "runtime_env": {"pip": ["testabc", "test123"]},
                },
                {
                    "name": "requirements-none",
                    "import_path": "main:app",
                    # `None` should disable overriding with workspace default.
                    "runtime_env": {"pip": None},
                },
            ],
            requirements=requirements_override,
        )

        sdk.deploy(config)
        applications = fake_client.rolled_out_model.ray_serve_config["applications"]
        assert len(applications) == 5

        if isinstance(requirements_override, str):
            # Override with a file.
            pass
        elif isinstance(requirements_override, list):
            # Override with a list.
            pass
        elif (
            inside_workspace
            and workspace_tracking_enabled
            and not enable_image_build_for_tracked_requirements
        ):
            # Workspace default.
            expected_workspace_pip = SINGLE_LINE_REQUIREMENTS.expected_pip_list
            assert applications[0]["runtime_env"]["pip"] == expected_workspace_pip
            assert applications[1]["runtime_env"]["pip"] == expected_workspace_pip
            assert (
                applications[2]["runtime_env"]["pip"]
                == MULTI_LINE_REQUIREMENTS.expected_pip_list
            )
            assert applications[3]["runtime_env"]["pip"] == ["testabc", "test123"]
            assert applications[4]["runtime_env"]["pip"] is None
        else:
            # No overrides.
            assert "pip" not in applications[0].get("runtime_env", {})
            assert "pip" not in applications[1]["runtime_env"]
            assert (
                applications[2]["runtime_env"]["pip"]
                == MULTI_LINE_REQUIREMENTS.expected_pip_list
            )
            assert applications[3]["runtime_env"]["pip"] == ["testabc", "test123"]
            assert applications[4]["runtime_env"]["pip"] is None


class TestDeployUploadDirs:
    @pytest.mark.parametrize("inside_workspace", [False, True])
    def test_upload_basic_working_dir(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        inside_workspace: bool,
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_inside_workspace(inside_workspace)

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            working_dir=".",
        )
        original_config = copy.deepcopy(config)

        sdk.deploy(config)
        # The original config should not be modified.
        assert config == original_config

        [application] = fake_client.rolled_out_model.ray_serve_config["applications"]

        # Check that the correct cloud_id was used for the upload.
        expected_cloud_id = (
            FakeAnyscaleClient.WORKSPACE_CLOUD_ID
            if inside_workspace
            else FakeAnyscaleClient.DEFAULT_CLOUD_ID
        )
        assert application["runtime_env"]["working_dir"].startswith(
            FakeAnyscaleClient.CLOUD_BUCKET.format(cloud_id=expected_cloud_id)
        )

    def test_upload_uses_cloud_from_compute_config(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.add_compute_config(
            ComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
                config=ComputeTemplateConfig(
                    cloud_id="compute-config-cloud-id",
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
            )
        )

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            working_dir=".",
            compute_config="fake-compute-config",
        )
        sdk.deploy(config)

        [application] = fake_client.rolled_out_model.ray_serve_config["applications"]

        # Check that the correct cloud_id was used for the upload.
        expected_cloud_id = "compute-config-cloud-id"
        assert application["runtime_env"]["working_dir"].startswith(
            FakeAnyscaleClient.CLOUD_BUCKET.format(cloud_id=expected_cloud_id)
        )

    def test_upload_with_no_local_dirs(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        """Configs should be left unchanged if there are no local dirs."""
        sdk, fake_client, _, _ = sdk_with_fakes

        basic_config = ServiceConfig(
            applications=[{"import_path": "main:app"}], name="test-service-name"
        )
        sdk.deploy(basic_config)
        assert (
            fake_client.rolled_out_model.ray_serve_config["applications"]
            == basic_config.applications
        )

        config_with_requirements = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            requirements=["pip-install-test"],
        )
        sdk.deploy(config_with_requirements)
        assert fake_client.rolled_out_model.ray_serve_config["applications"] == [
            {"import_path": "main:app", "runtime_env": {"pip": ["pip-install-test"]},},
        ]

        complex_config = ServiceConfig(
            name="test-service-name",
            applications=[
                {"name": "app1", "import_path": "main:app",},
                {
                    "name": "app2",
                    "import_path": "main:app",
                    "runtime_env": {"env_vars": {"foo": "bar",},},
                },
            ],
        )
        sdk.deploy(complex_config)
        assert (
            fake_client.rolled_out_model.ray_serve_config["applications"]
            == complex_config.applications
        )

    def test_no_upload_remote_working_dir(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-service-name",
            working_dir="s3://some-remote-uri.zip",
        )

        sdk.deploy(config)
        applications = fake_client.rolled_out_model.ray_serve_config["applications"]
        assert len(applications) == 1
        assert (
            applications[0]["runtime_env"]["working_dir"] == "s3://some-remote-uri.zip"
        )

    def test_upload_local_py_modules(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        config = ServiceConfig(
            name="test-service-name",
            applications=[
                {
                    "import_path": "main:app",
                    "runtime_env": {
                        "py_modules": [
                            # Should be left alone.
                            "s3://some-remote-uri.zip",
                            # Should be uploaded.
                            "local-path",
                        ],
                    },
                },
            ],
        )
        sdk.deploy(config)
        applications = fake_client.rolled_out_model.ray_serve_config["applications"]
        assert len(applications) == 1
        assert (
            applications[0]["runtime_env"]["py_modules"][0]
            == "s3://some-remote-uri.zip"
        )
        assert applications[0]["runtime_env"]["py_modules"][1].startswith(
            FakeAnyscaleClient.CLOUD_BUCKET.format(
                cloud_id=FakeAnyscaleClient.DEFAULT_CLOUD_ID
            )
        )

    def test_upload_caching(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        """The same directory should only by uploaded once."""
        sdk, fake_client, _, _ = sdk_with_fakes
        config = ServiceConfig(
            name="test-service-name",
            applications=[
                {
                    "name": "app1",
                    "import_path": "main:app",
                    "runtime_env": {"working_dir": ".",},
                },
                {
                    "name": "app2",
                    "import_path": "main:app",
                    "runtime_env": {
                        "working_dir": ".",
                        "py_modules": [".", "other-dir",],
                    },
                },
            ],
        )
        sdk.deploy(config)
        applications = fake_client.rolled_out_model.ray_serve_config["applications"]
        assert len(applications) == 2
        assert applications[0]["runtime_env"]["working_dir"].startswith(
            FakeAnyscaleClient.CLOUD_BUCKET.format(
                cloud_id=FakeAnyscaleClient.DEFAULT_CLOUD_ID
            )
        )
        common_uri = applications[0]["runtime_env"]["working_dir"]

        assert applications[1]["runtime_env"]["working_dir"] == common_uri
        assert applications[1]["runtime_env"]["py_modules"][0] == common_uri
        assert applications[1]["runtime_env"]["py_modules"][1] != common_uri
        assert applications[1]["runtime_env"]["py_modules"][1].startswith(
            FakeAnyscaleClient.CLOUD_BUCKET.format(
                cloud_id=FakeAnyscaleClient.DEFAULT_CLOUD_ID
            )
        )


class TestLoadRequirementsFiles:
    @pytest.mark.parametrize("requirements", [None, *TEST_REQUIREMENTS_FILES])
    @pytest.mark.parametrize("in_applications", [False, True])
    def test_override_requirements_file(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        requirements: Optional[RequirementsFile],
        in_applications: bool,
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        applications: List[Dict[str, Any]] = [
            {"name": "no_runtime_env", "import_path": "main:app"},
            {
                "name": "empty_runtime_env",
                "import_path": "main:app",
                "runtime_env": {},
            },
            {
                "name": "has_runtime_env",
                "import_path": "main:app",
                "runtime_env": {
                    "env_vars": {"abc": "123"},
                    "working_dir": "s3://somewhere.zip",
                },
            },
        ]
        if in_applications and requirements is not None:
            for application in applications:
                assert isinstance(application, dict)
                runtime_env = application.get("runtime_env", {})
                runtime_env["pip"] = requirements.get_path()
                application["runtime_env"] = runtime_env

            config = ServiceConfig(name="test-service-name", applications=applications)
        else:
            config = ServiceConfig(
                name="test-service-name",
                applications=applications,
                requirements=requirements.get_path() if requirements else None,
            )

        if requirements is not None and requirements.expected_pip_list is None:
            with pytest.raises(FileNotFoundError):
                sdk.deploy(config)

            return

        sdk.deploy(config)
        deployed_ray_serve_config = fake_client.rolled_out_model.ray_serve_config
        if requirements is None:
            assert deployed_ray_serve_config["applications"] == config.applications
        else:
            assert len(deployed_ray_serve_config["applications"]) == 3
            assert deployed_ray_serve_config["applications"][0] == {
                "name": "no_runtime_env",
                "import_path": "main:app",
                "runtime_env": {"pip": requirements.expected_pip_list},
            }

            assert deployed_ray_serve_config["applications"][1] == {
                "name": "empty_runtime_env",
                "import_path": "main:app",
                "runtime_env": {"pip": requirements.expected_pip_list},
            }
            assert deployed_ray_serve_config["applications"][2] == {
                "name": "has_runtime_env",
                "import_path": "main:app",
                "runtime_env": {
                    "env_vars": {"abc": "123"},
                    "working_dir": "s3://somewhere.zip",
                    "pip": requirements.expected_pip_list,
                },
            }


TEST_SERVICE_ID = "fake-service-id"
TEST_SERVICE_NAME = "fake-service-name"
TEST_QUERY_URL = "fake-query-url"

TEST_IMAGE_URI = ImageURI.from_str("user/fake-build:3")
TEST_CLUSTER_ENV_BUILD_ID = "fake-build-id"

TEST_COMPUTE_CONFIG_NAME = "fake-compute-config"
TEST_COMPUTE_CONFIG_ID = "fake-compute-config-id"

TEST_APPLICATIONS = [{"import_path": "main:app"}]
TEST_HTTP_OPTIONS = {
    "request_timeout_s": 10.0,
}
TEST_GRPC_OPTIONS = {
    "grpc_servicer_functions": ["hello.world"],
}

DEFAULT_EXPECTED_STATUS = ServiceStatus(
    id=TEST_SERVICE_ID,
    name=TEST_SERVICE_NAME,
    state=ServiceState.TERMINATED,
    query_url=TEST_QUERY_URL,
    query_auth_token=None,
    primary_version=None,
    canary_version=None,
)


def _expected_status(**kwargs) -> ServiceStatus:
    return ServiceStatus(**{**DEFAULT_EXPECTED_STATUS.to_dict(), **kwargs})


def _service_version_model(
    id: str,  # noqa: A002
    weight: int,
    *,
    state: ExternalAPIServiceVersionState = ExternalAPIServiceVersionState.RUNNING,
    build_id: str = TEST_CLUSTER_ENV_BUILD_ID,
    compute_config_id: str = TEST_COMPUTE_CONFIG_ID,
    applications: Optional[List[Dict[str, Any]]] = None,
    http_options: Optional[Dict[str, Any]] = None,
    grpc_options: Optional[Dict[str, Any]] = None,
    logging_config: Optional[Dict[str, Any]] = None,
    ray_gcs_external_storage_config: Optional[Dict[str, Any]] = None,
) -> ProductionServiceV2VersionModel:
    ray_serve_config: Dict[str, Any] = {
        "applications": applications or TEST_APPLICATIONS
    }
    if http_options:
        ray_serve_config["http_options"] = http_options
    if grpc_options:
        ray_serve_config["grpc_options"] = grpc_options
    if logging_config:
        ray_serve_config["logging_config"] = logging_config

    return ProductionServiceV2VersionModel(
        id=id,
        current_state=state,
        weight=weight,
        build_id=build_id,
        compute_config_id=compute_config_id,
        ray_serve_config=ray_serve_config,
        ray_gcs_external_storage_config=ExternalAPIRayGCSExternalStorageConfig(
            **ray_gcs_external_storage_config
        )
        if ray_gcs_external_storage_config
        else None,
        local_vars_configuration=OPENAPI_NO_VALIDATION,
    )


@dataclass
class ServiceStatusTestCase:
    id: str = TEST_SERVICE_ID
    name: str = TEST_SERVICE_NAME
    state: ServiceEventCurrentState = ServiceEventCurrentState.TERMINATED
    base_url: str = TEST_QUERY_URL
    auth_token: Optional[str] = None
    primary_version: Optional[ProductionServiceV2VersionModel] = None
    canary_version: Optional[ProductionServiceV2VersionModel] = None

    expected_status: ServiceStatus = DEFAULT_EXPECTED_STATUS

    def service_model(self) -> ServiceModel:
        return ServiceModel(
            id=self.id,
            name=self.name,
            current_state=self.state,
            base_url=self.base_url,
            auth_token=self.auth_token,
            primary_version=self.primary_version,
            canary_version=self.canary_version,
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )


SERVICE_STATUS_TEST_CASES = [
    ServiceStatusTestCase(),
    ServiceStatusTestCase(expected_status=DEFAULT_EXPECTED_STATUS),
    # Test that states are mapped correctly.
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.STARTING,
        expected_status=_expected_status(state=ServiceState.STARTING),
    ),
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.RUNNING,
        expected_status=_expected_status(state=ServiceState.RUNNING),
    ),
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.ROLLING_OUT,
        expected_status=_expected_status(state=ServiceState.ROLLING_OUT),
    ),
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.ROLLING_BACK,
        expected_status=_expected_status(state=ServiceState.ROLLING_BACK),
    ),
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.UPDATING,
        expected_status=_expected_status(state=ServiceState.UPDATING),
    ),
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.TERMINATING,
        expected_status=_expected_status(state=ServiceState.TERMINATING),
    ),
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.TERMINATED,
        expected_status=_expected_status(state=ServiceState.TERMINATED),
    ),
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.UNHEALTHY,
        expected_status=_expected_status(state=ServiceState.UNHEALTHY),
    ),
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.SYSTEM_FAILURE,
        expected_status=_expected_status(state=ServiceState.SYSTEM_FAILURE),
    ),
    # Test that unrecognized states are mapped to ServiceState.UNKNOWN.
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.USER_ERROR_FAILURE,
        expected_status=_expected_status(state=ServiceState.UNKNOWN),
    ),
    ServiceStatusTestCase(
        auth_token="test-token-abc123",
        expected_status=_expected_status(query_auth_token="test-token-abc123"),
    ),
    # Test that primary and canary versions are mapped correctly.
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.RUNNING,
        primary_version=_service_version_model("primary", 100),
        expected_status=_expected_status(
            state=ServiceState.RUNNING,
            primary_version=ServiceVersionStatus(
                id="primary",
                state=ServiceVersionState.RUNNING,
                weight=100,
                config=ServiceConfig(
                    name=TEST_SERVICE_NAME,
                    applications=TEST_APPLICATIONS,
                    image_uri=TEST_IMAGE_URI.image_uri,
                    compute_config=TEST_COMPUTE_CONFIG_NAME + ":1",
                    query_auth_token_enabled=False,
                ),
            ),
        ),
    ),
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.RUNNING,
        primary_version=_service_version_model("primary", 50),
        canary_version=_service_version_model(
            "canary",
            0,
            http_options=TEST_HTTP_OPTIONS,
            grpc_options=TEST_GRPC_OPTIONS,
            state=ExternalAPIServiceVersionState.STARTING,
        ),
        expected_status=_expected_status(
            state=ServiceState.RUNNING,
            primary_version=ServiceVersionStatus(
                id="primary",
                state=ServiceVersionState.RUNNING,
                weight=50,
                config=ServiceConfig(
                    name=TEST_SERVICE_NAME,
                    applications=TEST_APPLICATIONS,
                    image_uri=TEST_IMAGE_URI.image_uri,
                    compute_config=TEST_COMPUTE_CONFIG_NAME + ":1",
                    query_auth_token_enabled=False,
                ),
            ),
            canary_version=ServiceVersionStatus(
                id="canary",
                state=ServiceVersionState.STARTING,
                weight=0,
                config=ServiceConfig(
                    name=TEST_SERVICE_NAME,
                    applications=TEST_APPLICATIONS,
                    image_uri=TEST_IMAGE_URI.image_uri,
                    compute_config=TEST_COMPUTE_CONFIG_NAME + ":1",
                    query_auth_token_enabled=False,
                    http_options=TEST_HTTP_OPTIONS,
                    grpc_options=TEST_GRPC_OPTIONS,
                ),
            ),
        ),
    ),
    # Test that when the service is TERMINATED, primary/canary versions are ignored.
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.TERMINATED,
        primary_version=_service_version_model("primary", 100),
        expected_status=_expected_status(state=ServiceState.TERMINATED),
    ),
    ServiceStatusTestCase(
        state=ServiceEventCurrentState.TERMINATED,
        canary_version=_service_version_model("canary", 100),
        expected_status=_expected_status(state=ServiceState.TERMINATED),
    ),
]


class TestStatus:
    def test_service_not_found(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        with pytest.raises(
            RuntimeError, match="Service with name 'test-service-name' was not found."
        ):
            sdk.status("test-service-name")

    @pytest.mark.parametrize("test_case", SERVICE_STATUS_TEST_CASES)
    def test_build_status_from_model(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        test_case: ServiceStatusTestCase,
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_image_uri_mapping(TEST_IMAGE_URI, TEST_CLUSTER_ENV_BUILD_ID)
        fake_client.add_compute_config(
            ComputeTemplate(
                id=TEST_COMPUTE_CONFIG_ID,
                name=TEST_COMPUTE_CONFIG_NAME,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )
        service_model = test_case.service_model()
        fake_client.update_service(service_model)

        status: ServiceStatus = sdk.status(name=service_model.name)
        assert (
            status == test_case.expected_status
        ), f"Expected: {test_case.expected_status}\nActual: {status}"

    def test_failed_to_get_cluster_env_build_image_uri(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        test_case = ServiceStatusTestCase(
            state=ServiceEventCurrentState.RUNNING,
            primary_version=_service_version_model("primary", 100),
        )
        service_model = test_case.service_model()
        fake_client.update_service(service_model)
        fake_client.add_compute_config(
            ComputeTemplate(
                id=TEST_COMPUTE_CONFIG_ID,
                name=TEST_COMPUTE_CONFIG_NAME,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        with pytest.raises(
            RuntimeError, match="Failed to get image URI for ID fake-build-id"
        ):
            sdk.status(name=service_model.name)

    def test_failed_to_get_compute_config_name(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        test_case = ServiceStatusTestCase(
            state=ServiceEventCurrentState.RUNNING,
            primary_version=_service_version_model("primary", 100),
        )
        service_model = test_case.service_model()
        fake_client.update_service(service_model)
        fake_client.set_image_uri_mapping(TEST_IMAGE_URI, TEST_CLUSTER_ENV_BUILD_ID)

        with pytest.raises(RuntimeError, match="Failed to get compute config"):
            sdk.status(name=service_model.name)

    def test_anonymous_compute_config_inlined(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_image_uri_mapping(TEST_IMAGE_URI, TEST_CLUSTER_ENV_BUILD_ID)
        fake_client.add_compute_config(
            ComputeTemplate(
                anonymous=True,
                id="anonymous-compute-config-id",
                name="anonymous-compute-config-name",
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.DEFAULT_CLOUD_ID,
                    head_node_type=ComputeNodeType(
                        name="head-node", instance_type="head-node-instance-type",
                    ),
                    worker_node_types=[],
                    auto_select_worker_config=True,
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        test_case = ServiceStatusTestCase(
            state=ServiceEventCurrentState.RUNNING,
            primary_version=_service_version_model(
                "primary", 100, compute_config_id="anonymous-compute-config-id"
            ),
            expected_status=_expected_status(
                state=ServiceState.RUNNING,
                primary_version=ServiceVersionStatus(
                    id="primary",
                    state=ServiceVersionState.RUNNING,
                    weight=100,
                    config=ServiceConfig(
                        name=TEST_SERVICE_NAME,
                        applications=TEST_APPLICATIONS,
                        image_uri=TEST_IMAGE_URI.image_uri,
                        compute_config=ComputeConfig(
                            cloud=fake_client.DEFAULT_CLOUD_NAME,
                            head_node=HeadNodeConfig(
                                instance_type="head-node-instance-type"
                            ),
                        ),
                        query_auth_token_enabled=False,
                    ),
                ),
            ),
        )
        service_model = test_case.service_model()
        fake_client.update_service(service_model)

        status: ServiceStatus = sdk.status(name=service_model.name)
        assert (
            status == test_case.expected_status
        ), f"Expected: {test_case.expected_status}\nActual: {status}"

    def test_ray_gcs_external_storage_config(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_image_uri_mapping(TEST_IMAGE_URI, TEST_CLUSTER_ENV_BUILD_ID)
        fake_client.add_compute_config(
            ComputeTemplate(
                id="compute-config-id",
                name="compute-config-name",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        test_case = ServiceStatusTestCase(
            state=ServiceEventCurrentState.RUNNING,
            primary_version=_service_version_model(
                "primary",
                100,
                compute_config_id="compute-config-id",
                ray_gcs_external_storage_config={"address": "host:1234"},
            ),
            expected_status=_expected_status(
                state=ServiceState.RUNNING,
                primary_version=ServiceVersionStatus(
                    id="primary",
                    state=ServiceVersionState.RUNNING,
                    weight=100,
                    config=ServiceConfig(
                        name=TEST_SERVICE_NAME,
                        applications=TEST_APPLICATIONS,
                        image_uri=TEST_IMAGE_URI.image_uri,
                        compute_config="compute-config-name:1",
                        query_auth_token_enabled=False,
                        ray_gcs_external_storage_config=RayGCSExternalStorageConfig(
                            enabled=True,
                            address="host:1234",
                            certificate_path="/etc/ssl/certs/ca-certificates.crt",
                        ),
                    ),
                ),
            ),
        )
        service_model = test_case.service_model()
        fake_client.update_service(service_model)

        status: ServiceStatus = sdk.status(name=service_model.name)
        assert (
            status == test_case.expected_status
        ), f"Expected: {test_case.expected_status}\nActual: {status}"

    def test_logging_config(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_image_uri_mapping(TEST_IMAGE_URI, TEST_CLUSTER_ENV_BUILD_ID)
        fake_client.add_compute_config(
            ComputeTemplate(
                id="compute-config-id",
                name="compute-config-name",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        test_case = ServiceStatusTestCase(
            state=ServiceEventCurrentState.RUNNING,
            primary_version=_service_version_model(
                "primary",
                100,
                compute_config_id="compute-config-id",
                logging_config={"log_level": "DEBUG"},
            ),
            expected_status=_expected_status(
                state=ServiceState.RUNNING,
                primary_version=ServiceVersionStatus(
                    id="primary",
                    state=ServiceVersionState.RUNNING,
                    weight=100,
                    config=ServiceConfig(
                        name=TEST_SERVICE_NAME,
                        applications=TEST_APPLICATIONS,
                        image_uri=TEST_IMAGE_URI.image_uri,
                        compute_config="compute-config-name:1",
                        query_auth_token_enabled=False,
                        logging_config={"log_level": "DEBUG"},
                    ),
                ),
            ),
        )
        service_model = test_case.service_model()
        fake_client.update_service(service_model)

        status: ServiceStatus = sdk.status(name=service_model.name)
        assert (
            status == test_case.expected_status
        ), f"Expected: {test_case.expected_status}\nActual: {status}"

    def test_versioned_compute_config_name(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        """Verify that versioned compute config names are constructed properly."""
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_image_uri_mapping(TEST_IMAGE_URI, TEST_CLUSTER_ENV_BUILD_ID)

        # Version 1.
        fake_client.add_compute_config(
            ComputeTemplate(
                id="v1-compute-config-id",
                name="test-compute-config",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )
        test_case = ServiceStatusTestCase(
            state=ServiceEventCurrentState.RUNNING,
            primary_version=_service_version_model(
                "primary", 100, compute_config_id="v1-compute-config-id",
            ),
            expected_status=_expected_status(
                state=ServiceState.RUNNING,
                primary_version=ServiceVersionStatus(
                    id="primary",
                    state=ServiceVersionState.RUNNING,
                    weight=100,
                    config=ServiceConfig(
                        name=TEST_SERVICE_NAME,
                        applications=TEST_APPLICATIONS,
                        image_uri=TEST_IMAGE_URI.image_uri,
                        compute_config="test-compute-config:1",
                        query_auth_token_enabled=False,
                    ),
                ),
            ),
        )
        service_model = test_case.service_model()
        fake_client.update_service(service_model)

        v1_status: ServiceStatus = sdk.status(name=service_model.name)
        assert (
            v1_status == test_case.expected_status
        ), f"Expected: {test_case.expected_status}\nActual: {v1_status}"

        # Version 2.
        fake_client.add_compute_config(
            ComputeTemplate(
                id="v2-compute-config-id",
                name="test-compute-config",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )
        test_case = ServiceStatusTestCase(
            state=ServiceEventCurrentState.RUNNING,
            primary_version=_service_version_model(
                "primary", 100, compute_config_id="v2-compute-config-id"
            ),
            expected_status=_expected_status(
                state=ServiceState.RUNNING,
                primary_version=ServiceVersionStatus(
                    id="primary",
                    state=ServiceVersionState.RUNNING,
                    weight=100,
                    config=ServiceConfig(
                        name=TEST_SERVICE_NAME,
                        applications=TEST_APPLICATIONS,
                        image_uri=TEST_IMAGE_URI.image_uri,
                        compute_config="test-compute-config:2",
                        query_auth_token_enabled=False,
                    ),
                ),
            ),
        )
        service_model = test_case.service_model()
        fake_client.update_service(service_model)

        v2_status: ServiceStatus = sdk.status(name=service_model.name)
        assert (
            v2_status == test_case.expected_status
        ), f"Expected: {test_case.expected_status}\nActual: {v2_status}"


class TestRollback:
    def test_not_found(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        with pytest.raises(
            RuntimeError, match="Service with name 'does-not-exist' was not found."
        ):
            sdk.rollback("does-not-exist")

    def test_basic(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        service_id = "test-service-id"
        fake_client.update_service(
            ServiceModel(
                id=service_id,
                name="test-name",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        sdk.rollback("test-name")
        assert fake_client.rolled_back_service == ("test-service-id", None)

    def test_max_surge_percent(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        service_id = "test-service-id"
        fake_client.update_service(
            ServiceModel(
                id=service_id,
                name="test-name",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        sdk.rollback("test-name", max_surge_percent=50)
        assert fake_client.rolled_back_service == ("test-service-id", 50)

    def test_no_name_passed_outside_workspace(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        with pytest.raises(
            ValueError,
            match="A service name must be provided when running outside of a workspace.",
        ):
            sdk.rollback()

    def test_default_name_in_workspace(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_inside_workspace(
            True,
            cluster_name=WORKSPACE_CLUSTER_NAME_PREFIX + "default-name-from-workspace",
        )

        service_id = "test-service-id"
        fake_client.update_service(
            ServiceModel(
                id=service_id,
                name="default-name-from-workspace",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        sdk.rollback()
        assert fake_client.rolled_back_service == ("test-service-id", None)


class TestTerminate:
    def test_not_found(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        with pytest.raises(
            RuntimeError, match="Service with name 'does-not-exist' was not found."
        ):
            sdk.terminate("does-not-exist")

    def test_basic(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        service_id = "test-service-id"
        fake_client.update_service(
            ServiceModel(
                id=service_id,
                name="test-name",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        sdk.terminate("test-name")
        assert fake_client.terminated_service == "test-service-id"

    def test_no_name_passed_outside_workspace(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes

        with pytest.raises(
            ValueError,
            match="A service name must be provided when running outside of a workspace.",
        ):
            sdk.terminate()

    def test_default_name_in_workspace(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        fake_client.set_inside_workspace(
            True,
            cluster_name=WORKSPACE_CLUSTER_NAME_PREFIX + "default-name-from-workspace",
        )

        service_id = "test-service-id"
        fake_client.update_service(
            ServiceModel(
                id=service_id,
                name="default-name-from-workspace",
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        sdk.terminate()
        assert fake_client.terminated_service == "test-service-id"


class TestWait:
    def test_service_not_found(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = sdk_with_fakes
        with pytest.raises(
            RuntimeError, match="Service with name 'test-service-name' was not found."
        ):
            sdk.wait(
                "test-service-name",
                state=ServiceState.RUNNING,
                timeout_s=60,
                interval_s=1,
            )

    def test_succeeds_immediately(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, logger, _ = sdk_with_fakes
        fake_client.update_service(
            ServiceModel(
                id=str(uuid.uuid4()),
                name="test-service-name",
                current_state=ServiceEventCurrentState.RUNNING,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

        sdk.wait(
            "test-service-name", state=ServiceState.RUNNING, timeout_s=60, interval_s=1,
        )
        assert any(
            "Service 'test-service-name' reached target state, exiting" in info_log
            for info_log in logger.info_messages
        )

    def test_times_out(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, logger, _ = sdk_with_fakes
        fake_client.update_service(
            ServiceModel(
                id=str(uuid.uuid4()),
                name="test-service-name",
                current_state=ServiceEventCurrentState.ROLLING_OUT,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

        with pytest.raises(
            TimeoutError,
            match="Service 'test-service-name' did not reach target state RUNNING within 60s. Last seen state: ROLLING_OUT.",
        ):
            sdk.wait(
                "test-service-name",
                state=ServiceState.RUNNING,
                timeout_s=60,
                interval_s=1,
            )

    def test_start_sequence(
        self,
        sdk_with_fakes: Tuple[ServiceSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, logger, timer = sdk_with_fakes
        base_model = ServiceModel(
            id=str(uuid.uuid4()),
            name="test-service-name",
            current_state=ServiceEventCurrentState.STARTING,
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )
        fake_client.update_service(base_model)

        def start_sequence(i: int):
            model = copy.deepcopy(base_model)
            if i == 0:
                model.current_state = ServiceEventCurrentState.STARTING
            elif i == 1:
                model.current_state = ServiceEventCurrentState.UPDATING
            else:
                model.current_state = ServiceEventCurrentState.RUNNING

            fake_client.update_service(model)

        timer.set_on_poll_iteration(start_sequence)

        sdk.wait(
            "test-service-name", state=ServiceState.RUNNING, timeout_s=60, interval_s=1,
        )

        assert any(
            "Service 'test-service-name' transitioned from STARTING to UPDATING"
            in info_log
            for info_log in logger.info_messages
        )
        assert any(
            "Service 'test-service-name' transitioned from UPDATING to RUNNING"
            in info_log
            for info_log in logger.info_messages
        )
        assert any(
            "Service 'test-service-name' reached target state, exiting" in info_log
            for info_log in logger.info_messages
        )
