import os
from typing import Optional
from unittest.mock import ANY, Mock, mock_open as mock_open_factory, patch

import click
import pytest

from anyscale.connect_utils.project import ProjectBlock
from anyscale.sdk.anyscale_client import ArchiveStatus
from anyscale.sdk.anyscale_client.models.compute_template_query import (
    ComputeTemplateQuery,
)


@pytest.fixture()
def mock_project_block():
    with patch.multiple(
        "anyscale.connect_utils.project.ProjectBlock", __init__=Mock(return_value=None)
    ):
        project_block = ProjectBlock()
        project_block.anyscale_api_client = Mock()
        project_block.api_client = Mock()
        project_block.log = Mock()
        project_block.block_label = ""
        return project_block


@pytest.mark.parametrize("parent_cloud_id", ["mock_parent_cloud_id", None])
@pytest.mark.parametrize("cloud_isolation_ff_on", [True, False])
def test_get_default_project(
    mock_project_block, parent_cloud_id: Optional[str], cloud_isolation_ff_on: bool
):
    mock_project = Mock(id="project_id")
    mock_project.name = "project_name"
    mock_project_block.anyscale_api_client.get_default_project = Mock(
        return_value=Mock(result=mock_project)
    )
    mock_project_block.api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get = Mock(
        return_value=Mock(result=Mock(is_on=cloud_isolation_ff_on))
    )

    assert mock_project_block._get_default_project(parent_cloud_id) == (
        mock_project.id,
        mock_project.name,
    )
    mock_project_block.anyscale_api_client.get_default_project.assert_called_once_with(
        parent_cloud_id=parent_cloud_id
    )


@pytest.mark.parametrize("cloud_isolation_ff_on", [True, False])
@pytest.mark.parametrize("cloud_name", [None, "mock_cloud_name"])
@pytest.mark.parametrize("cluster_compute_name", [None, "mock_cluster_compute_name"])
def test_get_parent_cloud_id(
    mock_project_block,
    cloud_isolation_ff_on: bool,
    cloud_name: str,
    cluster_compute_name: str,
):
    mock_get_cloud_id_and_name = Mock(return_value=("mock_parent_cloud_id", ANY))
    mock_project_block.api_client.search_compute_templates_api_v2_compute_templates_search_post = Mock(
        return_value=Mock(
            results=[
                Mock(config=Mock(cloud_id="mock_parent_cloud_id"), archived_at=None)
            ]
        )
    )
    mock_get_organization_default_cloud = Mock(return_value=None)
    mock_get_last_used_cloud = Mock(return_value="mock_parent_cloud_name")

    with patch.multiple(
        "anyscale.connect_utils.project",
        get_cloud_id_and_name=mock_get_cloud_id_and_name,
        get_organization_default_cloud=mock_get_organization_default_cloud,
        get_last_used_cloud=mock_get_last_used_cloud,
    ):
        assert (
            mock_project_block._get_parent_cloud_id(
                cloud_name, cluster_compute_name, None
            )
            == "mock_parent_cloud_id"
        )
    if cloud_name:
        mock_get_cloud_id_and_name.assert_called_once_with(
            api_client=mock_project_block.api_client,
            cloud_id=None,
            cloud_name=cloud_name,
        )
    elif cluster_compute_name:
        mock_project_block.api_client.search_compute_templates_api_v2_compute_templates_search_post.assert_called_once_with(
            ComputeTemplateQuery(
                orgwide=True,
                name={"equals": cluster_compute_name},
                include_anonymous=True,
                archive_status=ArchiveStatus.ALL,
            )
        )
    else:
        mock_get_organization_default_cloud.assert_called_once_with(
            mock_project_block.api_client
        )
        mock_get_last_used_cloud.assert_called_once_with(
            None, mock_project_block.anyscale_api_client
        )
        mock_get_cloud_id_and_name.assert_called_once_with(
            mock_project_block.api_client,
            cloud_id=None,
            cloud_name="mock_parent_cloud_name",
        )


