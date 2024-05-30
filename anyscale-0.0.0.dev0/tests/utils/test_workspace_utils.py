import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from anyscale.client.openapi_client.models import (
    SessionSshKey,
    SessionsshkeyResponse,
)
from anyscale.controllers.workspace_controller import WorkspaceController
from anyscale.feature_flags import FLAG_DEFAULT_WORKING_DIR_FOR_PROJ
from anyscale.utils.workspace_utils import _get_ssh_key_info


def test_configure_ssh_key(base_mock_api_client: Mock) -> None:
    base_mock_api_client.get_session_ssh_key_api_v2_sessions_session_id_ssh_key_get = Mock(
        return_value=SessionsshkeyResponse(
            result=SessionSshKey(key_name="SSH_KEY", private_key="PRIVATE_KEY")
        )
    )
    with tempfile.TemporaryDirectory() as directory:
        _get_ssh_key_info("session_id", base_mock_api_client, directory)
        with open(os.path.join(directory, "SSH_KEY.pem")) as f:
            assert f.read() == "PRIVATE_KEY"


@pytest.mark.parametrize("default_working_dir_for_proj_flag", [True, False])
def test_get_workspace_dir_name(
    mock_auth_api_client, default_working_dir_for_proj_flag: bool
):
    workspace_controller = WorkspaceController()
    workspace_controller.api_client = Mock()

    mock_workspace = Mock(project_id="mock_project_id")
    mock_project = Mock(directory_name="default")
    mock_project.name = "default_cld_1"
    workspace_controller.api_client.get_workspace_api_v2_experimental_workspaces_workspace_id_get = Mock(
        return_value=Mock(result=mock_workspace)
    )
    workspace_controller.api_client.get_project_api_v2_projects_project_id_get = Mock(
        return_value=Mock(result=mock_project)
    )
    workspace_controller.api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get = Mock(
        return_value=Mock(result=Mock(is_on=default_working_dir_for_proj_flag))
    )

    with patch.multiple(
        "anyscale.controllers.workspace_controller",
        load_workspace_id_or_throw=Mock(return_value="mock_workspace_id"),
    ):
        directory_name = workspace_controller.get_workspace_dir_name()

    assert (
        directory_name == "default"
        if default_working_dir_for_proj_flag
        else "default_cld_1"
    )

    workspace_controller.api_client.get_workspace_api_v2_experimental_workspaces_workspace_id_get.assert_called_once_with(
        "mock_workspace_id"
    )
    workspace_controller.api_client.get_project_api_v2_projects_project_id_get.assert_called_once_with(
        "mock_project_id"
    )
    workspace_controller.api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get.assert_called_once_with(
        FLAG_DEFAULT_WORKING_DIR_FOR_PROJ
    )
