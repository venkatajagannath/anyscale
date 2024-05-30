from typing import Generator
from unittest.mock import Mock, patch

from click.testing import CliRunner
import pytest

from anyscale.commands.workspace_commands import create


class MockWorkspaceController(Mock):
    pass


@pytest.fixture()
def mock_workspace_controller() -> Generator[MockWorkspaceController, None, None]:
    mock_workspace_controller = MockWorkspaceController()
    mock_workspace_controller_cls = Mock(return_value=mock_workspace_controller,)

    with patch(
        "anyscale.commands.workspace_commands.WorkspaceController",
        new=mock_workspace_controller_cls,
    ):
        yield mock_workspace_controller


@pytest.fixture()
def mock_workspace_sdk() -> Generator[MockWorkspaceController, None, None]:
    mock_workspace_controller = MockWorkspaceController()
    mock_workspace_controller_cls = Mock(return_value=mock_workspace_controller,)

    with patch(
        "anyscale.commands.workspace_commands.WorkspaceController",
        new=mock_workspace_controller_cls,
    ):
        yield mock_workspace_controller


def test_create(mock_workspace_controller: MockWorkspaceController):
    """Tests the logic for creating new workspace
    """
    runner = CliRunner()

    # test required options
    runner.invoke(
        create,
        args=[
            "--name",
            "fake-workspace-name",
            "--cloud-id",
            "fake-cloud-id",
            "--compute-config-id",
            "fake-compute-config-id",
            "--cluster-env-build-id",
            "fake-cluster-environment-build-id",
        ],
    )
    mock_workspace_controller.create.assert_called_once_with(
        name="fake-workspace-name",
        cloud_id="fake-cloud-id",
        compute_config_id="fake-compute-config-id",
        project_id=None,
        cluster_environment_build_id="fake-cluster-environment-build-id",
    )
    mock_workspace_controller.reset_mock()

    # test project_id option
    runner.invoke(
        create,
        args=[
            "--name",
            "fake-workspace-name",
            "--cloud-id",
            "fake-cloud-id",
            "--compute-config-id",
            "fake-compute-config-id",
            "--cluster-env-build-id",
            "fake-cluster-environment-build-id",
            "--project-id",
            "fake-project-id",
        ],
    )
    mock_workspace_controller.create.assert_called_once_with(
        name="fake-workspace-name",
        cloud_id="fake-cloud-id",
        compute_config_id="fake-compute-config-id",
        project_id="fake-project-id",
        cluster_environment_build_id="fake-cluster-environment-build-id",
    )
    mock_workspace_controller.reset_mock()

    # test mutual exclusive arguments (--docker and --cluster-env-build-id)
    result = runner.invoke(
        create,
        args=[
            "--name",
            "fake-workspace-name",
            "--cloud-id",
            "fake-cloud-id",
            "--compute-config-id",
            "fake-compute-config-id",
            "--project-id",
            "fake-project-id",
            "--cluster-env-build-id",
            "fake-cluster-environment-build-id",
            "--docker",
            "fake-docker",
        ],
    )
    assert result.exception is not None

    # test mutual exclusive arguments (--docker and --python-version)
    result = runner.invoke(
        create,
        args=[
            "--name",
            "fake-workspace-name",
            "--cloud-id",
            "fake-cloud-id",
            "--compute-config-id",
            "fake-compute-config-id",
            "--project-id",
            "fake-project-id",
            "--python-version",
            "fake-python-version",
            "--docker",
            "fake-docker",
        ],
    )
    assert result.exception is not None

    # test mutual exclusive arguments (--docker and --ray-version)
    result = runner.invoke(
        create,
        args=[
            "--name",
            "fake-workspace-name",
            "--cloud-id",
            "fake-cloud-id",
            "--compute-config-id",
            "fake-compute-config-id",
            "--project-id",
            "fake-project-id",
            "--ray-version",
            "fake-ray-version",
            "--docker",
            "fake-docker",
        ],
    )
    assert result.exception is not None

    # test at least one of --docker or --cluster-env-build-id is required
    result = runner.invoke(
        create,
        args=[
            "--name",
            "fake-workspace-name",
            "--cloud-id",
            "fake-cloud-id",
            "--compute-config-id",
            "fake-compute-config-id",
        ],
    )
    assert result.exception is not None