def test_ensure_project_setup_at_dir_config_exists(mock_project_block):
    # Case where .anyscale.yaml exists and is correctly set up
    with patch.multiple("os.path", exists=Mock(return_value=True)), patch.multiple(
        "anyscale.project", get_project_id=Mock(return_value="project_id")
    ), patch("builtins.open", mock_open_factory()):
        mock_project = Mock(id="project_id")
        mock_project.name = "project_name"
        mock_project_block.anyscale_api_client.get_project = Mock(
            return_value=Mock(result=mock_project)
        )
        assert mock_project_block._ensure_project_setup_at_dir(
            "mock_project_dir", None
        ) == ("project_id", "project_name")

    # Case where .anyscale.yaml exists but has invalid project id
    with patch.multiple("os.path", exists=Mock(return_value=True)), patch.multiple(
        "anyscale.project", get_project_id=Mock(return_value="project_id")
    ), patch("builtins.open", mock_open_factory()):
        mock_project = Mock(id="project_id")
        mock_project.name = "project_name"
        mock_project_block.anyscale_api_client.get_project = Mock(
            side_effect=click.ClickException("")
        )
        with pytest.raises(click.ClickException):
            assert mock_project_block._ensure_project_setup_at_dir(
                "mock_project_dir", None
            )
        mock_project_block.anyscale_api_client.get_project.assert_called_once_with(
            "project_id"
        )

    # Case where .anyscale.yaml exists but doesn't have project_id in the file
    with patch.multiple("os.path", exists=Mock(return_value=True)), patch.multiple(
        "anyscale.project", get_project_id=Mock(return_value=None),
    ), patch("builtins.open", mock_open_factory()), pytest.raises(click.ClickException):
        assert mock_project_block._ensure_project_setup_at_dir("mock_project_dir", None)


@pytest.mark.parametrize("project_id", [None, "project_id"])
@pytest.mark.parametrize("parent_cloud_id", [None, "mock_parent_cloud_id"])
@pytest.mark.parametrize("cloud_isolation_ff_on", [True, False])
def test_ensure_project_setup_at_dir_no_config(
    mock_project_block,
    project_id: Optional[str],
    parent_cloud_id: Optional[str],
    cloud_isolation_ff_on: bool,
):
    # Case where .anyscale.yaml doesn't exist

    mock_project_block.anyscale_api_client.search_projects = Mock(
        return_value=Mock(results=[Mock(id=project_id)])
    )
    mock_project_block.anyscale_api_client.create_project = Mock(
        return_value=Mock(result=Mock(id="project_id"))
    )
    mock_project_block.api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get = Mock(
        return_value=Mock(result=Mock(is_on=cloud_isolation_ff_on))
    )
    mock_yaml_dump = Mock()
    with patch.multiple("os.path", exists=Mock(return_value=False)), patch(
        "builtins.open", mock_open_factory()
    ) as mock_open, patch.multiple("yaml", dump=mock_yaml_dump):
        mock_project_block._ensure_project_setup_at_dir(
            "mock_project_dir", "project_name", parent_cloud_id
        )
    if not project_id:
        mock_project_block.anyscale_api_client.create_project.assert_called_once_with(
            {
                "name": "project_name",
                "description": "Automatically created by Anyscale Connect",
                "parent_cloud_id": parent_cloud_id,
            }
        )
    mock_open.assert_called_once_with("mock_project_dir/.anyscale.yaml", "w+")
    mock_yaml_dump.assert_called_once_with({"project_id": "project_id"})


