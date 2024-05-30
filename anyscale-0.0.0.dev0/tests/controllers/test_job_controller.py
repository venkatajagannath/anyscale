import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
from typing import Any, Dict, List, Optional
from unittest.mock import ANY, call, MagicMock, Mock, mock_open, patch

from asynctest import CoroutineMock
import click
import pytest
import yaml

from anyscale.anyscale_pydantic import ValidationError
from anyscale.client.openapi_client.models.create_internal_production_job import (
    CreateInternalProductionJob,
)
from anyscale.client.openapi_client.models.ha_job_states import HaJobStates
from anyscale.client.openapi_client.models.production_job_config import (
    ProductionJobConfig,
)
from anyscale.controllers.job_controller import (
    JobController,
    LogsLogger,
)
from anyscale.models.job_model import _working_dir_is_remote_uri, JobConfig
from anyscale.sdk.anyscale_client.models.compute_template import ComputeTemplate
from anyscale.util import PROJECT_NAME_ENV_VAR
from anyscale.utils.runtime_env import is_dir_remote_uri
from frontend.cli.anyscale.client.openapi_client.models.create_job_queue_config import (
    CreateJobQueueConfig,
)


CONDA_DICT = {"dependencies": ["pip", {"pip": ["pip-install-test==0.5"]}]}
PIP_LIST = ["requests==1.0.0", "pip-install-test"]
ENV_VARS_DICT = {"TEST_ENV_VAR": "test_value"}


class FakeLogger(LogsLogger):
    logs: List[str] = []

    def open_block(self, *args, **kwargs,) -> None:
        pass

    def log(self, msg: str):
        self.logs.append(msg)
        print(msg)


@pytest.fixture()
def test_directory():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir)
        subdir = path / "subdir"
        subdir.mkdir(parents=True)
        requirements_file = subdir / "requirements.txt"
        with requirements_file.open(mode="w") as f:
            print("\n".join(PIP_LIST), file=f)

        good_conda_file = subdir / "good_conda_env.yaml"
        with good_conda_file.open(mode="w") as f:
            yaml.dump(CONDA_DICT, f)

        bad_conda_file = subdir / "bad_conda_env.yaml"
        with bad_conda_file.open(mode="w") as f:
            print("% this is not a YAML file %", file=f)

        old_dir = os.getcwd()
        os.chdir(tmp_dir)
        yield subdir, requirements_file, good_conda_file, bad_conda_file
        os.chdir(old_dir)


@pytest.fixture()
def patch_jobs_anyscale_api_client(base_mock_anyscale_api_client: Mock):
    base_mock_anyscale_api_client.get_cluster_environment_build = Mock(
        return_value=Mock(result=Mock(status="succeeded"))
    )
    with patch.multiple(
        "anyscale.cluster_env",
        get_auth_api_client=Mock(
            return_value=Mock(anyscale_api_client=base_mock_anyscale_api_client)
        ),
    ):
        yield


@pytest.mark.parametrize("workspace_id", [None, "test_workspace_id"])
def test_generate_config_from_entrypoint(
    mock_auth_api_client, workspace_id: Optional[str]
):
    mock_logger = Mock()
    job_controller = JobController(log=mock_logger)
    entrypoint = ["python", "test.py"]
    name = "test_name"
    description = "test_description"

    mock_get_default_cluster_compute = Mock(
        return_value=Mock(id="mock_compute_config_id")
    )

    mock_validate_successful_build = Mock()
    mock_get_default_cluster_env_build = Mock(return_value=Mock(id="mock_build_id"))
    with patch.multiple(
        "anyscale.models.job_model",
        validate_successful_build=mock_validate_successful_build,
        get_default_cluster_compute=mock_get_default_cluster_compute,
        get_default_cluster_env_build=mock_get_default_cluster_env_build,
    ):
        job_config = job_controller.generate_config_from_entrypoint(
            entrypoint, name, description, workspace_id
        )

    assert job_config.entrypoint == "python test.py"
    assert job_config.name == name
    assert job_config.description == description
    assert job_config.workspace_id == workspace_id


@pytest.mark.parametrize("add_extra_field", [True, False])
def test_config_validation(add_extra_field, mock_auth_api_client):
    """
    This test checks that an error is thrown if extra/mispelled fields
    are added into the config file
    """
    mock_logger = Mock()
    job_controller = JobController(log=mock_logger)

    name = "test_job_name"
    description = "mock_description"
    build_id = "test_build_id"
    compute_config_id = "test_compute_config_id"
    project_id = "test_project_id"
    extra_field_value = "*****"
    config_dict = {
        "name": name,
        "description": description,
        "entrypoint": "python test.py",
        "project_id": project_id,
        "build_id": build_id,
        "compute_config_id": compute_config_id,
    }
    if add_extra_field:
        extra_field_value = "*****"
        config_dict["extra_field"] = extra_field_value

    mock_validate_successful_build = Mock()
    with patch(
        "builtins.open", mock_open(read_data=json.dumps(config_dict))
    ), patch.multiple("os.path", exists=Mock(return_value=True)), patch.multiple(
        "anyscale.models.job_model",
        validate_successful_build=mock_validate_successful_build,
    ), patch.multiple(
        "anyscale.controllers.job_controller", validate_job_config_dict=Mock(),
    ):
        if add_extra_field:
            with pytest.raises(ValidationError):
                job_controller.generate_config_from_file(
                    "test_job_config_file", name=name, description=description,
                )
        else:
            job_controller.generate_config_from_file(
                "test_job_config_file", name=name, description=description,
            )


