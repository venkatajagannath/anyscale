import copy
from typing import Any, Dict, Optional

from anyscale._private.models.image_uri import ImageURI
from anyscale._private.workload import WorkloadSDK
from anyscale.sdk.anyscale_client.models import (
    AccessConfig,
    ApplyServiceModel,
    ProductionServiceV2VersionModel,
    RayGCSExternalStorageConfig as APIRayGCSExternalStorageConfig,
    ServiceConfig as ExternalAPIServiceConfig,
    ServiceEventCurrentState,
    ServiceModel,
)
from anyscale.service.models import (
    RayGCSExternalStorageConfig,
    ServiceConfig,
    ServiceState,
    ServiceStatus,
    ServiceVersionStatus,
)
from anyscale.utils.runtime_env import parse_requirements_file
from anyscale.utils.workspace_notification import (
    WorkspaceNotification,
    WorkspaceNotificationAction,
)


class ServiceSDK(WorkloadSDK):
    SERVICE_VERSION_ID_TRUNCATED_LEN = 8

    def _override_application_runtime_envs(
        self,
        config: ServiceConfig,
        *,
        autopopulate_in_workspace: bool = True,
        cloud_id: Optional[str] = None,
        workspace_requirements_path: Optional[str] = None,
    ) -> ServiceConfig:
        """Overrides the runtime_env of each application in the config.

        Local directories specified in the 'working_dir' or 'py_modules' fields will be
        uploaded and replaced with the resulting remote URIs.

        Requirements files will be loaded and populated into the 'pip' field.

        If autopopulate_from_workspace is passed and this code is running inside a
        workspace, the following defaults will be applied:
            - 'working_dir' will be set to '.'.
            - 'pip' will be set to the workspace-managed requirements file.
        """
        new_applications = copy.deepcopy(config.applications)
        new_runtime_envs = [app.get("runtime_env", {}) for app in new_applications]

        new_runtime_envs = self.override_and_upload_local_dirs(
            new_runtime_envs,
            working_dir_override=config.working_dir,
            excludes_override=config.excludes,
            cloud_id=cloud_id,
            autopopulate_in_workspace=autopopulate_in_workspace,
            additional_py_modules=config.py_modules,
        )
        new_runtime_envs = self.override_and_load_requirements_files(
            new_runtime_envs,
            requirements_override=config.requirements,
            workspace_requirements_path=workspace_requirements_path,
        )
        new_runtime_envs = self.update_env_vars(
            new_runtime_envs, env_vars_updates=config.env_vars
        )

        for app, new_runtime_env in zip(new_applications, new_runtime_envs):
            if new_runtime_env:
                app["runtime_env"] = new_runtime_env

        return config.options(
            applications=new_applications,
            requirements=None,
            working_dir=None,
            excludes=None,
        )

    def _get_default_name(self) -> str:
        """Get a default name for the service.

        A default is currently only generated when running inside a workspace
        (from the workspace cluster name), so this function errors if called outside
        a workspace.
        """
        name = self.get_current_workspace_name()
        if name is None:
            raise ValueError(
                "A service name must be provided when running outside of a workspace."
            )

        self.logger.info(f"No name was specified, using default: '{name}'.")
        return name

    def _log_deployed_service_info(
        self, service: ServiceModel, *, canary_percent: Optional[int]
    ):
        """Log user-facing information about a deployed service."""
        canary_percent_info = (
            ""
            if canary_percent is None
            else f" (target canary percent: {canary_percent})"
        )
        message = f"Service '{service.name}' deployed{canary_percent_info}."
        self.logger.info(message)
        if self.client.inside_workspace():
            self.client.send_workspace_notification(
                WorkspaceNotification(
                    body=message,
                    action=WorkspaceNotificationAction(
                        type="navigate-service", title="View Service", value=service.id,
                    ),
                ),
            )

        self.logger.info(
            f"View the service in the UI: '{self.client.get_service_ui_url(service.id)}'"
        )
        self.logger.info(
            "Query the service once it's running using the following curl command:"
        )
        auth_token_header = (
            ""
            if service.auth_token is None
            else f"-H 'Authorization: Bearer {service.auth_token}' "
        )
        self.logger.info(f"curl {auth_token_header}{service.base_url}/")

    def _build_ray_serve_config(self, config: ServiceConfig) -> Dict[str, Any]:
        ray_serve_config: Dict[str, Any] = {"applications": config.applications}
        if config.http_options:
            ray_serve_config["http_options"] = config.http_options
        if config.grpc_options:
            ray_serve_config["grpc_options"] = config.grpc_options
        if config.logging_config:
            ray_serve_config["logging_config"] = config.logging_config

        return ray_serve_config

    def _build_apply_service_model_for_in_place_update(  # noqa: PLR0912
        self,
        name: str,
        config: ServiceConfig,
        *,
        canary_percent: Optional[int] = None,
        max_surge_percent: Optional[int] = None,
        existing_service: Optional[ServiceModel] = None,
    ) -> ApplyServiceModel:
        """Build the ApplyServiceModel for an in_place update.

        in_place updates:
            - must be performed on an existing service.
            - cannot be performed while a rollout is active.
            - do not support rollout options (canary_percent and max_surge_percent).
            - do not support changing cluster-level config options (image, compute_config, etc.).

        If cluster-level options are provided, a warning will be logged and they will be ignored.
        """
        if canary_percent is not None:
            raise ValueError(
                "canary_percent cannot be specified when doing an in_place update."
            )
        if max_surge_percent is not None:
            raise ValueError(
                "max_surge_percent cannot be specified when doing an in_place update."
            )
        if existing_service is None:
            raise RuntimeError(
                "in_place can only be used to update running services, "
                f"but no service was found with name '{name}'."
            )
        if existing_service.current_state in {
            ServiceEventCurrentState.TERMINATING,
            ServiceEventCurrentState.TERMINATED,
        }:
            raise RuntimeError(
                "in_place can only be used to update running services, "
                f"but service '{name}' is terminated."
            )

        if existing_service.canary_version is not None:
            raise RuntimeError(
                "in_place updates cannot be used while a rollout is in progress. "
                "Complete the rollout or roll back first."
            )

        if any(
            [
                config.image_uri is not None,
                config.containerfile is not None,
                config.compute_config is not None,
                config.ray_gcs_external_storage_config is not None,
            ]
        ):
            self.logger.warning(
                "Cluster-level options such as image and compute config "
                "are ignored when performing an in_place update."
            )

        existing_config: ProductionServiceV2VersionModel = existing_service.primary_version
        query_auth_token_enabled = existing_service.auth_token is not None
        cloud_id = self.client.get_cloud_id(
            compute_config_id=existing_config.compute_config_id
        )
        config = self._override_application_runtime_envs(
            config,
            cloud_id=cloud_id,
            workspace_requirements_path=self.client.get_workspace_requirements_path(),
        )
        return ApplyServiceModel(
            name=name,
            project_id=self.client.get_project_id(parent_cloud_id=cloud_id),
            ray_serve_config=self._build_ray_serve_config(config),
            build_id=existing_config.build_id,
            compute_config_id=existing_config.compute_config_id,
            rollout_strategy="IN_PLACE",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=query_auth_token_enabled),
            ),
            ray_gcs_external_storage_config=existing_config.ray_gcs_external_storage_config,
        )

    def _build_apply_service_model_for_rollout(  # noqa: PLR0912
        self,
        name: str,
        config: ServiceConfig,
        *,
        canary_percent: Optional[int] = None,
        max_surge_percent: Optional[int] = None,
        existing_service: Optional[ServiceModel] = None,
    ) -> ApplyServiceModel:
        """Build the ApplyServiceModel for a rolling update."""

        build_id = None
        if config.containerfile is not None:
            build_id = self.client.get_cluster_env_build_id_from_containerfile(
                cluster_env_name=f"image-for-service-{name}",
                containerfile=self.get_containerfile_contents(config.containerfile),
                anonymous=True,
            )
        elif config.image_uri is not None:
            build_id = self.client.get_cluster_env_build_id_from_image_uri(
                image_uri=ImageURI.from_str(config.image_uri)
            )

        if self._image_sdk.enable_image_build_for_tracked_requirements:
            requirements_path_to_be_populated_in_runtime_env = None
            requirements_path = self.client.get_workspace_requirements_path()
            if requirements_path is not None:
                requirements = parse_requirements_file(requirements_path)
                if requirements:
                    build_id = self._image_sdk.build_image_from_requirements(
                        name=f"image-for-service-{name}",
                        base_build_id=self.client.get_default_build_id(),
                        requirements=requirements,
                    )
        else:
            requirements_path_to_be_populated_in_runtime_env = (
                self.client.get_workspace_requirements_path()
            )

        if build_id is None:
            build_id = self.client.get_default_build_id()

        compute_config_id, cloud_id = self.resolve_compute_config(config.compute_config)
        if (
            existing_service is not None
            and existing_service.primary_version is not None
        ):
            existing_cloud_id = self.client.get_cloud_id(
                compute_config_id=existing_service.primary_version.compute_config_id
            )
            if cloud_id != existing_cloud_id:
                new_cloud = self.client.get_cloud(cloud_id=cloud_id)
                assert new_cloud is not None
                existing_cloud = self.client.get_cloud(cloud_id=existing_cloud_id)
                assert existing_cloud is not None
                raise ValueError(
                    f"The cloud for a service cannot be changed once it's created. "
                    f"Service '{name}' was created on cloud '{existing_cloud.name}', but "
                    f"the provided config is for cloud '{new_cloud.name}'."
                )

        env_vars_from_workspace = self.client.get_workspace_env_vars()
        if env_vars_from_workspace:
            if config.env_vars:
                # the precedence should be cli > workspace
                env_vars_from_workspace.update(config.env_vars)
                config = config.options(env_vars=env_vars_from_workspace)
            else:
                config = config.options(env_vars=env_vars_from_workspace)

        config = self._override_application_runtime_envs(
            config,
            cloud_id=cloud_id,
            workspace_requirements_path=requirements_path_to_be_populated_in_runtime_env,
        )

        ray_gcs_external_storage_config = None
        if config.ray_gcs_external_storage_config is not None:
            assert isinstance(
                config.ray_gcs_external_storage_config, RayGCSExternalStorageConfig
            )
            ray_gcs_external_storage_config = APIRayGCSExternalStorageConfig(
                enable=config.ray_gcs_external_storage_config.enabled,
            )
            if config.ray_gcs_external_storage_config.address is not None:
                ray_gcs_external_storage_config.address = (
                    config.ray_gcs_external_storage_config.address
                )
            if config.ray_gcs_external_storage_config.certificate_path is not None:
                ray_gcs_external_storage_config.redis_certificate_path = (
                    config.ray_gcs_external_storage_config.certificate_path
                )
        return ApplyServiceModel(
            name=name,
            project_id=self.client.get_project_id(parent_cloud_id=cloud_id),
            ray_serve_config=self._build_ray_serve_config(config),
            build_id=build_id,
            compute_config_id=compute_config_id,
            canary_percent=canary_percent,
            max_surge_percent=max_surge_percent,
            rollout_strategy="ROLLOUT",
            config=ExternalAPIServiceConfig(
                access=AccessConfig(use_bearer_token=config.query_auth_token_enabled),
            ),
            ray_gcs_external_storage_config=ray_gcs_external_storage_config,
        )

    def deploy(
        self,
        config: ServiceConfig,
        *,
        in_place: bool = False,
        canary_percent: Optional[int] = None,
        max_surge_percent: Optional[int] = None,
    ) -> str:
        if not isinstance(in_place, bool):
            raise TypeError("in_place must be a bool.")

        if canary_percent is not None:
            if not isinstance(canary_percent, int):
                raise TypeError("canary_percent must be an int.")
            if canary_percent < 0 or canary_percent > 100:
                raise ValueError("canary_percent must be between 0 and 100.")

        if max_surge_percent is not None:
            if not isinstance(max_surge_percent, int):
                raise TypeError("max_surge_percent must be an int.")
            if max_surge_percent < 0 or max_surge_percent > 100:
                raise ValueError("max_surge_percent must be between 0 and 100.")

        name = config.name or self._get_default_name()
        existing_service: Optional[ServiceModel] = self.client.get_service(name)
        if existing_service is None:
            self.logger.info(f"Starting new service '{name}'.")
        elif existing_service.current_state == ServiceEventCurrentState.TERMINATED:
            self.logger.info(f"Restarting existing service '{name}'.")
        else:
            self.logger.info(f"Updating existing service '{name}'.")

        if in_place:
            model = self._build_apply_service_model_for_in_place_update(
                name,
                config,
                canary_percent=canary_percent,
                max_surge_percent=max_surge_percent,
                existing_service=existing_service,
            )
        else:
            model = self._build_apply_service_model_for_rollout(
                name,
                config,
                canary_percent=canary_percent,
                max_surge_percent=max_surge_percent,
                existing_service=existing_service,
            )

        service: ServiceModel = self.client.rollout_service(model)
        self._log_deployed_service_info(service, canary_percent=canary_percent)

        return service.id

    def rollback(
        self, name: Optional[str] = None, *, max_surge_percent: Optional[int] = None,
    ) -> str:
        if name is None:
            name = self._get_default_name()

        model: Optional[ServiceModel] = self.client.get_service(name)
        if model is None:
            raise RuntimeError(f"Service with name '{name}' was not found.")

        self.client.rollback_service(model.id, max_surge_percent=max_surge_percent)

        return model.id

    def terminate(self, name: Optional[str] = None) -> str:
        if name is None:
            name = self._get_default_name()

        model: Optional[ServiceModel] = self.client.get_service(name)
        if model is None:
            raise RuntimeError(f"Service with name '{name}' was not found.")

        self.client.terminate_service(model.id)

        return model.id

    def _service_version_model_to_status(
        self,
        model: ProductionServiceV2VersionModel,
        *,
        service_name: str,
        query_auth_token_enabled: bool,
    ) -> ServiceVersionStatus:
        image_uri = self._image_sdk.get_image_uri_from_build_id(model.build_id)
        if image_uri is None:
            raise RuntimeError(f"Failed to get image URI for ID {model.build_id}.")

        ray_gcs_external_storage_config = None
        if model.ray_gcs_external_storage_config is not None:
            ray_gcs_external_storage_config = RayGCSExternalStorageConfig(
                enabled=model.ray_gcs_external_storage_config.enable,
                address=model.ray_gcs_external_storage_config.address,
                certificate_path=model.ray_gcs_external_storage_config.redis_certificate_path,
            )

        return ServiceVersionStatus(
            # NOTE(edoakes): the "version ID" exposed in the UI and tagged in the metrics is
            # not actually the DB ID, but a truncated version of it. We should store this
            # in the DB to avoid breakages, but for now I'm copying the existing logic.
            id=model.id[-self.SERVICE_VERSION_ID_TRUNCATED_LEN :],
            state=model.current_state,
            # NOTE(edoakes): there is also a "current_weight" field but it does not match the UI.
            weight=model.weight,
            config=ServiceConfig(
                name=service_name,
                applications=model.ray_serve_config["applications"],
                image_uri=str(image_uri),
                compute_config=self.get_user_facing_compute_config(
                    model.compute_config_id
                ),
                query_auth_token_enabled=query_auth_token_enabled,
                http_options=model.ray_serve_config.get("http_options", None),
                grpc_options=model.ray_serve_config.get("grpc_options", None),
                logging_config=model.ray_serve_config.get("logging_config", None),
                ray_gcs_external_storage_config=ray_gcs_external_storage_config,
            ),
        )

    def _model_state_to_state(
        self, model_state: ServiceEventCurrentState,
    ) -> ServiceState:
        # If we add a new state to the backend, old clients may not recognize it.
        # Rather than erroring out and causing old code to crash, return UNKNOWN.
        state: ServiceState = ServiceState(ServiceState.UNKNOWN)
        try:
            state = ServiceState(model_state)
        except ValueError:
            self.logger.warning(
                f"Got unrecognized state: '{model_state}'. "
                "You likely need to update the 'anyscale' package. "
                "If you still see this message after upgrading, contact Anyscale support."
            )

        return state

    def _service_model_to_status(self, model: ServiceModel) -> ServiceStatus:
        # TODO(edoakes): for some reason the primary_version is populated
        # when the service is terminated. This should be fixed in the backend.
        is_terminated = model.current_state == ServiceEventCurrentState.TERMINATED

        # TODO(edoakes): this is currently only exposed at the service level in the API,
        # which means that the per-version `query_auth_token_enabled` field will lie if
        # it's changed.
        query_auth_token_enabled = model.auth_token is not None

        primary_version = None
        if not is_terminated and model.primary_version is not None:
            primary_version = self._service_version_model_to_status(
                model.primary_version,
                service_name=model.name,
                query_auth_token_enabled=query_auth_token_enabled,
            )

        canary_version = None
        if not is_terminated and model.canary_version is not None:
            canary_version = self._service_version_model_to_status(
                model.canary_version,
                service_name=model.name,
                query_auth_token_enabled=query_auth_token_enabled,
            )

        return ServiceStatus(
            id=model.id,
            name=model.name,
            state=self._model_state_to_state(model.current_state),
            query_url=model.base_url,
            query_auth_token=model.auth_token,
            primary_version=primary_version,
            canary_version=canary_version,
        )

    def status(self, name: str) -> ServiceStatus:
        model: Optional[ServiceModel] = self.client.get_service(name)
        if model is None:
            raise RuntimeError(f"Service with name '{name}' was not found.")

        return self._service_model_to_status(model)

    def wait(
        self, name: str, *, state: ServiceState, timeout_s: float, interval_s: float,
    ):
        if not isinstance(timeout_s, (int, float)):
            raise TypeError("timeout_s must be a float")
        if timeout_s <= 0:
            raise ValueError("timeout_s must be >= 0")

        if not isinstance(interval_s, (int, float)):
            raise TypeError("interval_s must be a float")
        if interval_s <= 0:
            raise ValueError("interval_s must be >= 0")

        def _get_curr_state() -> ServiceState:
            model: Optional[ServiceModel] = self.client.get_service(name)
            if model is None:
                raise RuntimeError(f"Service with name '{name}' was not found.")

            return self._model_state_to_state(model.current_state)

        curr_state = _get_curr_state()
        self.logger.info(
            f"Waiting for service '{name}' to reach target state {state}, currently in state: {curr_state}"
        )
        for _ in self.timer.poll(timeout_s=timeout_s, interval_s=interval_s):
            new_state = _get_curr_state()
            if new_state != curr_state:
                self.logger.info(
                    f"Service '{name}' transitioned from {curr_state} to {new_state}"
                )
                curr_state = new_state

            if curr_state == state:
                self.logger.info(f"Service '{name}' reached target state, exiting")
                break
        else:
            raise TimeoutError(
                f"Service '{name}' did not reach target state {state} within {timeout_s}s. Last seen state: {curr_state}."
            )
