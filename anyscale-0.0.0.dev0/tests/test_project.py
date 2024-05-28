import os
from unittest.mock import ANY, Mock, mock_open, patch

import click
import pytest

from anyscale.client.openapi_client.models.project import Project
from anyscale.client.openapi_client.models.project_response import ProjectResponse
from anyscale.client.openapi_client.models.session import Session
from anyscale.client.openapi_client.models.session_list_response import (
    SessionListResponse,
)
from anyscale.project import (
    create_new_proj_def,
    get_and_validate_project_id,
    get_default_project,
    get_parent_cloud_id_and_name_of_project,
    get_proj_id_from_name,
    get_proj_name_from_id,
    get_project_session,
    get_project_sessions,
    infer_project_id,
    ProjectDefinition,
    register_or_attach_to_project,
)
from anyscale.util import PROJECT_NAME_ENV_VAR


def test_get_project_sessions(session_test_data: Session) -> None:
    mock_api_client = Mock()
    mock_api_client.list_sessions_api_v2_sessions_get.return_value = SessionListResponse(
        results=[session_test_data]
    )

    sessions = get_project_sessions(session_test_data.project_id, None, mock_api_client)

    assert sessions == [session_test_data]
    mock_api_client.list_sessions_api_v2_sessions_get.assert_called_once_with(
        project_id=session_test_data.project_id,
        name=None,
        state_filter=["AwaitingFileMounts", "Running"],
        _request_timeout=ANY,
    )

    sessions = get_project_sessions(
        session_test_data.project_id, None, mock_api_client, all_active_states=True
    )

    assert sessions == [session_test_data]
    mock_api_client.list_sessions_api_v2_sessions_get.assert_called_with(
        project_id=session_test_data.project_id,
        name=None,
        active_only=True,
        _request_timeout=ANY,
    )


def test_get_project_session(session_test_data: Session) -> None:
    mock_api_client = Mock()
    mock_api_client.list_sessions_api_v2_sessions_get.return_value = SessionListResponse(
        results=[session_test_data]
    )

    session = get_project_session(session_test_data.project_id, None, mock_api_client)

    assert session == session_test_data
    mock_api_client.list_sessions_api_v2_sessions_get.assert_called_once_with(
        project_id=session_test_data.project_id,
        name=None,
        state_filter=["AwaitingFileMounts", "Running"],
        _request_timeout=ANY,
    )


def test_get_proj_name_from_id(project_test_data: Project) -> None:
    mock_api_client = Mock()
    mock_api_client.get_project_api_v2_projects_project_id_get.return_value = ProjectResponse(
        result=project_test_data
    )
    project_name = get_proj_name_from_id(project_test_data.id, mock_api_client)

    assert project_name == project_test_data.name
    mock_api_client.get_project_api_v2_projects_project_id_get.assert_called_once_with(
        project_id=project_test_data.id, _request_timeout=ANY,
    )


@pytest.mark.parametrize("owner", [None, "owner"])
def test_get_proj_id_from_name(project_test_data: Project, owner: str) -> None:
    mock_api_client = Mock()
    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.return_value.results = [
        project_test_data
    ]
    project_id = get_proj_id_from_name(project_test_data.name, mock_api_client)

    assert project_id == project_test_data.id
    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.assert_called_once_with(
        name=project_test_data.name, _request_timeout=ANY, owner=None
    )


def test_create_new_proj_def(project_test_data: Project) -> None:
    mock_api_client = Mock()

    project_name, project_definition = create_new_proj_def(
        project_test_data.name, api_client=mock_api_client,
    )

    assert project_name == project_test_data.name
    assert os.path.normpath(project_definition.root) == os.getcwd()


def test_register_project(project_test_data: Project) -> None:
    mock_api_client = Mock()
    # Mock no existing project
    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.return_value.results = (
        []
    )
    mock_api_client.create_project_api_v2_projects_post.return_value.result.id = (
        project_test_data.id
    )

    project_definition = ProjectDefinition(os.getcwd())
    project_definition.config["name"] = project_test_data.name

    with patch("builtins.open", new_callable=mock_open()), patch(
        "yaml.dump"
    ) as mock_dump:
        register_or_attach_to_project(project_definition, mock_api_client)

        mock_dump.assert_called_once_with({"project_id": project_test_data.id}, ANY)

    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.assert_called_once_with(
        project_test_data.name
    )
    mock_api_client.create_project_api_v2_projects_post.assert_called_once_with(
        write_project={
            "name": project_test_data.name,
            "description": "",
            "initial_cluster_config": None,
        }
    )


def test_register_or_attach_to_project_attach_to_existing(
    project_test_data: Project,
) -> None:
    mock_api_client = Mock()
    # Mock project already exists
    mock_project = Mock()
    mock_project.id = "prj_10"
    mock_project.name = project_test_data.name
    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.return_value.results = [
        mock_project
    ]
    mock_api_client.create_project_api_v2_projects_post.return_value.result.id = (
        project_test_data.id
    )
    project_definition = ProjectDefinition(os.getcwd())
    project_definition.config["name"] = project_test_data.name

    with patch("builtins.open", new_callable=mock_open()), patch(
        "yaml.dump"
    ) as mock_dump:
        register_or_attach_to_project(project_definition, mock_api_client)

        mock_dump.assert_called_once_with({"project_id": "prj_10"}, ANY)

    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.assert_called_once_with(
        project_test_data.name
    )
    mock_api_client.create_project_api_v2_projects_post.assert_not_called()