@pytest.mark.parametrize(
    "config_dict",
    [
        {
            "entrypoint": "mock_entrypoint",
            "build_id": "mock_build_id",
            "compute_config_id": "cpt_123",
        },
        {
            "entrypoint": "mock_entrypoint",
            "cluster_env": "mock_cluster_env",
            "compute_config": "mock_compute_config",
        },
        {
            "entrypoint": "mock_entrypoint",
            "compute_config": {
                "cloud_id": "mock_cloud_id",
                "region": "mock_region",
                "head_node_type": {"name": "head", "instance_type": "m5.large"},
                "worker_node_types": [],
            },
        },
        {
            "entrypoint": "mock_entrypoint",
            "cluster_env": "mock_cluster_env",
            "cloud": "mock_cloud",
        },
        {"entrypoint": "mock_entrypoint", "cluster_env": "mock_cluster_env"},
        {"entrypoint": "mock_entrypoint", "cloud": "mock_cloud"},
        {"entrypoint": "mock_entrypoint"},
        {"entrypoint": "mock_entrypoint", "project_id": "specified_project_id"},
        # Use-cases using job queues
        {
            "entrypoint": "mock_entrypoint",
            "build_id": "mock_build_id",
            "compute_config_id": "cpt_123",
            "job_queue_config": {
                "job_queue_spec": {
                    "job_queue_name": "mock_job_queue",
                    "idle_timeout_sec": 120,
                }
            },
        },
        {
            "entrypoint": "mock_entrypoint",
            "build_id": "mock_build_id",
            "compute_config_id": "cpt_123",
            "job_queue_config": {"target_job_queue_id": "mock_job_queue_id",},
        },
        {
            "entrypoint": "mock_entrypoint",
            "build_id": "mock_build_id",
            "compute_config_id": "cpt_123",
            "job_queue_config": {
                "target_job_queue_name": "mock_job_queue_user_provided_id",
            },
        },
    ],
)
@pytest.mark.parametrize("use_default_project", [True, False])
def test_submit_job(
    mock_auth_api_client,
    config_dict: Dict[str, Any],
    use_default_project: bool,
    compute_template_test_data: ComputeTemplate,
) -> None:
    config_project_id = config_dict.get("project_id")
    mock_logger = Mock()
    job_controller = JobController(log=mock_logger)
    mock_project_definition = Mock()
    mock_project_definition.root = "/some/directory"

    def infer_project_id_mock(*args: Any, **kwargs: Any):
        if kwargs.get("project_id"):
            return kwargs.get("project_id")
        elif use_default_project:
            return "mock_default_project_id"
        else:
            return "mock_project_id"

    mock_infer_project_id = Mock(side_effect=infer_project_id_mock)
    mock_get_build_from_cluster_env_identifier = Mock(
        return_value=Mock(id="mock_build_id")
    )

    mock_override_runtime_env_config = Mock(return_value=None)

    job_controller.api_client.get_compute_template_api_v2_compute_templates_template_id_get = Mock(
        return_value=Mock(result=compute_template_test_data)
    )
    job_controller.api_client.search_compute_templates_api_v2_compute_templates_search_post = Mock(
        return_value=Mock(results=[compute_template_test_data])
    )
    mock_get_cluster_compute_from_name = Mock(return_value=compute_template_test_data)
    mock_get_default_cluster_compute = Mock(return_value=compute_template_test_data)
    mock_register_compute_template = Mock(return_value=compute_template_test_data)

    mock_validate_successful_build = Mock()
    mock_get_default_cluster_env_build = Mock(return_value=Mock(id="mock_build_id"))
    mock_get_parent_cloud_id_and_name_of_project = Mock(
        return_value=("mock_parent_cloud_id", "mock_parent_cloud_name")
    )
    with patch(
        "builtins.open", mock_open(read_data=json.dumps(config_dict))
    ), patch.multiple(
        "anyscale.models.job_model",
        validate_successful_build=mock_validate_successful_build,
        get_cluster_compute_from_name=mock_get_cluster_compute_from_name,
        get_default_cluster_compute=mock_get_default_cluster_compute,
        register_compute_template=mock_register_compute_template,
        get_build_from_cluster_env_identifier=mock_get_build_from_cluster_env_identifier,
        get_default_cluster_env_build=mock_get_default_cluster_env_build,
        get_parent_cloud_id_and_name_of_project=mock_get_parent_cloud_id_and_name_of_project,
    ), patch.multiple(
        "anyscale.controllers.job_controller",
        infer_project_id=mock_infer_project_id,
        override_runtime_env_config=mock_override_runtime_env_config,
    ), patch.object(
        JobController,
        "_get_maximum_uptime_output",
        return_value="mock maximum uptime output",
    ), patch.multiple(
        "os.path", exists=Mock(return_value=True)
    ):
        job_controller.submit(
            "mock_config_file", name="mock_name", description="mock_description"
        )
    mock_validate_successful_build.assert_called_once_with("mock_build_id")
    mock_infer_project_id.assert_called_once_with(
        job_controller.anyscale_api_client,
        job_controller.api_client,
        job_controller.log,
        project_id=config_dict.get("project_id"),
        cluster_compute_id=compute_template_test_data.id,
        cluster_compute=config_dict.get("compute_config"),
        cloud=config_dict.get("cloud"),
    )

    if config_project_id:
        final_project_id = config_project_id
    elif use_default_project:
        final_project_id = "mock_default_project_id"
    else:
        final_project_id = "mock_project_id"

    if "job_queue_config" in config_dict:
        job_queue_config_dict = config_dict["job_queue_config"]
        expected_job_queue_config = CreateJobQueueConfig(**job_queue_config_dict)
    else:
        expected_job_queue_config = None

    job_controller.api_client.create_job_api_v2_decorated_ha_jobs_create_post.assert_called_once_with(
        CreateInternalProductionJob(
            name="mock_name",
            description="mock_description",
            project_id=final_project_id,
            workspace_id=None,
            config=ProductionJobConfig(  # noqa: PIE804
                entrypoint="mock_entrypoint",
                build_id="mock_build_id",
                compute_config_id=compute_template_test_data.id,
            ),
            job_queue_config=expected_job_queue_config,
        )
    )
    assert mock_logger.info.call_count == 5
    if "cluster_env" not in config_dict and "build_id" not in config_dict:
        mock_get_default_cluster_env_build.assert_called_once_with()
    if "compute_config" in config_dict:
        compute_config = config_dict["compute_config"]
        if isinstance(compute_config, str):
            mock_get_cluster_compute_from_name.assert_called_with(compute_config)
        elif isinstance(compute_config, dict):
            mock_register_compute_template.assert_called_once_with(compute_config)
    elif "cloud" in config_dict:
        mock_get_default_cluster_compute.assert_called_once_with(
            cloud_name=config_dict["cloud"], project_id=None
        )
    elif "compute_config_id" in config_dict:
        mock_get_default_cluster_compute.assert_not_called()
    if "project_id" in config_dict:
        mock_get_parent_cloud_id_and_name_of_project.assert_called_once_with(
            config_dict.get("project_id")
        )


