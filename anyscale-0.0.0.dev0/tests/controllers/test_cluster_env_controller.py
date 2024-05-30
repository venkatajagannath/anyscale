from contextlib import nullcontext
from datetime import datetime
import tempfile
from typing import Any, Callable, Optional
from unittest.mock import Mock, patch

import click
from click import ClickException
import pytest
import yaml

from anyscale.cluster_env import get_build_from_cluster_env_identifier
from anyscale.controllers.cluster_env_controller import ClusterEnvController
from anyscale.sdk.anyscale_client import (
    CreateBYODClusterEnvironment,
    CreateClusterEnvironment,
)
from anyscale.utils.ray_version_utils import get_correct_name_for_base_image_name


def get_imported_function_name(func: Callable[..., Any]) -> str:
    return ".".join([ClusterEnvController.__module__, func.__name__])


@pytest.mark.parametrize("cluster_env_name", ["mock_cluster_env_name", None])
@pytest.mark.parametrize("build_id", ["build_id_from_cli", None])
def test_get(
    mock_auth_api_client, cluster_env_name: Optional[str], build_id: Optional[str]
) -> None:
    cluster_env_controller = ClusterEnvController()
    example_cluster_env_config = '{ "foo": "bar" }'
    cluster_env_controller.api_client.get_build_api_v2_builds_build_id_get = Mock(
        return_value=Mock(result=Mock(config_json=example_cluster_env_config))
    )
    mock_build_id_from_cluster_env = "build_id_from_cluster_env"
    possible_error_if_both_or_neither_arg_provided = (
        pytest.raises(ClickException)
        if bool(cluster_env_name) == bool(build_id)
        else nullcontext()
    )
    with patch(
        get_imported_function_name(get_build_from_cluster_env_identifier),
        new=Mock(return_value=Mock(id=mock_build_id_from_cluster_env)),
    ) as mock_get_build_from_cluster_env_identifier, possible_error_if_both_or_neither_arg_provided as e:
        cluster_env_controller.get(cluster_env_name, build_id)
    if not e:
        if cluster_env_name:
            mock_get_build_from_cluster_env_identifier.assert_called_with(
                cluster_env_name, cluster_env_controller.anyscale_api_client
            )
            mock_build_id = mock_build_id_from_cluster_env
        else:
            mock_get_build_from_cluster_env_identifier.assert_not_called()
            mock_build_id = build_id  # type: ignore
        cluster_env_controller.api_client.get_build_api_v2_builds_build_id_get.assert_called_once_with(
            mock_build_id
        )
    else:
        assert "Please only provide one of" in e.value.message
        mock_get_build_from_cluster_env_identifier.assert_not_called()
        cluster_env_controller.api_client.get_build_api_v2_builds_build_id_get.assert_not_called()


@pytest.mark.parametrize("cluster_env_name", ["mock_cluster_env_name", None])
@pytest.mark.parametrize("cluster_env_id", ["mock_cluster_env_id", None])
def test_archive(
    mock_auth_api_client, cluster_env_name: Optional[str], cluster_env_id: Optional[str]
) -> None:
    cluster_env_controller = ClusterEnvController()
    cluster_env_controller.anyscale_api_client.get_cluster_environment = Mock(
        return_value=Mock(result=Mock(name="mock_cluster_env_name"))
    )
    mock_get_cluster_env_from_name = Mock(return_value=Mock(id="mock_cluster_env_id"))
    should_throw_error = bool(cluster_env_name) == bool(cluster_env_id)

    if should_throw_error:
        with pytest.raises(click.ClickException) as e:
            cluster_env_controller.archive(cluster_env_name, cluster_env_id)

        assert "Please only provide one of" in e.value.message

        cluster_env_controller.api_client.archive_cluster_environment_api_v2_application_templates_application_template_id_archive_post.assert_not_called()
    else:
        with patch.multiple(
            "anyscale.controllers.cluster_env_controller",
            get_cluster_env_from_name=mock_get_cluster_env_from_name,
        ):
            cluster_env_controller.archive(cluster_env_name, cluster_env_id)

        if cluster_env_id:
            cluster_env_controller.anyscale_api_client.get_cluster_environment.assert_called_with(
                cluster_env_id
            )
        else:
            mock_get_cluster_env_from_name.assert_called_with(
                cluster_env_name, cluster_env_controller.anyscale_api_client
            )

        cluster_env_controller.api_client.archive_cluster_environment_api_v2_application_templates_application_template_id_archive_post.assert_called_with(
            "mock_cluster_env_id"
        )


