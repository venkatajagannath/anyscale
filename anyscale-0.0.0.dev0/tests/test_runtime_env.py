# type: ignore

import os
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Optional
from unittest.mock import Mock, mock_open, patch

import boto3
import pytest
import smart_open

from anyscale.client.openapi_client.models.cloud_providers import CloudProviders
from anyscale.client.openapi_client.models.decoratedsession_response import (
    DecoratedsessionResponse,
)
from anyscale.utils.runtime_env import (
    _get_cloud_gs_bucket_from_cloud,
    _get_cloud_s3_bucket_from_cloud,
    autopopulate_runtime_env_for_workspace,
    infer_upload_path_and_rewrite_working_dir,
    override_runtime_env_config,
    parse_dot_env_file,
)
from anyscale.utils.workload_types import Workload


class TestRuntimeEnvOverride:
    """Test 5 cases of overriding runtime env
    1. Runtime env or working_dir is None from non-workspace
        -> If runtime_env is None, autopopulate to empty dict
        -> Else, Do nothing
    2. Working_dir is a remote uri -> Do nothing
    3. Working_dir is local and upload path is defined -> upload and rewrite working_dir
    4. Working_dir is local and upload path is not defined from workspace
        -> Autopopulate working_dir, infer upload path, upload working_dir, and rewrite working_dir
    5. Working_dir is local and upload path is not defined from non-workspace
        -> Infer upload path, upload working_dir, and rewrite working_dir

    Other Cases
    - Working_dir is not specified but upload_path is defined -> Pydantic error
    - Working_dir is a remote uri and upload_path is defined-> Pydantic error
    """

    @pytest.mark.parametrize("runtime_env", [None, {}, {"mock_key": "mock_value"}])
    def test_override_noop(self, runtime_env: Optional[Dict[str, Any]]):
        """ Test 1
        No runtime env or working_dir is defined from non-workspace, then do nothing
        If runtime env is None, then it should be autopopulated to an empty dict
        """
        boto_mock = Mock()
        with patch.multiple(os.path, ismount=Mock(return_value=True)), patch.multiple(
            os, makedirs=Mock()
        ), patch("builtins.open", mock_open()), patch.multiple(
            boto3, client=boto_mock
        ), patch.multiple(
            smart_open, open=Mock()
        ):

            modified_runtime_env = override_runtime_env_config(
                runtime_env=runtime_env,
                anyscale_api_client=Mock(),
                api_client=Mock(),
                workload_type=Mock(),
                compute_config_id=Mock(),
                log=Mock(),
            )

        if runtime_env is None:
            assert modified_runtime_env == {}
        else:
            assert modified_runtime_env == runtime_env

    @pytest.mark.parametrize(
        "is_workspace", [True, False],
    )
    def test_override_with_remote_working_dir(self, is_workspace: bool):
        """ Test 2
        Working_dir is a remote uri -> Return existing runtime env
        """
        runtime_env = {
            "working_dir": "s3://bk-premerge-first-jawfish-artifacts/e2e_tests/job",
        }
        boto_mock = Mock()
        with patch.multiple(os.path, ismount=Mock(return_value=True)), patch.multiple(
            os, makedirs=Mock()
        ), patch("builtins.open", mock_open()), patch.multiple(
            boto3, client=boto_mock
        ), patch.multiple(
            smart_open, open=Mock()
        ):
            if is_workspace:
                mock_os_environ = {
                    "ANYSCALE_SESSION_ID": "fake_session_id",
                    "ANYSCALE_EXPERIMENTAL_WORKSPACE_ID": "fake_workspace_id",
                }
                with patch.dict(os.environ, mock_os_environ):
                    modified_runtime_env = override_runtime_env_config(
                        runtime_env=runtime_env,
                        anyscale_api_client=Mock(),
                        api_client=Mock(),
                        workload_type=Mock(),
                        compute_config_id=Mock(),
                        log=Mock(),
                    )
            else:
                modified_runtime_env = override_runtime_env_config(
                    runtime_env=runtime_env,
                    anyscale_api_client=Mock(),
                    api_client=Mock(),
                    workload_type=Mock(),
                    compute_config_id=Mock(),
                    log=Mock(),
                )

        assert modified_runtime_env == runtime_env

    @pytest.mark.parametrize(
        "working_dir", [".", "./subdir/subdir2", "/root_dir/subdir1"],
    )
    @pytest.mark.parametrize(
        "is_workspace", [True, False],
    )
    def test_override_rewrite_working_dir(
        self, working_dir: Optional[str], is_workspace: bool
    ):
        """ Test 3
        Working_dir is a local path and upload path is defined
        1. Upload working_dir
        2. Rewrite working_dir to remote uri
        """
        runtime_env = {
            "working_dir": working_dir,
            "upload_path": "s3://bk-premerge-first-jawfish-artifacts/e2e_tests/job",
        }
        boto_mock = Mock()

        rewritten_runtime_env = {
            "working_dir": "s3://bk-premerge-first-jawfish-artifacts/e2e_tests/job"
        }
        mock_upload_and_rewrite_working_dir = Mock(return_value=rewritten_runtime_env)
        with patch.multiple(
            "anyscale.utils.runtime_env",
            upload_and_rewrite_working_dir=mock_upload_and_rewrite_working_dir,
        ), patch.multiple(os.path, ismount=Mock(return_value=True)), patch.multiple(
            os, makedirs=Mock()
        ), patch(
            "builtins.open", mock_open()
        ), patch.multiple(
            boto3, client=boto_mock
        ), patch.multiple(
            smart_open, open=Mock()
        ):
            if is_workspace:
                mock_os_environ = {
                    "ANYSCALE_SESSION_ID": "fake_session_id",
                    "ANYSCALE_EXPERIMENTAL_WORKSPACE_ID": "fake_workspace_id",
                }
                with patch.dict(os.environ, mock_os_environ):
                    modified_runtime_env = override_runtime_env_config(
                        runtime_env=runtime_env,
                        anyscale_api_client=Mock(),
                        api_client=Mock(),
                        workload_type=Mock(),
                        compute_config_id=Mock(),
                        log=Mock(),
                    )
            else:
                modified_runtime_env = override_runtime_env_config(
                    runtime_env=runtime_env,
                    anyscale_api_client=Mock(),
                    api_client=Mock(),
                    workload_type=Mock(),
                    compute_config_id=Mock(),
                    log=Mock(),
                )

            assert modified_runtime_env == rewritten_runtime_env

    @pytest.mark.parametrize(
        "runtime_env", [None, {}, {"working_dir": "job-services-cuj-examples"}]
    )
    def test_runtime_env_override_with_workspace(
        self, runtime_env: Optional[Dict[str, Any]]
    ):
        """ Test 4
        Override runtime env from workspace
        1. Autopopulate the working_dir to local dir if missing
        2. Infer the upload path
        3. Upload working_dir
        4. Rewrite working_dir to remote uri
        """
        workspace_id = "mock_workspace_id"
        cloud_id = "test_cloud_id"
        rewritten_runtime_env = {
            "working_dir": "s3://bucket",
        }
        mock_log = Mock()
        mock_infer_upload_path_and_rewrite_working_dir = Mock(
            return_value=rewritten_runtime_env
        )
        mock_api_client = Mock()

        mock_api_client.get_decorated_cluster_api_v2_decorated_sessions_cluster_id_get = Mock(
            return_value=Mock(result=Mock(cloud=Mock(id=cloud_id,)))
        )
        with patch.multiple(os.path, ismount=Mock(return_value=True)), patch.dict(
            os.environ,
            {
                "ANYSCALE_EXPERIMENTAL_WORKSPACE_ID": workspace_id,
                "ANYSCALE_SESSION_ID": "mock_session_id",
            },
            clear=True,
        ), patch.multiple(os, makedirs=Mock()), patch(
            "urllib.request", urlretrieve=Mock()
        ), patch(
            "builtins.open", mock_open()
        ), patch.multiple(
            "anyscale.utils.runtime_env",
            infer_upload_path_and_rewrite_working_dir=mock_infer_upload_path_and_rewrite_working_dir,
        ):
            modified_runtime_env = override_runtime_env_config(
                runtime_env=runtime_env,
                anyscale_api_client=Mock(),
                api_client=mock_api_client,
                workload_type=Workload.JOBS,
                compute_config_id=Mock(),
                log=mock_log,
            )

            runtime_env = autopopulate_runtime_env_for_workspace(
                runtime_env=runtime_env, log=Mock()
            )

            mock_infer_upload_path_and_rewrite_working_dir.assert_called_once_with(
                api_client=mock_api_client,
                existing_runtime_env=runtime_env,
                workload_type=Workload.JOBS,
                cloud_id=cloud_id,
                log=mock_log,
                workspace_id=workspace_id,
            )

            assert modified_runtime_env == rewritten_runtime_env

    def test_runtime_env_override_no_workspace(self):
        """ Test 5
        Override runtime env from non-workspace
        1. Infer the upload path
        2. Upload working_dir
        2. Rewrite working_dir to remote uri
        """
        runtime_env = {"working_dir": "job-services-cuj-examples"}
        cloud_id = "test_cloud_id"
        rewritten_runtime_env = {
            "working_dir": "s3://bucket",
        }
        mock_log = Mock()
        mock_infer_upload_path_and_rewrite_working_dir = Mock(
            return_value=rewritten_runtime_env
        )
        mock_anyscale_api_client = Mock()
        mock_api_client = Mock()

        mock_anyscale_api_client.get_compute_template = Mock(
            return_value=Mock(result=Mock(config=Mock(cloud_id=cloud_id,)))
        )
        with patch.multiple(os.path, ismount=Mock(return_value=True)), patch.multiple(
            os, makedirs=Mock()
        ), patch("urllib.request", urlretrieve=Mock()), patch(
            "builtins.open", mock_open()
        ), patch.multiple(
            "anyscale.utils.runtime_env",
            infer_upload_path_and_rewrite_working_dir=mock_infer_upload_path_and_rewrite_working_dir,
        ):
            modified_runtime_env = override_runtime_env_config(
                runtime_env=runtime_env,
                anyscale_api_client=mock_anyscale_api_client,
                api_client=mock_api_client,
                workload_type=Workload.JOBS,
                compute_config_id=Mock(),
                log=mock_log,
            )

            assert modified_runtime_env == rewritten_runtime_env
            mock_infer_upload_path_and_rewrite_working_dir.assert_called_once_with(
                api_client=mock_api_client,
                existing_runtime_env=runtime_env,
                workload_type=Workload.JOBS,
                cloud_id=cloud_id,
                log=mock_log,
            )