@pytest.mark.parametrize("include_all_users", [False, True])
@pytest.mark.parametrize("name", ["mock_job_name", None])
@pytest.mark.parametrize("job_id", ["mock_job_id", None])
@pytest.mark.parametrize("project_id", ["mock_project_id", None])
@pytest.mark.parametrize(
    "passed_service_id", [False, True]
)  # Whether `job_id` is id of job or service
@pytest.mark.parametrize("include_archived", [False, True])
def test_list_jobs(  # noqa: PLR0913
    mock_auth_api_client,
    include_all_users: bool,
    name: Optional[str],
    job_id: Optional[str],
    project_id: Optional[str],
    passed_service_id: bool,
    include_archived: bool,
) -> None:
    job_controller = JobController()
    job_controller.api_client.get_user_info_api_v2_userinfo_get = Mock(
        return_value=Mock(result=Mock(id="mock_user_id"))
    )
    job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get = Mock(
        return_value=Mock(
            results=[Mock(config=Mock(entrypoint=""))] * 10,
            metadata=Mock(next_paging_token="paging_token"),
        )
    )
    job_controller.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get = Mock(
        return_value=Mock(
            result=Mock(
                config=Mock(entrypoint="", is_service=passed_service_id),
                is_service=passed_service_id,
            )
        )
    )

    if passed_service_id and job_id is not None:
        # Raise error if trying to list id that is not valid for the command.
        # Eg: job_id providied for `anyscale service list`
        with pytest.raises(click.ClickException):
            job_controller.list(
                include_all_users=include_all_users,
                name=name,
                job_id=job_id,
                project_id=project_id,
                include_archived=include_archived,
                max_items=20,
            )
        return
    else:
        job_controller.list(
            include_all_users=include_all_users,
            name=name,
            job_id=job_id,
            project_id=project_id,
            include_archived=include_archived,
            max_items=20,
        )

    if job_id:
        job_controller.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get.assert_called_once_with(
            job_id
        )
        job_controller.api_client.get_user_info_api_v2_userinfo_get.assert_not_called()
        job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.assert_not_called()
    else:
        creator_id: Optional[str] = None
        if not include_all_users:
            creator_id = "mock_user_id"
            job_controller.api_client.get_user_info_api_v2_userinfo_get.assert_called_once()
        else:
            job_controller.api_client.get_user_info_api_v2_userinfo_get.assert_not_called()
        job_controller.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get.assert_not_called()
        job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.assert_any_call(
            creator_id=creator_id,
            name=name,
            project_id=project_id,
            type_filter="BATCH_JOB",
            archive_status="ALL" if include_archived else "NOT_ARCHIVED",
            count=10,
        )
        job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.assert_any_call(
            creator_id=creator_id,
            name=name,
            project_id=project_id,
            type_filter="BATCH_JOB",
            archive_status="ALL" if include_archived else "NOT_ARCHIVED",
            count=10,
            paging_token="paging_token",
        )
        assert (
            job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.call_count
            == 2
        )