def test_get_and_validate_project_id():

    # Test passing in project id
    with patch.multiple(
        "anyscale.project", validate_project_id=Mock(),
    ):
        assert (
            get_and_validate_project_id(
                project_id="mock_project_id1",
                project_name=None,
                parent_cloud_id=None,
                api_client=Mock(),
                anyscale_api_client=Mock(),
            )
            == "mock_project_id1"
        )

    # Test passing in project name
    mock_get_proj_id_from_name = Mock(return_value="mock_project_id1")
    with patch.multiple(
        "anyscale.project",
        validate_project_id=Mock(),
        get_proj_id_from_name=mock_get_proj_id_from_name,
    ):
        assert (
            get_and_validate_project_id(
                project_id=None,
                project_name="mock_project_name1",
                parent_cloud_id=None,
                api_client=Mock(),
                anyscale_api_client=Mock(),
            )
            == "mock_project_id1"
        ), "mock_cluster_name1"

    # Test using default project without cloud isolation
    anyscale_api_client = Mock()
    api_client = Mock()
    mock_get_default_project = Mock(return_value=Mock(id="mock_project_id2"))
    with patch.multiple(
        "anyscale.project",
        load_project_or_throw=Mock(side_effect=click.ClickException("")),
        get_default_project=mock_get_default_project,
    ):
        assert (
            get_and_validate_project_id(
                project_id=None,
                project_name=None,
                parent_cloud_id=None,
                api_client=api_client,
                anyscale_api_client=anyscale_api_client,
            )
            == "mock_project_id2"
        )
    mock_get_default_project.assert_called_once_with(
        api_client, anyscale_api_client, parent_cloud_id=None
    )

    # Test getting project_name from env var
    mock_get_proj_id_from_name = Mock(return_value="mock_project_id3")
    api_client = Mock()
    with patch.multiple(
        "anyscale.project",
        validate_project_id=Mock(),
        get_proj_id_from_name=mock_get_proj_id_from_name,
    ), patch.dict(os.environ, {PROJECT_NAME_ENV_VAR: "project_from_env"}):
        assert (
            get_and_validate_project_id(
                project_id=None,
                project_name=None,
                parent_cloud_id=None,
                api_client=api_client,
                anyscale_api_client=Mock(),
            )
            == "mock_project_id3"
        )
        mock_get_proj_id_from_name.assert_called_once_with(
            "project_from_env", api_client
        )

    # Test using default project with cloud isolation
    anyscale_api_client = Mock()
    api_client = Mock()
    mock_get_default_project = Mock(return_value=Mock(id="mock_project_id4"))
    api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get = Mock(
        return_value=Mock(result=Mock(is_on=True))
    )
    with patch.multiple(
        "anyscale.project",
        load_project_or_throw=Mock(side_effect=click.ClickException("")),
        get_default_project=mock_get_default_project,
    ):
        assert (
            get_and_validate_project_id(
                project_id=None,
                project_name=None,
                parent_cloud_id="mock_parent_cloud_id",
                api_client=api_client,
                anyscale_api_client=anyscale_api_client,
            )
            == "mock_project_id4"
        )
    mock_get_default_project.assert_called_once_with(
        api_client, anyscale_api_client, parent_cloud_id="mock_parent_cloud_id"
    )


@pytest.mark.parametrize("cloud_isolation_phase_1_feature_flag", [True, False])
def test_get_default_project(cloud_isolation_phase_1_feature_flag: bool):
    anyscale_api_client = Mock()
    api_client = Mock()
    anyscale_api_client.get_default_project = Mock(
        return_value=Mock(result=Mock(id="mock_project_id1"))
    )
    api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get = Mock(
        return_value=Mock(result=Mock(is_on=cloud_isolation_phase_1_feature_flag))
    )
    parent_cloud_id = (
        "mock_parent_cloud_id1" if cloud_isolation_phase_1_feature_flag else None
    )
    assert (
        get_default_project(
            api_client, anyscale_api_client, parent_cloud_id=parent_cloud_id
        ).id
        == "mock_project_id1"
    )

    expected_get_default_project_call_args = (
        {"parent_cloud_id": parent_cloud_id} if parent_cloud_id else {}
    )
    anyscale_api_client.get_default_project.assert_called_once_with(
        **expected_get_default_project_call_args
    )