def test_list_builds(mock_auth_api_client,):
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock",
        _validate_api_client_auth=Mock(),
        _validate_credentials_format=Mock(),
    ):
        cluster_env_controller = ClusterEnvController()
    mock_list_builds = Mock(
        return_value=[
            Mock(
                id="mock_build1",
                revision="mock_revision",
                status="mock_status",
                last_modified_at=datetime.now(),
            )
        ]
    )
    cluster_env_controller.anyscale_api_client.get_cluster_environment = Mock(
        return_value=Mock(result=Mock(name="mock_cluster_env_name"))
    )
    mock_get_cluster_env_from_name = Mock(return_value=Mock(id="mock_cluster_env_id"))

    with patch.multiple(
        "anyscale.controllers.cluster_env_controller",
        list_builds=mock_list_builds,
        get_cluster_env_from_name=mock_get_cluster_env_from_name,
    ):
        cluster_env_controller._list_builds("mock_cluster_env_name", None, max_items=20)
        mock_get_cluster_env_from_name.assert_called_with(
            "mock_cluster_env_name", cluster_env_controller.anyscale_api_client
        )
        mock_list_builds.assert_called_with(
            "mock_cluster_env_id",
            cluster_env_controller.anyscale_api_client,
            max_items=20,
        )

        cluster_env_controller._list_builds(None, "mock_cluster_env_id", max_items=20)
        mock_list_builds.assert_called_with(
            "mock_cluster_env_id",
            cluster_env_controller.anyscale_api_client,
            max_items=20,
        )
        cluster_env_controller.anyscale_api_client.get_cluster_environment.assert_called_with(
            "mock_cluster_env_id"
        )


@pytest.mark.parametrize("include_shared", [True, False])
def test_list_cluster_envs(
    mock_auth_api_client, include_shared: bool,
):
    cluster_env_controller = ClusterEnvController()
    mock_cluster_env = Mock()
    mock_cluster_env.name = "mock_cluster_env_name"
    cluster_env_controller.anyscale_api_client.search_cluster_environments = Mock(
        return_value=Mock(
            results=[mock_cluster_env], metadata=Mock(next_paging_token=None)
        )
    )
    cluster_env_controller.api_client.get_user_info_api_v2_userinfo_get = Mock(
        return_value=Mock(result=Mock(id="mock_user_id"))
    )
    mock_get_build_from_cluster_env_identifier = Mock(
        return_value=Mock(id="mock_build_id")
    )
    cluster_env_controller.anyscale_api_client.get_cluster_environment_build = Mock(
        return_value=Mock(result=Mock(last_modified_at=datetime.now()))
    )

    with patch.multiple(
        "anyscale.controllers.cluster_env_controller",
        get_build_from_cluster_env_identifier=mock_get_build_from_cluster_env_identifier,
    ):
        cluster_env_controller._list_cluster_envs(include_shared, max_items=20)
        if not include_shared:
            cluster_env_controller.anyscale_api_client.search_cluster_environments.assert_called_with(
                {"creator_id": "mock_user_id", "paging": {"count": 20}}
            )
        else:
            cluster_env_controller.anyscale_api_client.search_cluster_environments.assert_called_with(
                {"creator_id": None, "paging": {"count": 20}}
            )
        mock_get_build_from_cluster_env_identifier.assert_called_with(
            "mock_cluster_env_name", cluster_env_controller.anyscale_api_client
        )


def test_disambiguate_byod_builds(mock_auth_api_client):
    # Test that CLI can disambiguate which type of build to create based on
    # the contents of cluster-env yaml
    build_cluster_environment_mock = Mock()
    mock_anyscale_sdk = Mock(build_cluster_environment=build_cluster_environment_mock)
    cluster_env_controller = ClusterEnvController(
        anyscale_sdk=mock_anyscale_sdk, initialize_auth_api_client=False,
    )
    byod_config = {"docker_image": "a.b.c/d:efg", "ray_version": "nightly"}
    expected_byod_create_build = CreateBYODClusterEnvironment(
        name="byod", config_json=byod_config,
    )

    non_byod_config = {"env_vars": {}}
    expected_non_byod_create_build = CreateClusterEnvironment(
        name="non-byod", config_json=non_byod_config,
    )

    with tempfile.NamedTemporaryFile("wt") as f:
        yaml.dump(byod_config, f)
        f.flush()
        cluster_env_controller.build("byod", f.name)
        build_cluster_environment_mock.assert_called_with(
            expected_byod_create_build, log_output=True
        )

    with tempfile.NamedTemporaryFile("wt") as f:
        yaml.dump(non_byod_config, f)
        f.flush()
        cluster_env_controller.build("non-byod", f.name)
        build_cluster_environment_mock.assert_called_with(
            expected_non_byod_create_build, log_output=True
        )


@pytest.mark.parametrize(
    ("base_image_name", "expected_result"),
    [
        ("anyscale/ray:2.8.0-py38-cuda121", "anyscale/ray:2.8.0-py38-cuda121"),
        ("anyscale/ray:2.7.1oss-py38-cuda121", "anyscale/ray:2.7.1oss-py38-cuda121"),
        (
            "anyscale/ray:2.7.1optimized-py38-cuda121",
            "anyscale/ray:2.7.1optimized-py38-cuda121",
        ),
        ("anyscale/ray:2.7.1-py38-cuda121", "anyscale/ray:2.7.1optimized-py38-cuda121"),
        ("anyscale/ray:2.7.0-py38-cuda121", "anyscale/ray:2.7.0optimized-py38-cuda121"),
        ("anyscale/ray:2.6.0-py38", "anyscale/ray:2.6.0-py38"),
        ("anyscale/ray:2.6.0", "anyscale/ray:2.6.0"),
        ("anyscale/ray:2.1.1rc1", "anyscale/ray:2.1.1rc1"),
        ("anyscale/ray:2.0.1rc-py38-cuda121", "anyscale/ray:2.0.1rc-py38-cuda121"),
    ],
)
def test_get_correct_name_for_base_image_name(base_image_name, expected_result):
    result = get_correct_name_for_base_image_name(base_image_name)
    assert result == expected_result