@pytest.mark.parametrize("name", ["mock_job_name", None])
@pytest.mark.parametrize("id", ["mock_job_id", None])
def test_terminate_job(
    mock_auth_api_client, name: Optional[str], id: Optional[str],  # noqa: A002
) -> None:
    job_controller = JobController()
    job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get = Mock(
        return_value=Mock(results=[Mock(id="mock_job_id")])
    )
    job_controller.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get = Mock(
        return_value=Mock(result=Mock(id="mock_job_id"))
    )
    if not name and not id:
        with pytest.raises(click.ClickException):
            job_controller.terminate(id, name)
        return
    else:
        job_controller.terminate(id, name)

    job_controller.api_client.terminate_job_api_v2_decorated_ha_jobs_production_job_id_terminate_post.assert_called_once_with(
        "mock_job_id"
    )
    if name is not None and id is None:
        job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.assert_called_once_with(
            name=name, type_filter="BATCH_JOB",
        )


@pytest.mark.parametrize("name", ["mock_job_name", None])
@pytest.mark.parametrize("id", ["mock_job_id", None])
def test_archive_job(
    mock_auth_api_client, name: Optional[str], id: Optional[str],  # noqa: A002
) -> None:
    job_controller = JobController()
    job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get = Mock(
        return_value=Mock(results=[Mock(id="mock_job_id")])
    )
    job_controller.api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get = Mock(
        return_value=Mock(result=Mock(id="mock_job_id"))
    )
    if not name and not id:
        with pytest.raises(click.ClickException):
            job_controller.archive(id, name)
        return
    else:
        job_controller.archive(id, name)

    job_controller.api_client.archive_job_api_v2_decorated_ha_jobs_production_job_id_archive_post.assert_called_once_with(
        "mock_job_id"
    )
    if name is not None and id is None:
        job_controller.api_client.list_decorated_jobs_api_v2_decorated_ha_jobs_get.assert_called_once_with(
            name=name, type_filter="BATCH_JOB",
        )


class TestValidateConda:
    def test_validate_conda_str(self, test_directory, patch_jobs_anyscale_api_client):
        """Tests the conda field is allowed to be a str. It represents an existing env name."""
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"conda": "env_name", "working_dir": "s3://bucket"},
        )
        assert jc.runtime_env["conda"] == "env_name"

    def test_validate_conda_invalid_path(self, patch_jobs_anyscale_api_client):
        """If a path to a YAML file is given, it should error if the path does not exist."""
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"conda": "../bad_path.yaml"},
            )

    @pytest.mark.parametrize("absolute_path", [True, False])
    def test_validate_conda_valid_file(
        self, test_directory, absolute_path, patch_jobs_anyscale_api_client
    ):
        _, _, good_conda_file, _ = test_directory

        if absolute_path:
            good_conda_file = good_conda_file.resolve()

        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"conda": str(good_conda_file)},
        )
        assert jc.runtime_env["conda"] == CONDA_DICT

    @pytest.mark.parametrize("absolute_path", [True, False])
    def test_validate_conda_invalid_file(
        self, test_directory, absolute_path, patch_jobs_anyscale_api_client
    ):
        """We should error if a .yml file with invalid YAML format is specified."""
        _, _, _, bad_conda_file = test_directory

        if absolute_path:
            bad_conda_file = bad_conda_file.resolve()

        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"conda": str(bad_conda_file)},
            )

    def test_validate_conda_valid_dict(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"conda": CONDA_DICT},
        )
        assert jc.runtime_env["conda"] == CONDA_DICT


class TestValidatePip:
    def test_validate_pip_invalid_path(self, patch_jobs_anyscale_api_client):
        """If a path to a .txt file is given, it should error if the path does not exist."""
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"pip": "../bad_path.txt"},
            )

    @pytest.mark.parametrize("absolute_path", [True, False])
    def test_validate_pip_valid_file(
        self, test_directory, absolute_path, patch_jobs_anyscale_api_client
    ):
        _, requirements_file, _, _ = test_directory

        if absolute_path:
            requirements_file = requirements_file.resolve()

        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"pip": str(requirements_file)},
        )
        assert jc.runtime_env["pip"] == PIP_LIST

    def test_validate_pip_valid_list(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"pip": PIP_LIST},
        )
        assert jc.runtime_env["pip"] == PIP_LIST


class TestValidateEnvVars:
    def test_validate_env_vars_valid_dict(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"env_vars": ENV_VARS_DICT},
        )
        assert jc.runtime_env["env_vars"] == ENV_VARS_DICT

    def test_validate_env_vars_invalid_dict(self, patch_jobs_anyscale_api_client):
        """Error if env_vars is not a dict."""
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"env_vars": "not_a_dict"},
            )

    def test_validate_env_vars_not_dict_str(self, patch_jobs_anyscale_api_client):
        """Error if env_vars is not a Dict[str, str]."""
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"env_vars": {"key", 123}},
            )
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"env_vars": {"key": "value", 123: "value2"}},
            )