@pytest.mark.parametrize(
    (
        "runtime_env",
        "is_workspace",
        "requirements_file_contents",
        "expected_runtime_env",
    ),
    [
        # If not in a workspace, the fields should not be modified.
        [None, False, None, None],
        [{}, False, None, {}],
        [
            {"working_dir": "s3://something.zip", "pip": ["test"]},
            False,
            None,
            {"working_dir": "s3://something.zip", "pip": ["test"]},
        ],
        # If no working_dir is passed, it should default to ".".
        [None, True, None, {"working_dir": "."}],
        [{}, True, None, {"working_dir": "."}],
        # If a working_dir is passed, it should not be altered.
        [
            {"working_dir": "local-path-from-user"},
            True,
            None,
            {"working_dir": "local-path-from-user"},
        ],
        [
            {"working_dir": "s3://remote-path-from-user.zip"},
            True,
            None,
            {"working_dir": "s3://remote-path-from-user.zip"},
        ],
        # If no pip or conda field is specified, the requirements file should be picked up.
        # Also check that the file is read and stripped of comments & whitespace.
        [
            {},
            True,
            "test-pkg1\n test-pkg2==0.1.2\n \n#comment\n ",
            {"working_dir": ".", "pip": ["test-pkg1", "test-pkg2==0.1.2"]},
        ],
        [
            {},
            True,
            "test-pkg1\n test-pkg2==0.1.2#comment\n ",
            {"working_dir": ".", "pip": ["test-pkg1", "test-pkg2==0.1.2"]},
        ],
        [
            {},
            True,
            "test-pkg1\n test-pkg2==0.1.2 #comment\n ",
            {"working_dir": ".", "pip": ["test-pkg1", "test-pkg2==0.1.2"]},
        ],
        # If the requirements file is empty (after stripping), the field shouldn't be set.
        [{}, True, "", {"working_dir": "."},],
        [{}, True, "\n#comment\n ", {"working_dir": "."},],
        # If the pip or conda field is specified, it should not be altered.
        [
            {"pip": ["some-other-pkg"]},
            True,
            "test-pkg1\ntest-pkg2\n",
            {"working_dir": ".", "pip": ["some-other-pkg"]},
        ],
        [
            {"conda": ["some-other-pkg"]},
            True,
            "test-pkg1\ntest-pkg2\n",
            {"working_dir": ".", "conda": ["some-other-pkg"]},
        ],
    ],
)
def test_autopopulate_runtime_env_for_workspace(
    runtime_env: Optional[Dict[str, Any]],
    is_workspace: bool,
    requirements_file_contents: Optional[str],
    expected_runtime_env: Optional[Dict[str, Any]],
):
    """Test that working_dir and pip fields are populated properly for workspaces."""
    mock_logger = Mock()
    mock_os_environ = (
        {
            "ANYSCALE_SESSION_ID": "fake_session_id",
            "ANYSCALE_EXPERIMENTAL_WORKSPACE_ID": "fake_workspace_id",
            "ANYSCALE_WORKSPACE_DYNAMIC_DEPENDENCY_TRACKING": "1",
        }
        if is_workspace
        else {}
    )

    requirements_file_path = None
    if requirements_file_contents is not None:
        f = NamedTemporaryFile("w")
        f.write(requirements_file_contents)
        f.flush()
        requirements_file_path = f.name
    else:
        requirements_file_path = "/some/nonexistent/path"

    with patch.dict(os.environ, mock_os_environ):
        modified_runtime_env = autopopulate_runtime_env_for_workspace(
            runtime_env, mock_logger, requirements_file_path=requirements_file_path,
        )

    assert modified_runtime_env == expected_runtime_env