@pytest.mark.parametrize("project_exists", [True, False])
@pytest.mark.parametrize("parent_cloud_id", [None, "mock_parent_cloud_id"])
@pytest.mark.parametrize("cloud_isolation_ff_on", [True, False])
def test_create_or_get_project_from_name(
    mock_project_block,
    project_exists: bool,
    parent_cloud_id: Optional[str],
    cloud_isolation_ff_on: bool,
):
    mock_find_project_id = Mock(
        return_value="test_project_id" if project_exists else None
    )
    mock_project_block.anyscale_api_client.create_project = Mock(
        return_value=Mock(result=Mock(id="test_project_id"))
    )
    mock_project_block.api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get = Mock(
        return_value=Mock(result=Mock(is_on=cloud_isolation_ff_on))
    )

    with patch.multiple(
        "anyscale.connect_utils.project", find_project_id=mock_find_project_id
    ):
        assert mock_project_block._create_or_get_project_from_name(
            "test_project_name", parent_cloud_id
        ) == ("test_project_id", "test_project_name")

    if not project_exists:
        mock_project_block.anyscale_api_client.create_project.assert_called_once_with(
            {
                "name": "test_project_name",
                "description": "Automatically created by Anyscale Connect",
                "parent_cloud_id": parent_cloud_id,
            }
        )
    else:
        mock_project_block.anyscale_api_client.create_project.assert_not_called()


@pytest.mark.parametrize("project_dir", [None, "test_project_dir"])
@pytest.mark.parametrize("project_name", [None, "test_project_name"])
@pytest.mark.parametrize("cloud_name", [None, "test_cloud_name"])
@pytest.mark.parametrize("compute_template_name", [None, "test_compute_template_name"])
@pytest.mark.parametrize("project_exists_in_dir_tree", [True, False])
def test_init(
    project_dir: Optional[str],
    project_exists_in_dir_tree: bool,
    project_name: Optional[str],
    cloud_name: Optional[str],
    compute_template_name: Optional[str],
):
    mock_get_default_project = Mock(
        return_value=("test_default_project_id", "test_default_project_name")
    )
    mock_ensure_project_setup_at_dir = Mock(
        return_value=("test_project_id", "test_project_name")
    )
    mock_find_project_root = Mock(
        return_value="test_project_dir" if project_exists_in_dir_tree else None
    )
    mock_create_or_get_project_from_name = Mock(
        return_value=("test_project_id", "test_project_name")
    )
    mock_get_parent_cloud_id = Mock(return_value="mock_parent_cloud_id")
    with patch.multiple(
        "anyscale.connect_utils.project.ProjectBlock",
        _get_default_project=mock_get_default_project,
        _ensure_project_setup_at_dir=mock_ensure_project_setup_at_dir,
        _create_or_get_project_from_name=mock_create_or_get_project_from_name,
        _get_parent_cloud_id=mock_get_parent_cloud_id,
    ), patch.multiple(
        "anyscale.connect_utils.project", get_auth_api_client=Mock(return_value=Mock())
    ), patch.multiple(
        "anyscale.project", find_project_root=mock_find_project_root
    ):
        project_block = ProjectBlock(
            project_dir=project_dir,
            project_name=project_name,
            cloud_name=cloud_name,
            cluster_compute_name=compute_template_name,
        )
        if project_dir:
            # Project dir passed in
            assert project_block.project_dir == os.path.abspath(
                os.path.expanduser(project_dir)
            )
            assert project_block.project_name == "test_project_name"
            assert project_block.project_id == "test_project_id"
            mock_ensure_project_setup_at_dir.assert_called_once_with(
                os.path.abspath(os.path.expanduser(project_dir)),
                project_name,
                "mock_parent_cloud_id",
            )
        elif project_exists_in_dir_tree and not project_name:
            # Find project dir in local directory structure
            assert project_block.project_dir == "test_project_dir"
            assert project_block.project_name == "test_project_name"
            assert project_block.project_id == "test_project_id"
            mock_ensure_project_setup_at_dir.assert_called_once_with(
                "test_project_dir", project_name, "mock_parent_cloud_id"
            )
        elif project_name:
            assert project_block.project_dir is None
            assert project_block.project_name == "test_project_name"
            assert project_block.project_id == "test_project_id"
            mock_create_or_get_project_from_name.assert_called_once_with(
                "test_project_name", "mock_parent_cloud_id"
            )
        else:
            # Use default project
            assert project_block.project_dir is None
            assert project_block.project_name == "test_default_project_name"
            assert project_block.project_id == "test_default_project_id"
            mock_get_default_project.assert_called_once_with("mock_parent_cloud_id")