class TestValidateUploadPath:
    @pytest.mark.parametrize("working_dir", [None, ".", "s3://bucket", "gs://bucket"])
    @pytest.mark.parametrize("upload_path", [None, "s3://bucket", "gs://bucket"])
    def test_validate_working_dir_and_upload_path_combinations(
        self, patch_jobs_anyscale_api_client, working_dir: str, upload_path: str
    ):
        """Test combinations of working_dir and upload_path
        Exceptions:
        1. Working_dir is a remote uri and upload_path is defined
        2. Working_dir is None and upload_path is defined
        """
        runtime_env = {}
        if working_dir:
            runtime_env["working_dir"] = working_dir
        if upload_path:
            runtime_env["upload_path"] = upload_path

        if is_dir_remote_uri(working_dir) and is_dir_remote_uri(upload_path):
            with pytest.raises(
                click.ClickException,
                match=r"`upload_path` was specified, but `working_dir` is not a local directory",
            ):
                JobConfig(
                    entrypoint="ls",
                    build_id="123",
                    compute_config_id="test",
                    runtime_env=runtime_env,
                )
        elif working_dir is None and is_dir_remote_uri(upload_path):
            with pytest.raises(
                click.ClickException,
                match=r"upload_path` was specified, but no `working_dir` is defined",
            ):
                JobConfig(
                    entrypoint="ls",
                    build_id="123",
                    compute_config_id="test",
                    runtime_env=runtime_env,
                )
        else:
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env=runtime_env,
            )

    def test_reject_non_s3_or_gs_upload_path(self, patch_jobs_anyscale_api_client):
        """If upload_path is specified, it must be an s3 or gs path."""
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"upload_path": "file://some_file"},
            )

    def test_accept_s3_upload_path(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"working_dir": "./", "upload_path": "s3://some_bucket"},
        )
        assert jc.runtime_env["upload_path"] == "s3://some_bucket"

    def test_accept_gs_upload_path(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"working_dir": "./", "upload_path": "gs://some_bucket"},
        )
        assert jc.runtime_env["upload_path"] == "gs://some_bucket"


class TestValidateWorkingDir:
    def test_working_dir_is_remote_uri(self):
        assert _working_dir_is_remote_uri("s3://some_bucket")
        assert _working_dir_is_remote_uri("s3://some_bucket/some/path")
        assert _working_dir_is_remote_uri("fake://some_bucket/some/path/")
        assert not _working_dir_is_remote_uri("/some/path")
        assert not _working_dir_is_remote_uri("some/path/")

    def test_reject_nonexistent_local_dir(self, patch_jobs_anyscale_api_client):
        """If a local working_dir is specified, it must exist."""
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={
                    "working_dir": "/does/not/exist",
                    "upload_path": "gs://fake",
                },
            )

    def test_accept_uri(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"working_dir": "s3://path/to/archive.zip"},
        )
        assert jc.runtime_env["working_dir"] == "s3://path/to/archive.zip"


class TestValidatePyModules:
    def test_reject_local_dir(self, patch_jobs_anyscale_api_client):
        """Local directories are only supported using working_dir, not py_modules."""
        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"py_modules": ["."]},
            )

        with pytest.raises(click.ClickException):
            JobConfig(
                entrypoint="ls",
                build_id="123",
                compute_config_id="test",
                runtime_env={"py_modules": ["/tmp/dir"]},
            )

    def test_accept_uri(self, patch_jobs_anyscale_api_client):
        jc = JobConfig(
            entrypoint="ls",
            build_id="123",
            compute_config_id="test",
            runtime_env={"py_modules": ["s3://path/to/archive.zip"]},
        )
        assert jc.runtime_env["py_modules"] == ["s3://path/to/archive.zip"]