def test_infer_project_id():
    # Test passing compute config
    anyscale_api_client = Mock()
    api_client = Mock()
    mock_get_default_project = Mock(return_value=Mock(id="mock_project_id1"))
    mock_get_selected_cloud_id_or_default = Mock(return_value="mock_cloud_id1")
    with patch.multiple(
        "anyscale.project",
        get_default_project=mock_get_default_project,
        find_project_root=Mock(return_value=None),
        get_selected_cloud_id_or_default=mock_get_selected_cloud_id_or_default,
    ):
        assert (
            infer_project_id(
                anyscale_api_client,
                api_client,
                Mock(),
                project_id=None,
                cluster_compute_id="mock_cluster_compute_id",
            )
            == "mock_project_id1"
        )
    mock_get_default_project.assert_called_once_with(
        api_client, anyscale_api_client, parent_cloud_id="mock_cloud_id1"
    )
    mock_get_selected_cloud_id_or_default.assert_called_once_with(
        api_client,
        anyscale_api_client,
        cluster_compute_id="mock_cluster_compute_id",
        cluster_compute_config=None,
        cloud_id=None,
        cloud_name=None,
    )

    # Test passing compute config name
    anyscale_api_client = Mock()
    api_client = Mock()
    mock_cluster_compute = Mock(id="mock_cluster_compute_id")
    mock_get_default_project = Mock(return_value=Mock(id="mock_project_id1"))
    mock_get_selected_cloud_id_or_default = Mock(return_value="mock_cloud_id1")
    mock_get_cluster_compute_from_name = Mock(return_value=mock_cluster_compute)
    with patch.multiple(
        "anyscale.project",
        get_default_project=mock_get_default_project,
        find_project_root=Mock(return_value=None),
        get_selected_cloud_id_or_default=mock_get_selected_cloud_id_or_default,
        get_cluster_compute_from_name=mock_get_cluster_compute_from_name,
    ):
        assert (
            infer_project_id(
                anyscale_api_client,
                api_client,
                Mock(),
                project_id=None,
                cluster_compute="mock_cluster_compute_name",
            )
            == "mock_project_id1"
        )
    mock_get_default_project.assert_called_once_with(
        api_client, anyscale_api_client, parent_cloud_id="mock_cloud_id1"
    )
    mock_get_selected_cloud_id_or_default.assert_called_once_with(
        api_client,
        anyscale_api_client,
        cluster_compute_id="mock_cluster_compute_id",
        cluster_compute_config=None,
        cloud_id=None,
        cloud_name=None,
    )

    # Test passing in cloud
    mock_get_default_project = Mock(return_value=Mock(id="mock_project_id2"))
    mock_get_selected_cloud_id_or_default = Mock(return_value="mock_cloud_id2")
    with patch.multiple(
        "anyscale.project",
        get_default_project=mock_get_default_project,
        find_project_root=Mock(return_value=None),
        get_selected_cloud_id_or_default=mock_get_selected_cloud_id_or_default,
    ):
        assert (
            infer_project_id(
                anyscale_api_client,
                api_client,
                Mock(),
                project_id=None,
                cloud="mock_cloud_name",
            )
            == "mock_project_id2"
        )
    mock_get_default_project.assert_called_once_with(
        api_client, anyscale_api_client, parent_cloud_id="mock_cloud_id2"
    )
    mock_get_selected_cloud_id_or_default.assert_called_once_with(
        api_client,
        anyscale_api_client,
        cluster_compute_id=None,
        cluster_compute_config=None,
        cloud_id=None,
        cloud_name="mock_cloud_name",
    )


@pytest.mark.parametrize("project_exists", [True, False])
@pytest.mark.parametrize("cloud_isolation_phase_1_feature_flag", [True, False])
def test_get_parent_cloud_id_and_name_of_project(
    project_exists: bool, cloud_isolation_phase_1_feature_flag: bool
):
    api_client = Mock()
    api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get = Mock(
        return_value=Mock(result=Mock(is_on=cloud_isolation_phase_1_feature_flag))
    )

    parent_cloud_id = (
        "mock_parent_cloud_id" if cloud_isolation_phase_1_feature_flag else None
    )
    mock_project = Mock(parent_cloud_id=parent_cloud_id) if project_exists else None
    api_client.get_project_api_v2_projects_project_id_get = Mock(
        return_value=Mock(result=mock_project)
    )

    mock_cloud = Mock(id="mock_parent_cloud_id")
    mock_cloud.name = "mock_parent_cloud_name"
    api_client.get_cloud_api_v2_clouds_cloud_id_get = Mock(
        return_value=Mock(result=mock_cloud)
    )

    if project_exists and cloud_isolation_phase_1_feature_flag:
        assert get_parent_cloud_id_and_name_of_project(
            "mock_project_id", api_client
        ) == ("mock_parent_cloud_id", "mock_parent_cloud_name")
    else:
        assert (
            get_parent_cloud_id_and_name_of_project("mock_project_id", api_client)
            is None
        )

    api_client.get_project_api_v2_projects_project_id_get.assert_called_once_with(
        project_id="mock_project_id"
    )
    if project_exists and cloud_isolation_phase_1_feature_flag:
        api_client.get_cloud_api_v2_clouds_cloud_id_get.assert_called_once_with(
            cloud_id="mock_parent_cloud_id"
        )
