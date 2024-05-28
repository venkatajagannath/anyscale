from dataclasses import dataclass
import os
import re
from typing import Optional

import pytest

from anyscale.job.models import (
    JobConfig,
    JobRunState,
    JobRunStatus,
    JobState,
    JobStatus,
)


@dataclass
class JobConfigFile:
    name: str
    expected_config: Optional[JobConfig] = None
    expected_error: Optional[str] = None

    def get_path(self) -> str:
        return os.path.join(
            os.path.dirname(__file__), "test_files/job_config_files", self.name
        )


TEST_CONFIG_FILES = [
    JobConfigFile(
        "minimal.yaml", expected_config=JobConfig(entrypoint="python test.py"),
    ),
    JobConfigFile(
        "full.yaml",
        expected_config=JobConfig(
            name="test-name-from-file",
            image_uri="docker.io/library/test:latest",
            compute_config="test-compute-config",
            working_dir="test-working-dir",
            excludes=["test"],
            requirements=["pip-install-test"],
            entrypoint="python test.py",
            max_retries=5,
        ),
    ),
    JobConfigFile(
        "points_to_requirements_file.yaml",
        expected_config=JobConfig(
            entrypoint="python test.py", requirements="some_requirements_file.txt",
        ),
    ),
    JobConfigFile(
        "unrecognized_option.yaml",
        expected_error=re.escape(
            "__init__() got an unexpected keyword argument 'bad_option'"
        ),
    ),
]


class TestJobConfig:
    def test_invalid_entrypoint(self):
        with pytest.raises(ValueError, match="'entrypoint' cannot be empty."):
            JobConfig()

        with pytest.raises(ValueError, match="'entrypoint' cannot be empty."):
            JobConfig(entrypoint="")

        with pytest.raises(TypeError, match="'entrypoint' must be a string."):
            JobConfig(entrypoint=b"oops")

    def test_invalid_max_retries(self):
        with pytest.raises(TypeError, match="'max_retries' must be an int."):
            JobConfig(entrypoint="python test.py", max_retries="1")

        with pytest.raises(ValueError, match="'max_retries' must be >= 0."):
            JobConfig(entrypoint="python test.py", max_retries=-1)

    def test_options(self):
        config = JobConfig(entrypoint="python test.py")

        options = {
            "name": "test-name",
            "image_uri": "docker.io/libaray/test-image:latest",
            "compute_config": "test-compute-config",
            "requirements": ["pip-install-test"],
            "working_dir": ".",
            "excludes": ["some-path"],
            "max_retries": 100,
        }

        # Test setting fields one at a time.
        for option, val in options.items():
            assert config.options(**{option: val}) == JobConfig(
                entrypoint="python test.py", **{option: val}
            )

        # Test setting fields all at once.
        assert config.options(**options) == JobConfig(
            entrypoint="python test.py", **options
        )

    @pytest.mark.parametrize("config_file", TEST_CONFIG_FILES)
    def test_from_config_file(self, config_file: JobConfigFile):
        if config_file.expected_error is not None:
            with pytest.raises(Exception, match=config_file.expected_error):
                JobConfig.from_yaml(config_file.get_path())

            return

        assert config_file.expected_config == JobConfig.from_yaml(
            config_file.get_path()
        )


class TestJobStatus:
    @pytest.mark.parametrize(
        "state",
        [
            JobState.STARTING,
            JobState.RUNNING,
            JobState.FAILED,
            JobState.SUCCEEDED,
            JobState.UNKNOWN,
        ],
    )  # type: ignore
    def test_version_states(self, state: JobState):
        # id, name, state, config
        assert (
            JobStatus(
                id="test-job-id",
                name="test-job-name",
                state=state,
                config=JobConfig(entrypoint="python test.py"),
                runs=[],
            ).state
            == state
        )

    def test_unknown_states(self):
        with pytest.raises(
            ValueError, match="'NOT_REAL_STATE' is not a valid JobState"
        ):
            JobStatus(
                id="test-job-id",
                name="test-job-name",
                state="NOT_REAL_STATE",
                config=JobConfig(entrypoint="python test.py"),
                runs=[],
            )

    def test_job_runs(self):
        status = JobStatus(
            id="test-job-id",
            name="test-job-name",
            state=JobState.SUCCEEDED,
            config=JobConfig(entrypoint="python test.py"),
            runs=[
                JobRunStatus(name="failed-job-run", state=JobRunState.FAILED),
                JobRunStatus(name="succeeded-job-run", state=JobRunState.SUCCEEDED),
            ],
        )

        run_states = [run.state for run in status.runs]
        assert JobRunState.FAILED in run_states
        assert JobRunState.SUCCEEDED in run_states


class TestJobRunStatus:
    @pytest.mark.parametrize(
        "state",
        [
            JobRunState.STARTING,
            JobRunState.RUNNING,
            JobRunState.FAILED,
            JobRunState.SUCCEEDED,
            JobRunState.UNKNOWN,
        ],
    )  # type: ignore
    def test_version_states(self, state: JobRunState):
        assert JobRunStatus(name="test-job-run-name", state=state).state == state

    def test_unknown_states(self):
        with pytest.raises(
            ValueError, match="'NOT_REAL_STATE' is not a valid JobRunState"
        ):
            JobRunStatus(name="test-job-run-name", state="NOT_REAL_STATE")
