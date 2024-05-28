from unittest.mock import call, Mock, patch

import click
import pytest

from anyscale.cluster_env import (
    get_build_from_cluster_env_identifier,
    get_cluster_env_from_name,
    get_default_cluster_env_build,
    list_builds,
    validate_successful_build,
)


def test_get_build_id_from_cluster_env_identifier():
    mock_anyscale_api_client = Mock()

    mock_get_cluster_env_from_name = Mock()
    mock_list_builds = Mock(return_value=[Mock(revision=3, id="mock_build_id")])
    with patch.multiple(
        "anyscale.cluster_env",
        get_cluster_env_from_name=mock_get_cluster_env_from_name,
        list_builds=mock_list_builds,
    ):
        assert (
            get_build_from_cluster_env_identifier(
                "my_cluster_env:3", mock_anyscale_api_client
            ).id
            == "mock_build_id"
        )

    mock_list_builds = Mock(
        return_value=[
            Mock(revision=3, id="mock_build_id3"),
            Mock(revision=1, id="mock_build_id1"),
        ]
    )
    with patch.multiple(
        "anyscale.cluster_env",
        get_cluster_env_from_name=mock_get_cluster_env_from_name,
        list_builds=mock_list_builds,
    ):
        assert (
            get_build_from_cluster_env_identifier(
                "my_cluster_env", mock_anyscale_api_client
            ).id
            == "mock_build_id3"
        )

    mock_list_builds = Mock(return_value=[])
    with patch.multiple(
        "anyscale.cluster_env",
        get_cluster_env_from_name=mock_get_cluster_env_from_name,
        list_builds=mock_list_builds,
    ), pytest.raises(click.ClickException):
        get_build_from_cluster_env_identifier(
            "my_cluster_env:3", mock_anyscale_api_client
        )

    mock_list_builds = Mock(return_value=[])
    with patch.multiple(
        "anyscale.cluster_env",
        get_cluster_env_from_name=mock_get_cluster_env_from_name,
        list_builds=mock_list_builds,
    ), pytest.raises(click.ClickException):
        get_build_from_cluster_env_identifier(
            "my_cluster_env", mock_anyscale_api_client
        )


def test_get_cluster_env_id_from_name():
    mock_anyscale_api_client = Mock()

    mock_cluster_env = Mock(id="my_cluster_env_id")
    mock_cluster_env.name = "my_cluster_env"
    mock_anyscale_api_client.search_cluster_environments = Mock(
        return_value=Mock(results=[mock_cluster_env])
    )
    assert (
        get_cluster_env_from_name("my_cluster_env", mock_anyscale_api_client).id
        == "my_cluster_env_id"
    )
    mock_anyscale_api_client.search_cluster_environments.assert_called_once_with(
        {"name": {"equals": "my_cluster_env"}, "paging": {"count": 1}}
    )

    mock_anyscale_api_client.search_cluster_environments.return_value = Mock(results=[])
    with pytest.raises(click.ClickException):
        assert get_cluster_env_from_name("my_cluster_env", mock_anyscale_api_client)


def test_list_builds_with_pagination():
    mock_anyscale_api_client = Mock()

    first_page = []
    for i in range(50):
        first_page.append(f"result_{i}")

    second_page = []
    for i in range(10):
        second_page.append(f"result_{50 + i}")

    def list_builds_mock(cluster_env_id, count, paging_token):
        if paging_token is None:
            return Mock(
                results=first_page, metadata=Mock(next_paging_token="next_page")
            )
        if paging_token == "next_page":
            return Mock(results=second_page, metadata=Mock(next_paging_token=None))

    mock_anyscale_api_client.list_cluster_environment_builds = Mock(
        side_effect=list_builds_mock,
    )
    assert (
        list_builds("my_cluster_env_id", mock_anyscale_api_client)
        == first_page + second_page
    )
    mock_anyscale_api_client.list_cluster_environment_builds.assert_has_calls(
        [
            call("my_cluster_env_id", count=50, paging_token=None),
            call("my_cluster_env_id", count=50, paging_token="next_page"),
        ]
    )


def test_validate_successful_build():
    # Check the function return without error for successful build
    mock_anyscale_api_client = Mock()
    mock_anyscale_api_client.get_cluster_environment_build = Mock(
        return_value=Mock(result=Mock(status="succeeded"))
    )
    validate_successful_build("mock_build_id", mock_anyscale_api_client)
    mock_anyscale_api_client.get_cluster_environment_build.assert_called_once_with(
        "mock_build_id"
    )

    # Check the function raises an error for non-successful builds
    mock_anyscale_api_client.get_cluster_environment_build = Mock(
        return_value=Mock(
            result=Mock(status="failed", cluster_environment_id="mock_cluster_env_id")
        )
    )
    with pytest.raises(click.ClickException):
        validate_successful_build("mock_build_id", mock_anyscale_api_client)
    mock_anyscale_api_client.get_cluster_environment_build.assert_called_once_with(
        "mock_build_id"
    )
    mock_anyscale_api_client.get_cluster_environment.assert_called_once_with(
        "mock_cluster_env_id"
    )


def test_get_default_cluster_env_build():
    mock_api_client = Mock()
    mock_build = Mock()
    mock_build.id = "mock_build_id"
    mock_api_client.get_default_cluster_env_build_api_v2_builds_default_py_version_ray_version_get = Mock(
        return_value=Mock(result=mock_build)
    )
    mock_anyscale_api_client = Mock()
    mock_anyscale_api_client.get_cluster_environment_build = Mock(
        return_value=Mock(result=mock_build)
    )
    mock_get_ray_and_py_version_for_default_cluster_env = Mock(
        return_value=("mock_ray_version", "mock_py_verison")
    )

    with patch.multiple(
        "anyscale.cluster_env",
        get_ray_and_py_version_for_default_cluster_env=mock_get_ray_and_py_version_for_default_cluster_env,
    ):
        assert (
            get_default_cluster_env_build(mock_api_client, mock_anyscale_api_client)
            == mock_build
        )
    mock_get_ray_and_py_version_for_default_cluster_env.assert_called_once_with()
    mock_api_client.get_default_cluster_env_build_api_v2_builds_default_py_version_ray_version_get.assert_called_once_with(
        "pymock_py_verison", "mock_ray_version"
    )
    mock_anyscale_api_client.get_cluster_environment_build.assert_called_once_with(
        "mock_build_id"
    )