class TestComputeConfig:
    @pytest.fixture()
    def patch_calls_to_get_compute_config(self,):
        mock_get_default_cluster_compute = Mock(
            return_value=Mock(id="mock_default_compute_config_id")
        )
        mock_get_cluster_compute_from_name = Mock(
            return_value=Mock(id="mock_existing_compute_config_id")
        )
        mock_register_compute_template = Mock(
            return_value=Mock(id="mock_registered_compute_config_id")
        )
        mock_get_parent_cloud_id_and_name_of_project = Mock(
            return_value=("mock_parent_cloud_id", "mock_parent_cloud_name")
        )

        with patch.multiple(
            "anyscale.models.job_model",
            get_default_cluster_compute=mock_get_default_cluster_compute,
            get_cluster_compute_from_name=mock_get_cluster_compute_from_name,
            register_compute_template=mock_register_compute_template,
            get_parent_cloud_id_and_name_of_project=mock_get_parent_cloud_id_and_name_of_project,
        ):
            yield mock_get_default_cluster_compute, mock_get_cluster_compute_from_name, mock_register_compute_template, mock_get_parent_cloud_id_and_name_of_project

    def test_fill_compute_config_id_from_compute_config_id(
        self, patch_jobs_anyscale_api_client, patch_calls_to_get_compute_config
    ):
        (
            mock_get_default_cluster_compute,
            mock_get_cluster_compute_from_name,
            mock_register_compute_template,
            mock_get_parent_cloud_id_and_name_of_project,
        ) = patch_calls_to_get_compute_config
        jc = JobConfig(
            entrypoint="ls", compute_config_id="mock_existing_compute_config_id",
        )
        assert jc.compute_config_id == "mock_existing_compute_config_id"
        mock_get_default_cluster_compute.assert_not_called()
        mock_get_cluster_compute_from_name.assert_not_called()
        mock_register_compute_template.assert_not_called()
        mock_get_parent_cloud_id_and_name_of_project.assert_not_called()

    def test_fill_compute_config_id_from_compute_config_name(
        self, patch_jobs_anyscale_api_client, patch_calls_to_get_compute_config
    ):
        (
            mock_get_default_cluster_compute,
            mock_get_cluster_compute_from_name,
            mock_register_compute_template,
            mock_get_parent_cloud_id_and_name_of_project,
        ) = patch_calls_to_get_compute_config
        jc = JobConfig(
            entrypoint="ls", compute_config="mock_existing_compute_config_name",
        )
        assert jc.compute_config_id == "mock_existing_compute_config_id"
        mock_get_default_cluster_compute.assert_not_called()
        mock_get_cluster_compute_from_name.assert_called_once_with(
            "mock_existing_compute_config_name"
        )
        mock_register_compute_template.assert_not_called()
        mock_get_parent_cloud_id_and_name_of_project.assert_not_called()

    def test_fill_compute_config_id_from_compute_config_dict(
        self, patch_jobs_anyscale_api_client, patch_calls_to_get_compute_config
    ):
        (
            mock_get_default_cluster_compute,
            mock_get_cluster_compute_from_name,
            mock_register_compute_template,
            mock_get_parent_cloud_id_and_name_of_project,
        ) = patch_calls_to_get_compute_config
        compute_config_dict = {
            "cloud_id": "mock_cloud_id",
            "region": "mock_region",
            "head_node_type": {"name": "head", "instance_type": "m5.large"},
            "worker_node_types": [],
        }
        jc = JobConfig(entrypoint="ls", compute_config=compute_config_dict,)
        assert jc.compute_config_id == "mock_registered_compute_config_id"
        mock_get_default_cluster_compute.assert_not_called()
        mock_get_cluster_compute_from_name.assert_not_called()
        mock_register_compute_template.assert_called_once_with(compute_config_dict)
        mock_get_parent_cloud_id_and_name_of_project.assert_not_called()

    def test_fill_compute_config_id_from_cloud(
        self, patch_jobs_anyscale_api_client, patch_calls_to_get_compute_config
    ):
        (
            mock_get_default_cluster_compute,
            mock_get_cluster_compute_from_name,
            mock_register_compute_template,
            mock_get_parent_cloud_id_and_name_of_project,
        ) = patch_calls_to_get_compute_config
        jc = JobConfig(entrypoint="ls", cloud="mock_cloud",)
        assert jc.compute_config_id == "mock_default_compute_config_id"
        mock_get_default_cluster_compute.assert_called_once_with(
            cloud_name="mock_cloud", project_id=None
        )
        mock_get_cluster_compute_from_name.assert_not_called()
        mock_register_compute_template.assert_not_called()
        mock_get_parent_cloud_id_and_name_of_project.assert_not_called()

    def test_fill_compute_config_id_from_project_with_cloud_isolation(
        self, patch_jobs_anyscale_api_client, patch_calls_to_get_compute_config
    ):
        (
            mock_get_default_cluster_compute,
            mock_get_cluster_compute_from_name,
            mock_register_compute_template,
            mock_get_parent_cloud_id_and_name_of_project,
        ) = patch_calls_to_get_compute_config
        jc = JobConfig(entrypoint="ls", project_id="mock_project_id")
        assert jc.compute_config_id == "mock_default_compute_config_id"
        mock_get_default_cluster_compute.assert_called_once_with(
            cloud_name="mock_parent_cloud_name", project_id=None
        )
        mock_get_cluster_compute_from_name.assert_not_called()
        mock_register_compute_template.assert_not_called()
        mock_get_parent_cloud_id_and_name_of_project.assert_called_once_with(
            "mock_project_id"
        )


@pytest.mark.parametrize("project_id", [None, "proj_id"])
@pytest.mark.parametrize("project_name", [None, "proj_name"])
@pytest.mark.parametrize("project_name_env_var", [None, "proj_name_env"])
def test_validate_project_id_field(
    project_id: Optional[str],
    project_name: Optional[str],
    project_name_env_var: Optional[str],
):
    mock_get_proj_id_from_name = Mock(return_value="proj_id")
    mock_validate_successful_build = Mock()
    config_dict = {
        "entrypoint": "mock_entrypoint",
        "build_id": "mock_build_id",
        "compute_config_id": "mock_compute_config_id",
        "project_id": project_id,
        "project": project_name,
    }
    mock_os_dict = (
        {PROJECT_NAME_ENV_VAR: project_name_env_var} if project_name_env_var else {}
    )
    with patch.multiple(
        "anyscale.models.job_model",
        get_proj_id_from_name=mock_get_proj_id_from_name,
        validate_successful_build=mock_validate_successful_build,
    ), patch.dict(os.environ, mock_os_dict):
        if project_id and project_name:
            with pytest.raises(click.ClickException):
                job_config = JobConfig.parse_obj(config_dict)
        else:
            job_config = JobConfig.parse_obj(config_dict)
            if project_name_env_var:
                assert job_config.project_id == "proj_id"
                mock_get_proj_id_from_name.assert_called_once_with(project_name_env_var)
            elif project_name:
                assert job_config.project_id == "proj_id"
                mock_get_proj_id_from_name.assert_called_once_with(project_name)
            else:
                assert job_config.project_id == project_id