@pytest.mark.parametrize(
    "workload_type", [Workload.JOBS, Workload.SERVICES, Workload.SCHEDULED_JOBS],
)
@pytest.mark.parametrize(
    "is_workspace", [True, False],
)
@pytest.mark.parametrize(
    "working_dir", [".", "./subdir/subdir2", "/root_dir/subdir1"],
)
@pytest.mark.parametrize(
    "protocol", ["s3", "gs"],
)
def test_infer_upload_path_and_rewrite_working_dir(
    workload_type: Workload, is_workspace: bool, working_dir: str, protocol: str
):
    """This test checks that the upload remote path follows the expected pattern.
    Works for all workloads

    Test every combination
    working_dir [True, False]
    is_workspace [True, False]
    worktype: [jobs, services, scheduled_jobs]
    """
    workspace_id = "test_workspace_id"

    cloud_id = "test_cloud_id"
    org_id = "test_org_id"
    remote_bucket_name = "test_remote_bucket_name"

    # mock api calls utilized for collecting information required to construct the remote path
    mock_api_client = Mock()
    mock_get_decorated_cluster_api_v2_decorated_sessions_cluster_id_get = Mock(
        return_value=DecoratedsessionResponse(result=Mock(cloud=Mock(id=cloud_id)))
    )
    if protocol == "s3":
        mock_api_client.get_cloud_with_cloud_resource_api_v2_clouds_with_cloud_resource_router_cloud_id_get = Mock(
            return_value=Mock(
                result=Mock(
                    provider=CloudProviders.AWS,
                    cloud_resource=Mock(aws_s3_id=remote_bucket_name),
                )
            )
        )
    elif protocol == "gs":
        mock_api_client.get_cloud_with_cloud_resource_api_v2_clouds_with_cloud_resource_router_cloud_id_get = Mock(
            return_value=Mock(result=Mock(provider=CloudProviders.GCP, id=cloud_id,))
        )
        mock_api_client.get_cloud_with_cloud_resource_api_v2_clouds_with_cloud_resource_gcp_router_cloud_id_get = Mock(
            return_value=Mock(
                result=Mock(
                    cloud_resource=Mock(gcp_cloud_storage_bucket_id=remote_bucket_name),
                )
            )
        )
    mock_get_user_info_api_v2_userinfo_get = Mock(
        return_value=Mock(result=Mock(organizations=[Mock(id=org_id)]))
    )
    mock_api_client.get_decorated_cluster_api_v2_decorated_sessions_cluster_id_get = (
        mock_get_decorated_cluster_api_v2_decorated_sessions_cluster_id_get
    )
    mock_api_client.get_user_info_api_v2_userinfo_get = (
        mock_get_user_info_api_v2_userinfo_get
    )

    rewritten_runtime_env = {
        "pip": ["requests"],
        "working_dir": f"{protocol}://bucket",
    }
    mock_upload_and_rewrite_working_dir = Mock(return_value=rewritten_runtime_env)
    with patch.multiple(
        "anyscale.utils.runtime_env",
        upload_and_rewrite_working_dir=mock_upload_and_rewrite_working_dir,
    ), patch.multiple(os.path, ismount=Mock(return_value=True)), patch.dict(
        os.environ, {"ANYSCALE_EXPERIMENTAL_WORKSPACE_ID": workspace_id}, clear=True,
    ):

        workspace_id_arg = None
        if is_workspace:
            workspace_id_arg = workspace_id

        infer_upload_path_and_rewrite_working_dir(
            api_client=mock_api_client,
            existing_runtime_env={"working_dir": working_dir},
            cloud_id=cloud_id,
            workspace_id=workspace_id_arg,
            workload_type=workload_type,
            log=Mock(),
        )
    if is_workspace:
        expected_bucket_prefix = f"{protocol}://{remote_bucket_name}/{org_id}/{cloud_id}/workspace_snapshots/{workspace_id}/{workload_type}"
    else:
        expected_bucket_prefix = (
            f"{protocol}://{remote_bucket_name}/{org_id}/{cloud_id}/{workload_type}"
        )
    call_args = mock_upload_and_rewrite_working_dir.call_args
    runtime_env_arg = call_args[0][0]
    assert runtime_env_arg["working_dir"] == working_dir
    assert runtime_env_arg["upload_path"].startswith(expected_bucket_prefix)


