from typing import Any, cast, Dict, List, Optional, Union
import uuid

from anyscale._private.workload import WorkloadSDK
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models import (
    CreateInternalProductionJob,
    InternalProductionJob,
    ProductionJobConfig,
)
from anyscale.client.openapi_client.models.job_status import (
    JobStatus as BackendJobStatus,
)
from anyscale.client.openapi_client.models.production_job import ProductionJob
from anyscale.client.openapi_client.models.ray_runtime_env_config import (
    RayRuntimeEnvConfig,
)
from anyscale.job.models import (
    JobConfig,
    JobRunState,
    JobRunStatus,
    JobState,
    JobStatus,
)
from anyscale.sdk.anyscale_client.models import Job
from anyscale.sdk.anyscale_client.models.ha_job_states import HaJobStates
from anyscale.utils.runtime_env import parse_requirements_file


logger = BlockLogger()


class JobSDK(WorkloadSDK):
    _POLLING_INTERVAL_SECONDS = 10.0

    def _populate_runtime_env(
        self,
        config: JobConfig,
        *,
        autopopulate_in_workspace: bool = True,
        cloud_id: Optional[str] = None,
        workspace_requirements_path: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Populates a runtime_env from the config.

        Local directories specified in the 'working_dir' will be uploaded and
        replaced with the resulting remote URIs.

        Requirements files will be loaded and populated into the 'pip' field.

        If autopopulate_from_workspace is passed and this code is running inside a
        workspace, the following defaults will be applied:
            - 'working_dir' will be set to '.'.
            - 'pip' will be set to the workspace-managed requirements file.
        """
        runtime_env: Dict[str, Any] = {}
        [runtime_env] = self.override_and_upload_local_dirs(
            [runtime_env],
            working_dir_override=config.working_dir,
            excludes_override=config.excludes,
            cloud_id=cloud_id,
            autopopulate_in_workspace=autopopulate_in_workspace,
            additional_py_modules=config.py_modules,
        )
        [runtime_env] = self.override_and_load_requirements_files(
            [runtime_env],
            requirements_override=config.requirements,
            workspace_requirements_path=workspace_requirements_path,
        )
        [runtime_env] = self.update_env_vars(
            [runtime_env], env_vars_updates=config.env_vars,
        )

        return runtime_env or None

    def _get_default_name(self) -> str:
        """Get a default name for the job.

        If running inside a workspace, this is generated from the workspace name,
        else it generates a random name.
        """
        # TODO(edoakes): generate two random words instead of UUID here.
        name = f"job-{self.get_current_workspace_name() or str(uuid.uuid4())}"
        self.logger.info(f"No name was specified, using default: '{name}'.")
        return name

    def submit(self, config: JobConfig) -> str:
        name = config.name or self._get_default_name()

        build_id = None
        if config.containerfile is not None:
            build_id = self._image_sdk.build_image_from_containerfile(
                name=f"image-for-job-{name}",
                containerfile=self.get_containerfile_contents(config.containerfile),
            )
        elif config.image_uri is not None:
            build_id = self._image_sdk.registery_image(image_uri=config.image_uri)

        if self._image_sdk.enable_image_build_for_tracked_requirements:
            requirements_path_to_be_populated_in_runtime_env = None
            requirements_path = self.client.get_workspace_requirements_path()
            if requirements_path is not None:
                requirements = parse_requirements_file(requirements_path)
                if requirements:
                    build_id = self._image_sdk.build_image_from_requirements(
                        name=f"image-for-job-{name}",
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

        env_vars_from_workspace = self.client.get_workspace_env_vars()
        if env_vars_from_workspace:
            if config.env_vars:
                # the precedence should be cli > workspace
                env_vars_from_workspace.update(config.env_vars)
                config = config.options(env_vars=env_vars_from_workspace)
            else:
                config = config.options(env_vars=env_vars_from_workspace)

        runtime_env = self._populate_runtime_env(
            config,
            cloud_id=cloud_id,
            workspace_requirements_path=requirements_path_to_be_populated_in_runtime_env,
        )

        job: InternalProductionJob = self.client.submit_job(
            CreateInternalProductionJob(
                name=name,
                project_id=self.client.get_project_id(parent_cloud_id=cloud_id),
                workspace_id=self.client.get_current_workspace_id(),
                config=ProductionJobConfig(
                    entrypoint=config.entrypoint,
                    runtime_env=runtime_env,
                    build_id=build_id,
                    compute_config_id=compute_config_id,
                    max_retries=config.max_retries,
                ),
                # TODO(edoakes): support job queue config.
                job_queue_config=None,
            )
        )

        self.logger.info(f"Job '{name}' submitted, ID: '{job.id}'.")
        self.logger.info(
            f"View the job in the UI: {self.client.get_job_ui_url(job.id)}"
        )
        return job.id

    _HA_JOB_STATE_TO_JOB_STATE = {
        HaJobStates.UPDATING: JobState.RUNNING,
        HaJobStates.RUNNING: JobState.RUNNING,
        HaJobStates.RESTARTING: JobState.RUNNING,
        HaJobStates.CLEANING_UP: JobState.RUNNING,
        HaJobStates.PENDING: JobState.STARTING,
        HaJobStates.AWAITING_CLUSTER_START: JobState.STARTING,
        HaJobStates.SUCCESS: JobState.SUCCEEDED,
        HaJobStates.ERRORED: JobState.FAILED,
        HaJobStates.TERMINATED: JobState.FAILED,
        HaJobStates.BROKEN: JobState.FAILED,
        HaJobStates.OUT_OF_RETRIES: JobState.FAILED,
    }

    _BACKEND_JOB_STATUS_TO_JOB_RUN_STATE = {
        BackendJobStatus.RUNNING: JobRunState.RUNNING,
        BackendJobStatus.COMPLETED: JobRunState.SUCCEEDED,
        BackendJobStatus.PENDING: JobRunState.STARTING,
        BackendJobStatus.STOPPED: JobRunState.FAILED,
        BackendJobStatus.SUCCEEDED: JobRunState.SUCCEEDED,
        BackendJobStatus.FAILED: JobRunState.FAILED,
        BackendJobStatus.UNKNOWN: JobRunState.UNKNOWN,
    }

    def _job_state_from_job_model(self, model: ProductionJob) -> JobState:
        ha_state = model.state.current_state if model.state else None
        return cast(
            JobState, self._HA_JOB_STATE_TO_JOB_STATE.get(ha_state, JobState.UNKNOWN)
        )

    def _job_run_model_to_job_run_status(self, run: Job) -> JobRunStatus:
        state = self._BACKEND_JOB_STATUS_TO_JOB_RUN_STATE.get(
            run.status, JobRunState.UNKNOWN
        )
        return JobRunStatus(name=run.name, state=state)

    def _job_model_to_status(self, model: ProductionJob, runs: List[Job]) -> JobStatus:
        state = self._job_state_from_job_model(model)

        prod_job_config: ProductionJobConfig = model.config
        runtime_env_config: RayRuntimeEnvConfig = prod_job_config.runtime_env if prod_job_config else None
        config = JobConfig(
            name=model.name,
            compute_config=self.get_user_facing_compute_config(
                prod_job_config.compute_config_id
            ),
            requirements=runtime_env_config.pip if runtime_env_config else None,
            working_dir=runtime_env_config.working_dir if runtime_env_config else None,
            env_vars=runtime_env_config.env_vars if runtime_env_config else None,
            entrypoint=prod_job_config.entrypoint,
            max_retries=prod_job_config.max_retries
            if prod_job_config.max_retries is not None
            else -1,
        )
        runs = [self._job_run_model_to_job_run_status(run) for run in runs]

        return JobStatus(
            name=model.name, id=model.id, state=state, runs=runs, config=config
        )

    def _resolve_to_job_model(
        self, name: Optional[str] = None, job_id: Optional[str] = None
    ) -> ProductionJob:
        if name is None and job_id is None:
            raise ValueError("One of 'name' or 'job_id' must be provided.")

        if name is not None and job_id is not None:
            raise ValueError("Only one of 'name' or 'job_id' can be provided.")

        model: Optional[ProductionJob] = self.client.get_job(name=name, job_id=job_id)
        if model is None:
            if name is not None:
                raise RuntimeError(f"Job with name '{name}' was not found.")
            else:
                raise RuntimeError(f"Job with id '{job_id}' was not found.")

        return model

    def status(
        self, name: Optional[str] = None, job_id: Optional[str] = None
    ) -> JobStatus:
        job_model = self._resolve_to_job_model(name=name, job_id=job_id)
        runs = self.client.get_job_runs(job_model.id)
        return self._job_model_to_status(model=job_model, runs=runs)

    def terminate(
        self, job_id: Optional[str] = None, name: Optional[str] = None,
    ) -> str:
        job_model = self._resolve_to_job_model(name=name, job_id=job_id)
        self.client.terminate_job(job_model.id)
        self.logger.info(f"Marked job '{job_model.name}' for termination")
        return job_model.id

    _TERMINAL_HA_JOB_STATES = [
        HaJobStates.SUCCESS,
        HaJobStates.TERMINATED,
        HaJobStates.OUT_OF_RETRIES,
    ]

    def archive(self, job_id: Optional[str] = None, name: Optional[str] = None,) -> str:
        job_model = self._resolve_to_job_model(name=name, job_id=job_id)

        ha_state = job_model.state.current_state if job_model.state else None
        if ha_state not in self._TERMINAL_HA_JOB_STATES:
            raise RuntimeError(
                f"Job with id '{job_model.id}' has not reached a terminal state and cannot be archived."
            )

        self.client.archive_job(job_model.id)
        self.logger.info(f"Job {job_model.id} is successfully archived.")
        return job_model.id

    def wait(
        self,
        *,
        name: Optional[str] = None,
        job_id: Optional[str] = None,
        state: Union[str, JobState] = JobState.SUCCEEDED,
        timeout_s: float = 1800,
        interval_s: float = _POLLING_INTERVAL_SECONDS,
    ):
        if not isinstance(timeout_s, (int, float)):
            raise TypeError("timeout_s must be a float")
        if timeout_s <= 0:
            raise ValueError("timeout_s must be >= 0")

        if not isinstance(interval_s, (int, float)):
            raise TypeError("interval_s must be a float")
        if interval_s <= 0:
            raise ValueError("interval_s must be >= 0")

        if not isinstance(state, JobState):
            raise TypeError("'state' must be a JobState.")

        job_id_or_name = job_id or name
        job_model = self._resolve_to_job_model(name=name, job_id=job_id)
        curr_state = self._job_state_from_job_model(job_model)

        self.logger.info(
            f"Waiting for job '{job_id_or_name}' to reach target state {state}, currently in state: {curr_state}"
        )
        for _ in self.timer.poll(timeout_s=timeout_s, interval_s=interval_s):
            job_model = self._resolve_to_job_model(name=name, job_id=job_id)
            new_state = self._job_state_from_job_model(job_model)

            if new_state != curr_state:
                self.logger.info(
                    f"Job '{job_id_or_name}' transitioned from {curr_state} to {new_state}"
                )
                curr_state = new_state

            if curr_state == state:
                self.logger.info(
                    f"Job '{job_id_or_name}' reached target state, exiting"
                )
                break

            if JobState.is_terminal(curr_state):
                raise RuntimeError(
                    f"Job '{job_id_or_name}' reached terminal state '{curr_state}', and will not reach '{state}'."
                )
        else:
            raise TimeoutError(
                f"Job '{job_id_or_name}' did not reach target state {state} within {timeout_s}s. Last seen state: {curr_state}."
            )

    def logs(
        self,
        *,
        job_id: Optional[str] = None,
        name: Optional[str] = None,
        run: Optional[str] = None,
        follow: bool = False,
    ) -> str:
        # no_cluster_journal_events: bool = False
        job_model = self._resolve_to_job_model(name=name, job_id=job_id)
        curr_state = self._job_state_from_job_model(job_model)

        if follow:
            raise NotImplementedError(
                "anyscale.job.logs(..., follow=True) is not supported yet. Please set follow=False."
            )

        # TODO(mowen): Should we wait on JobState.UNKNOWN as well?
        if curr_state == JobState.STARTING:
            self.wait(name=name, job_id=job_id, state=JobState.RUNNING)
            # TODO(mowen): This is replacing JobController._wait_for_a_job_run https://github.com/anyscale/product/blob/2329d51a382fda6b5fd20fc4212f0f5af1740b34/frontend/cli/anyscale/controllers/job_controller.py#L473
            # which prints out cluster journal event logs. Do we want to support that?

        last_job_run_id = job_model.last_job_run_id
        if run is None:
            job_run_id = last_job_run_id
        else:
            runs: List[Job] = self.client.get_job_runs(job_model.id)
            for job_run in runs:
                if job_run.name == run:
                    job_run_id = job_run.id
                    break
            else:
                raise ValueError(
                    f"Job run '{run}' was not found for job '{job_id or name}'."
                )

        return self.client.logs_for_job_run(
            job_run_id=job_run_id, follow=follow and job_id == last_job_run_id
        )