def test_logs_streaming(mock_auth_api_client) -> None:
    job_controller = JobController()
    prod_job_id = "prodjob_123"
    last_job_run_id = "job_123"
    mock_job = Mock(
        id=prod_job_id,
        last_job_run_id=last_job_run_id,
        state=Mock(current_state=HaJobStates.RUNNING),
    )
    job_controller.log = Mock()
    job_controller.log.spinner = LogsLogger().spinner
    job_controller._wait_for_a_job_run = Mock(return_value=mock_job)  # type: ignore
    mock_ff_response = Mock()
    mock_ff_response.result = Mock()
    mock_ff_response.result.is_on = True
    job_controller.api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get = Mock(
        return_value=mock_ff_response
    )

    get_jobs_logs_from_storage_bucket_streaming_mock = CoroutineMock(
        side_effect=[
            ("1\n2\n3\n", "next_token", 10, False),
            ("4\n5\n6\n", "next_token_2", 10, True),
            ("7\n8\n9\n10\n", "next_token_3", 10, True),
            ("", "next_token_3", 10, True),
            ("", "next_token_3", 10, True),
        ]
    )

    with patch(
        "anyscale.controllers.job_controller._get_job_logs_from_storage_bucket_streaming",
        new=get_jobs_logs_from_storage_bucket_streaming_mock,
    ):
        job_controller.logs(job_id=prod_job_id, should_follow=True)

    get_jobs_logs_from_storage_bucket_streaming_mock.assert_has_awaits(
        [
            call(
                ANY,
                ANY,
                job_run_id=last_job_run_id,
                remove_escape_chars=False,
                next_page_token=None,
                cluster_journal_events_start_line=0,
                no_cluster_journal_events=False,
            ),
            call(
                ANY,
                ANY,
                job_run_id=last_job_run_id,
                remove_escape_chars=False,
                next_page_token="next_token",
                cluster_journal_events_start_line=10,
                no_cluster_journal_events=False,
            ),
            call(
                ANY,
                ANY,
                job_run_id=last_job_run_id,
                remove_escape_chars=False,
                next_page_token="next_token_2",
                cluster_journal_events_start_line=10,
                no_cluster_journal_events=False,
            ),
            call(
                ANY,
                ANY,
                job_run_id=last_job_run_id,
                remove_escape_chars=False,
                next_page_token="next_token_3",
                cluster_journal_events_start_line=10,
                no_cluster_journal_events=False,
            ),
            call(
                ANY,
                ANY,
                job_run_id=last_job_run_id,
                remove_escape_chars=False,
                next_page_token="next_token_3",
                cluster_journal_events_start_line=10,
                no_cluster_journal_events=False,
            ),
        ]
    )
    job_controller.log.log.assert_has_calls(
        [
            call("1"),
            call("2"),
            call("3"),
            call("4"),
            call("5"),
            call("6"),
            call("7"),
            call("8"),
            call("9"),
            call("10"),
        ]
    )


def test_job_submit_parse_logic(mock_auth_api_client) -> None:
    job_controller = JobController()
    job_controller.generate_config_from_entrypoint = Mock()  # type: ignore
    job_controller.generate_config_from_file = Mock()  # type: ignore
    job_controller.submit_from_config = Mock()  # type: ignore

    # We are not in a workspace, so entrypoint should not be allowed
    with pytest.raises(click.ClickException):
        job_controller.submit(
            "file", entrypoint=["entrypoint"], is_entrypoint_cmd=False
        )

    with pytest.raises(click.ClickException):
        job_controller.submit("file", entrypoint=["entrypoint"], is_entrypoint_cmd=True)

    with pytest.raises(click.ClickException):
        job_controller.submit(
            "file", entrypoint=["entrypoint", "commands"], is_entrypoint_cmd=True
        )

    # Simulate a workspace
    with patch.dict(
        os.environ, {"ANYSCALE_EXPERIMENTAL_WORKSPACE_ID": "fake_workspace_id"}
    ):
        # Fails due to is_entrypoint_cmd being False
        with pytest.raises(click.ClickException):
            job_controller.submit(
                "file", entrypoint=["entrypoint"], is_entrypoint_cmd=False
            )

        mock_config = Mock()
        job_controller.generate_config_from_file.return_value = mock_config
        job_controller.submit("file", entrypoint=[], is_entrypoint_cmd=False)
        job_controller.generate_config_from_file.assert_called_once_with(
            "file", name=None, description=None, workspace_id="fake_workspace_id"
        )
        job_controller.submit_from_config.assert_called_once_with(mock_config)
        job_controller.generate_config_from_file.reset_mock()
        job_controller.submit_from_config.reset_mock()

        mock_config = Mock()
        job_controller.generate_config_from_entrypoint.return_value = mock_config
        job_controller.submit("file", entrypoint=["entrypoint"], is_entrypoint_cmd=True)
        job_controller.generate_config_from_entrypoint.assert_called_once_with(
            ["file", "entrypoint"], None, None, "fake_workspace_id"
        )
        job_controller.submit_from_config.assert_called_once_with(mock_config)


