from typing import Optional, Union

from anyscale._private.sdk import sdk_command
from anyscale.job._private.job_sdk import JobSDK
from anyscale.job.models import JobConfig, JobState


_JOB_SDK_SINGLETON_KEY = "job_sdk"

_SUBMIT_EXAMPLE = """
import anyscale
from anyscale.job.models import JobConfig

anyscale.job.submit(
    JobConfig(
        name="my-job",
        entrypoint="python main.py",
        working_dir=".",
    ),
)
"""


@sdk_command(
    _JOB_SDK_SINGLETON_KEY,
    JobSDK,
    doc_py_example=_SUBMIT_EXAMPLE,
    arg_docstrings={"config": "The config options defining the job.",},
)
def submit(config: JobConfig, *, _sdk: JobSDK) -> str:
    """Submit a job.

    Returns the id of the submitted job.
    """
    return _sdk.submit(config)


_STATUS_EXAMPLE = """
import anyscale
from anyscale.job.models import JobStatus

status: JobStatus = anyscale.job.status(name="my-job")
"""


@sdk_command(
    _JOB_SDK_SINGLETON_KEY,
    JobSDK,
    doc_py_example=_STATUS_EXAMPLE,
    arg_docstrings={"name": "Name of the job.", "job_id": "Unique ID of the job"},
)
def status(
    name: Optional[str] = None, job_id: Optional[str] = None, *, _sdk: JobSDK
) -> str:
    """Get the status of a job."""
    return _sdk.status(name=name, job_id=job_id)


_TERMINATE_EXAMPLE = """
import anyscale

anyscale.job.terminate(name="my-job")
"""


@sdk_command(
    _JOB_SDK_SINGLETON_KEY,
    JobSDK,
    doc_py_example=_TERMINATE_EXAMPLE,
    arg_docstrings={"name": "Name of the job.", "job_id": "Unique ID of the job"},
)
def terminate(
    name: Optional[str] = None, job_id: Optional[str] = None, *, _sdk: JobSDK
) -> str:
    """Terminate a job.

    This command is asynchronous, so it always returns immediately.

    Returns the id of the terminated job.
    """
    return _sdk.terminate(name=name, job_id=job_id)


_ARCHIVE_EXAMPLE = """
import anyscale

anyscale.job.archive(name="my-job")
"""


@sdk_command(
    _JOB_SDK_SINGLETON_KEY,
    JobSDK,
    doc_py_example=_ARCHIVE_EXAMPLE,
    arg_docstrings={"name": "Name of the job.", "job_id": "Unique ID of the job"},
)
def archive(
    name: Optional[str] = None, job_id: Optional[str] = None, *, _sdk: JobSDK
) -> str:
    """Archive a job.

    This command is asynchronous, so it always returns immediately.

    Returns the id of the archived job.
    """
    return _sdk.archive(name=name, job_id=job_id)


_WAIT_EXAMPLE = """\
import anyscale

anyscale.job.wait(name="my-job", timeout_s=180)"""


@sdk_command(
    _JOB_SDK_SINGLETON_KEY,
    JobSDK,
    doc_py_example=_WAIT_EXAMPLE,
    arg_docstrings={
        "name": "Name of the job.",
        "job_id": "Unique ID of the job",
        "state": "Target state of the job",
        "timeout_s": "Number of seconds to wait before timing out, this timeout will not affect job execution",
    },
)
def wait(
    *,
    name: Optional[str] = None,
    job_id: Optional[str] = None,
    state: Union[JobState, str] = JobState.SUCCEEDED,
    timeout_s: float = 1800,
    _sdk: JobSDK
):
    """"Wait for a job to enter a specific state."""
    _sdk.wait(name=name, job_id=job_id, state=state, timeout_s=timeout_s)


_LOGS_EXAMPLE = """\
import anyscale

anyscale.job.logs(name="my-job", run="my-run-name)"""


@sdk_command(
    _JOB_SDK_SINGLETON_KEY,
    JobSDK,
    doc_py_example=_WAIT_EXAMPLE,
    arg_docstrings={
        "name": "Name of the job",
        "job_id": "Unique ID of the job",
        "run": "The name of the run to query, query run names using anyscale.job.status",
        "follow": "Whether to follow the log",
    },
)
def logs(
    *,
    name: Optional[str] = None,
    job_id: Optional[str] = None,
    run: Optional[str] = None,
    follow: bool = False,
    _sdk: JobSDK
) -> str:
    """"Query the jobs for a job run."""
    return _sdk.logs(name=name, job_id=job_id, run=run, follow=follow)
