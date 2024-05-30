from dataclasses import dataclass, field
from typing import List, Optional, Union

from anyscale._private.models import ModelBase, ModelEnum
from anyscale._private.workload import WorkloadConfig


@dataclass(frozen=True)
class JobConfig(WorkloadConfig):
    """Configuration options for a job."""

    __doc_py_example__ = """\
from anyscale.job.models import JobConfig

config = JobConfig(
    name="my-job",
    entrypoint="python main.py",
    max_retries=1,
    # An inline `ComputeConfig` can also be provided.
    compute_config="my-compute-config:1",
    # A containerfile path can also be provided.
    image_uri="anyscale/image/my-image:1",
)
"""

    __doc_yaml_example__ = """\
name: my-job
entrypoint: python main.py
# An inline dictionary can also be provided.
compute_config: my-compute-config:1
# A containerfile path can also be provided.
image_uri: anyscale/image/my-image:1
"""

    # Override the `name` field from `WorkloadConfig` so we can document it separately for jobs and services.
    name: Optional[str] = field(
        default=None,
        metadata={
            "docstring": "Name of the job. Multiple jobs can be submitted with the same name."
        },
    )

    entrypoint: str = field(
        default="",
        repr=False,
        metadata={
            "docstring": "Command that will be run to execute the job, e.g., `python main.py`."
        },
    )

    def _validate_entrypoint(self, entrypoint: str):
        if not isinstance(entrypoint, str):
            raise TypeError("'entrypoint' must be a string.")

        if not entrypoint:
            raise ValueError("'entrypoint' cannot be empty.")

    max_retries: int = field(
        default=1,
        repr=False,
        metadata={
            "docstring": "Maximum number of times the job will be retried before being marked failed. Defaults to `1`."
        },
    )

    def _validate_max_retries(self, max_retries: int):
        if not isinstance(max_retries, int):
            raise TypeError("'max_retries' must be an int.")

        if max_retries < 0:
            raise ValueError("'max_retries' must be >= 0.")


class JobRunState(ModelEnum):
    """Current state of a job run."""

    STARTING = "STARTING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"
    UNKNOWN = "UNKNOWN"

    def __str__(self):
        return self.name

    __docstrings__ = {
        STARTING: "The job run is being started and is not yet running.",
        RUNNING: "The job run is running.",
        FAILED: "The job run did not finish running or the entrypoint returned an exit code other than 0.",
        SUCCEEDED: "The job run finished running and its entrypoint returned exit code 0.",
        UNKNOWN: "The CLI/SDK received an unexpected state from the API server. In most cases, this means you need to update the CLI.",
    }


@dataclass(frozen=True)
class JobRunStatus(ModelBase):
    """Current status of a job."""

    __doc_py_example__ = """\
import anyscale
from anyscale.job.models import JobRunStatus
run_statuses: List[JobRunStatus] = anyscale.job.status(name="my-job").runs
"""

    __doc_cli_example__ = """\
$ anyscale job status -n my-job
id: prodjob_jurfnb5tebn76rtm1jiev1des7
name: my-job
state: SUCCEEDED
runs:
- name: raysubmit_igxeSmbQAtUY8qNf
  state: FAILED
- name: raysubmit_bKuhY2s2SrS9TYSz
  state: SUCCEEDED
"""

    name: str = field(metadata={"docstring": "Name of the job run."})

    def _validate_name(self, name: str):  # noqa: A002
        if not isinstance(name, str):
            raise TypeError("'name' must be a string.")

    state: Union[str, JobRunState] = field(
        metadata={"docstring": "Current state of the job run."}
    )

    def _validate_state(self, state: Union[str, JobRunState]) -> JobRunState:
        return JobRunState.validate(state)


class JobState(ModelEnum):
    """Current state of a job."""

    STARTING = "STARTING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"
    UNKNOWN = "UNKNOWN"

    _TERMINAL_JOB_STATES = [
        SUCCEEDED,
        FAILED,
    ]

    def __str__(self):
        return self.name

    @classmethod
    def is_terminal(cls, state: "JobState"):
        return state in cls._TERMINAL_JOB_STATES

    __docstrings__ = {
        STARTING: "The job is being started and is not yet running.",
        RUNNING: "The job is running. A job will have state RUNNING if a job run fails and there are remaining retries.",
        FAILED: "The job did not finish running or the entrypoint returned an exit code other than 0 after retrying up to max_retries times.",
        SUCCEEDED: "The job finished running and its entrypoint returned exit code 0.",
        UNKNOWN: "The CLI/SDK received an unexpected state from the API server. In most cases, this means you need to update the CLI.",
    }


@dataclass(frozen=True)
class JobStatus(ModelBase):
    """Current status of a job."""

    __doc_py_example__ = """\
import anyscale
from anyscale.job.models import JobStatus
status: JobStatus = anyscale.job.status(name="my-job")
"""

    __doc_cli_example__ = """\
$ anyscale job status -n my-job
id: prodjob_3suiybn8r7dhz92yv63jqzm473
name: my-job
state: STARTING
"""

    id: str = field(
        metadata={
            "docstring": "Unique ID of the job (generated when the job is first submitted)."
        }
    )

    def _validate_id(self, id: str):  # noqa: A002
        if not isinstance(id, str):
            raise TypeError("'id' must be a string.")

    name: str = field(
        metadata={
            "docstring": "Name of the job. Multiple jobs can be submitted with the same name."
        },
    )

    def _validate_name(self, name: str):
        if not isinstance(name, str):
            raise TypeError("'name' must be a string.")

    state: Union[str, JobState] = field(
        metadata={"docstring": "Current state of the job."}
    )

    def _validate_state(self, state: Union[str, JobState]) -> JobState:
        return JobState.validate(state)

    config: JobConfig = field(
        repr=False, metadata={"docstring": "Configuration of the job."}
    )

    def _validate_config(self, config: JobConfig):
        if not isinstance(config, JobConfig):
            raise TypeError("'config' must be a JobConfig.")

    runs: List[JobRunStatus] = field(metadata={"docstring": "List of job run states."})

    def _validate_runs(self, runs: List[JobRunStatus]):
        for run in runs:
            if not isinstance(run, JobRunStatus):
                raise TypeError("Each run in 'runs' must be a JobRunStatus.")