def test_job_wait(mock_auth_api_client) -> None:
    job_controller = JobController()
    job_controller.api_client = Mock()
    job_controller._resolve_job_object = Mock(return_value=SimpleNamespace(id="id"))  # type: ignore
    spin_mock = MagicMock()
    job_controller.log = MagicMock()
    job_controller.log.spinner.return_value.__enter__.return_value = spin_mock

    def get_job_state(states_to_return, mock_state=None):
        if mock_state is None:
            mock_state = Mock()

        mock_state.i = 0

        def g(*args, **kwargs):
            nonlocal mock_state
            state = states_to_return[mock_state.i]
            mock_state.i += 1
            mock_state.state = state
            return state

        return g, mock_state

    # Test the happy path
    states_to_return = ["PENDING", "AWAITING_CLUSTER_START", "SUCCESS"]
    job_controller._get_job_state, mock_state = get_job_state(states_to_return)  # type: ignore

    assert job_controller.wait("name")
    assert mock_state.i == 3
    assert mock_state.state == "SUCCESS"
    spin_mock.succeed.assert_called_once()

    # Test the failure case
    spin_mock.reset_mock()
    states_to_return = [
        "PENDING",
        "AWAITING_CLUSTER_START",
        "ERRORED",
        "OUT_OF_RETRIES",
    ]
    job_controller._get_job_state, mock_state = get_job_state(states_to_return)  # type: ignore

    with pytest.raises(click.ClickException):
        job_controller.wait("name")
    assert mock_state.i == 4
    assert mock_state.state == "OUT_OF_RETRIES"
    spin_mock.fail.assert_called_once()

    # Test the non default case
    spin_mock.reset_mock()
    states_to_return = [
        "PENDING",
        "AWAITING_CLUSTER_START",
        "ERRORED",
        "SHOULD_NOT_REACH",
        "SHOULD_NOT_REACH",
        "SHOULD_NOT_REACH",
    ]
    job_controller._get_job_state, mock_state = get_job_state(states_to_return)  # type: ignore

    assert job_controller.wait("name", target_state="ERRORED")
    assert mock_state.state == "ERRORED"
    assert mock_state.i == 3
    spin_mock.succeed.assert_called_once()

    # Test timeout logic
    spin_mock.reset_mock()
    states_to_return = [
        "PENDING",
        "AWAITING_CLUSTER_START",
        "ERRORED",
        "SHOULD_NOT_REACH",
        "SHOULD_NOT_REACH",
        "SHOULD_NOT_REACH",
    ]
    job_controller._get_job_state, mock_state = get_job_state(states_to_return)  # type: ignore

    with pytest.raises(click.ClickException):
        job_controller.wait("name", timeout_secs=0.00001)

    # Test parsing logic
    with pytest.raises(click.ClickException):
        job_controller.wait("name", target_state="FAKE_STATE")


def test_override_runtime_env_config_and_infer_project_id(mock_auth_api_client):
    """Test helper functions in submit_from_config function
    Test that runtime_env is overwrriten from override_runtime_env_config
    Test the project_id is autopopulated from infer_project_id
    """
    config_dict = {
        "name": "mock_name",
        "entrypoint": "mock_entrypoint",
        "description": "mock_description",
        "build_id": "mock_build_id",
        "compute_config_id": "mock_compute_config_id",
    }

    assert "project_id" not in config_dict

    mock_project_id = "default"

    with patch.multiple(
        "anyscale.models.job_model", validate_successful_build=Mock(),
    ):
        job_config = JobConfig.parse_obj(config_dict)

    new_runtime_env = {"working_dir": "s3://bucket"}
    mock_override_config = Mock(return_value=new_runtime_env)

    mock_infer_project_id = Mock(return_value=mock_project_id)

    with patch.multiple(
        "anyscale.controllers.job_controller",
        infer_project_id=mock_infer_project_id,
        override_runtime_env_config=mock_override_config,
    ):
        job_controller = JobController()
        job_controller.api_client.create_job_api_v2_decorated_ha_jobs_create_post = (
            Mock()
        )
        job_controller._get_maximum_uptime_output = Mock()
        job_controller.submit_from_config(job_config)
        job_controller.api_client.create_job_api_v2_decorated_ha_jobs_create_post.assert_called_once_with(
            CreateInternalProductionJob(
                name=config_dict["name"],
                description=config_dict["description"],
                project_id=mock_project_id,
                config=ProductionJobConfig(
                    entrypoint=job_config.entrypoint,
                    runtime_env=new_runtime_env,
                    build_id=job_config.build_id,
                    compute_config_id=job_config.compute_config_id,
                    max_retries=job_config.max_retries,
                ),
            )
        )