@pytest.mark.parametrize(
    ("aws_s3_id", "expected_bucket_name"),
    [
        (None, None),
        (
            "anyscale-production-data-cld-9xr5r1b2g6egh9bwgdi66whsjv",
            "anyscale-production-data-cld-9xr5r1b2g6egh9bwgdi66whsjv",
        ),
        (
            "arn:aws:s3:::anyscale-test-data-cld-n5rtny1bj8pv6gsmb7m5a4l2",
            "anyscale-test-data-cld-n5rtny1bj8pv6gsmb7m5a4l2",
        ),
    ],
)
def test_get_s3_bucket_aws(
    aws_s3_id: Optional[str], expected_bucket_name: Optional[str]
):
    cloud = Mock(provider=CloudProviders.AWS, cloud_resource=Mock(aws_s3_id=aws_s3_id))

    assert _get_cloud_s3_bucket_from_cloud(cloud) == expected_bucket_name


@pytest.mark.parametrize(
    ("gcp_cloud_storage_bucket_id", "expected_bucket_name"),
    [
        (None, None),
        (
            "anyscale-production-data-cld-9xr5r1b2g6egh9bwgdi66whsjv",
            "anyscale-production-data-cld-9xr5r1b2g6egh9bwgdi66whsjv",
        ),
    ],
)
def test_get_gs_bucket_gcp(
    gcp_cloud_storage_bucket_id: Optional[str], expected_bucket_name: Optional[str]
):
    mock_api_client = Mock()
    mock_api_client.get_cloud_with_cloud_resource_api_v2_clouds_with_cloud_resource_gcp_router_cloud_id_get = Mock(
        return_value=Mock(
            result=Mock(
                cloud_resource=Mock(
                    gcp_cloud_storage_bucket_id=gcp_cloud_storage_bucket_id
                ),
            )
        )
    )

    cloud = Mock(id="test_cloud_id", provider=CloudProviders.GCP,)

    assert (
        _get_cloud_gs_bucket_from_cloud(mock_api_client, cloud) == expected_bucket_name
    )


@pytest.mark.parametrize(
    ("raw", "expected", "error_in_logs"),
    [
        (b"", {}, False),
        (b"\xff=abc\x00a=b", {"a": "b"}, False),  # invalid utf-8 should be ignored
        (b"a=b\x00b=c", {"a": "b", "b": "c"}, False),
        (b"a=b\x00b='c\nd'", {"a": "b", "b": "'c\nd'"}, False),
        (b"a=b\x00b=c=d", {"a": "b", "b": "c=d"}, False),
        (b"a=b\x00b=c=d\x00a\x00k=d\n", {"a": "b", "b": "c=d", "k": "d"}, True),
        (b"  a=b\x00b=c=d   \x00a\x00k=d   \n", {"a": "b", "b": "c=d", "k": "d"}, True),
    ],
)
def test_parse_dot_env_file(raw, expected, error_in_logs, caplog):
    assert parse_dot_env_file(raw) == expected
    if not error_in_logs:
        assert "Invalid env var entry:" not in caplog.text
