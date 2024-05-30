import subprocess
from unittest.mock import MagicMock, Mock, patch

import click
import pytest

from anyscale.client.openapi_client.models.create_experimental_workspace import (
    CreateExperimentalWorkspace,
)
from anyscale.controllers.workspace_controller import WorkspaceController


@pytest.mark.parametrize("project_id", [None, "fake-project-id"])
@pytest.mark.parametrize(
    "compute_config_cloud_id", ["fake-cloud-id", "fake-another-cloud-id"]
)
@patch(
    "anyscale.controllers.workspace_controller.get_default_project",
    Mock(return_value=Mock(id="fake-default-project-id")),
)
def test_create_workspace(
    mock_auth_api_client, project_id, compute_config_cloud_id
) -> None:

    workspace_controller = WorkspaceController()
    mock_create_workspace_api_v2_experimental_workspaces_post = Mock()
    workspace_controller.api_client.create_workspace_api_v2_experimental_workspaces_post = (
        mock_create_workspace_api_v2_experimental_workspaces_post
    )
    mock_get_compute_template_api_v2_compute_templates_template_id_get = Mock(
        return_value=Mock(result=Mock(config=Mock(cloud_id=compute_config_cloud_id)))
    )
    workspace_controller.api_client.get_compute_template_api_v2_compute_templates_template_id_get = (
        mock_get_compute_template_api_v2_compute_templates_template_id_get
    )

    if compute_config_cloud_id != "fake-cloud-id":
        with pytest.raises(click.ClickException):
            workspace_controller.create(
                name="fake-workspace-name",
                cloud_id="fake-cloud-id",
                compute_config_id="fake-compute-config-id",
                cluster_environment_build_id="fake-cluster-environment-build-id",
                project_id=project_id,
            )
            mock_create_workspace_api_v2_experimental_workspaces_post.assert_not_called()
    else:
        workspace_controller.create(
            name="fake-workspace-name",
            cloud_id="fake-cloud-id",
            compute_config_id="fake-compute-config-id",
            cluster_environment_build_id="fake-cluster-environment-build-id",
            project_id=project_id,
        )
        expected_project_id = (
            "fake-project-id" if project_id else "fake-default-project-id"
        )

        mock_create_workspace_api_v2_experimental_workspaces_post.assert_called_once_with(
            CreateExperimentalWorkspace(
                name="fake-workspace-name",
                cloud_id="fake-cloud-id",
                compute_config_id="fake-compute-config-id",
                cluster_environment_build_id="fake-cluster-environment-build-id",
                project_id=expected_project_id,
            )
        )


@pytest.mark.parametrize("delete_existing_files_in_destination", [True, False])
def test_run_rsync(mock_auth_api_client, delete_existing_files_in_destination: bool):
    # Mock subprocess.run to prevent actual execution of the rsync command
    with patch.object(subprocess, "run") as mocked_run, patch.object(
        WorkspaceController, "_get_workspace_command_context"
    ) as mock_get_workspace_command_context:
        mock_get_workspace_command_context.return_value = MagicMock(
            ssh=MagicMock(key_path="mock_key_path", user="mock_user"),
            head_ip="mock_head_ip",
            working_dir="mock_working_dir",
        )
        workspace_controller = WorkspaceController()

        # Set up the expected rsync command
        expected_rsync_command = [
            "rsync",
            "--rsh",
            'ssh -i mock_key_path -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o IdentitiesOnly=yes -o "ProxyCommand=ssh -W %h:%p -i mock_key_path -o StrictHostKeyChecking=accept-new mock_user@mock_head_ip" -p 5020',
            "-rvzl",
            "--delete",
            "--exclude",
            "exclude_pattern1",
            "--exclude",
            "exclude_pattern2",
            "--filter",
            "dir-merge,- filter_pattern1",
            "--filter",
            "dir-merge,- filter_pattern2",
            "ray@0.0.0.0:mock_remote_path",
            "mock_local_path",
        ]

        if not delete_existing_files_in_destination:
            expected_rsync_command.remove("--delete")

        # Call the run_rsync method with mock parameters
        workspace_controller.run_rsync(
            local_path="mock_local_path",
            remote_path="mock_remote_path",
            down=True,
            rsync_filters=["filter_pattern1", "filter_pattern2"],
            rsync_excludes=["exclude_pattern1", "exclude_pattern2"],
            delete_existing_files_in_destination=delete_existing_files_in_destination,
        )

        # Check if subprocess.run was called with the expected rsync command
        mocked_run.assert_called_once_with(expected_rsync_command, check=False)
