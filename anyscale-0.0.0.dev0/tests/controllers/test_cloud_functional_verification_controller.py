from typing import Iterator, List, Optional
from unittest.mock import MagicMock, Mock, patch

from click import ClickException
import pytest

from anyscale.client.openapi_client.models import (
    ApplyProductionServiceV2Model,
    CloudProviders,
    ServiceConfig,
)
from anyscale.controllers.cloud_functional_verification_controller import (
    CloudFunctionalVerificationController,
    CloudFunctionalVerificationType,
    SERVICE_VERIFICATION_TIMEOUT_MINUTES,
)
from anyscale.sdk.anyscale_client.models import ComputeTemplateQuery


@pytest.fixture(autouse=True)
def mock_auth_api_client(base_mock_anyscale_api_client: Mock) -> Iterator[None]:
    mock_auth_api_client = Mock(
        api_client=Mock(), anyscale_api_client=base_mock_anyscale_api_client,
    )
    with patch.multiple(
        "anyscale.controllers.base_controller",
        get_auth_api_client=Mock(return_value=mock_auth_api_client),
    ):
        yield


@pytest.mark.parametrize("cloud_provider", [CloudProviders.AWS, CloudProviders.GCP])
@pytest.mark.parametrize(
    ("is_exception_stream_removed", "timeout", "compute_config_exists"),
    [
        pytest.param(None, False, True, id="happy-path-exists"),
        pytest.param(None, False, False, id="happy-path-create"),
        pytest.param(True, False, False, id="stream-removed"),
        pytest.param(False, False, False, id="cannot-create"),
        pytest.param(True, True, False, id="timeout"),
    ],
)
def test_get_or_create_cluster_compute(
    is_exception_stream_removed: Optional[bool],
    timeout: bool,
    compute_config_exists: bool,
    cloud_provider: CloudProviders,
) -> None:
    mock_cloud_id = "mock_cloud_id"
    mock_cluster_compute_id = "mock_cluster_compute_id"
    mock_api_client = Mock()
    mock_api_client.search_compute_templates_api_v2_compute_templates_search_post = Mock(
        return_value=Mock(
            results=[Mock(id=mock_cluster_compute_id)] if compute_config_exists else []
        )
    )
    mock_anyscale_api_client = Mock()
    if is_exception_stream_removed is None:
        mock_anyscale_api_client.create_cluster_compute = Mock(
            return_value=Mock(result=Mock(id=mock_cluster_compute_id))
        )
    elif is_exception_stream_removed is True:
        mock_anyscale_api_client.create_cluster_compute = Mock()
        if timeout:
            mock_anyscale_api_client.create_cluster_compute.side_effect = ClickException(
                "Stream removed"
            )
        else:
            mock_anyscale_api_client.create_cluster_compute.side_effect = [
                ClickException("Stream removed"),
                Mock(result=Mock(id=mock_cluster_compute_id)),
            ]

    elif is_exception_stream_removed is False:
        mock_anyscale_api_client.create_cluster_compute = Mock(
            side_effect=ClickException("mock error")
        )
    with patch(
        "anyscale.controllers.cloud_functional_verification_controller.CREATE_COMPUTE_CONFIG_TIMEOUT_SECONDS",
        1,
    ):
        funciontal_verification_controller = CloudFunctionalVerificationController(
            Mock()
        )

        funciontal_verification_controller = CloudFunctionalVerificationController(
            Mock()
        )
        funciontal_verification_controller.api_client = mock_api_client
        funciontal_verification_controller.anyscale_api_client = (
            mock_anyscale_api_client
        )
        if timeout or (is_exception_stream_removed is False):
            with pytest.raises(ClickException) as e:
                funciontal_verification_controller.get_or_create_cluster_compute(
                    mock_cloud_id, cloud_provider
                )
            if timeout:
                e.match("Timed out")
            else:
                e.match("mock error")
        else:

            assert (
                funciontal_verification_controller.get_or_create_cluster_compute(
                    mock_cloud_id, cloud_provider
                )
                == mock_cluster_compute_id
            )

    mock_api_client.search_compute_templates_api_v2_compute_templates_search_post.assert_called_with(
        ComputeTemplateQuery(
            orgwide=True,
            name={"equals": f"functional_verification_{mock_cloud_id}"},
            include_anonymous=True,
            version=1,
        )
    )

    if compute_config_exists:
        mock_anyscale_api_client.create_cluster_compute.assert_not_called()
    else:
        mock_anyscale_api_client.create_cluster_compute.assert_called()


@pytest.mark.parametrize(
    ("prepare_verification_failed", "create_workspace_failed"),
    [
        pytest.param(False, False, id="happy-path"),
        pytest.param(True, False, id="prepare-verification-failed"),
        pytest.param(False, True, id="create-workspace-failed"),
    ],
)
def test_create_workspace(
    prepare_verification_failed: bool, create_workspace_failed: bool
):
    expected_result = not prepare_verification_failed and not create_workspace_failed
    mock_prepare_verification = Mock(return_value=(Mock(), Mock(), Mock()))
    if prepare_verification_failed:
        mock_prepare_verification.side_effect = ClickException("mock error")
    mock_create_workspace = Mock()
    if create_workspace_failed:
        mock_create_workspace.side_effect = ClickException("mock error")
    with patch.multiple(
        "anyscale.controllers.cloud_functional_verification_controller.CloudFunctionalVerificationController",
        _prepare_verification=mock_prepare_verification,
    ):
        controller = CloudFunctionalVerificationController(Mock())
        controller.api_client.create_workspace_api_v2_experimental_workspaces_post = (
            mock_create_workspace
        )
        if expected_result:
            controller.create_workspace(Mock(), Mock())
        else:
            with pytest.raises(ClickException):
                controller.create_workspace(Mock(), Mock())


@pytest.mark.parametrize(
    (
        "create_workspace_succeed",
        "poll_until_active_succeed",
        "terminate_workspace_succeed",
        "expected_result",
    ),
    [
        pytest.param(True, True, True, True, id="happy-path",),
        pytest.param(False, False, False, False, id="create-workspace-failed",),
        pytest.param(True, False, False, False, id="poll-until-active-failed",),
        pytest.param(True, True, False, False, id="workspace-termination-failed",),
    ],
)
def test_verify_workspace(
    create_workspace_succeed: bool,
    poll_until_active_succeed: bool,
    terminate_workspace_succeed: bool,
    expected_result: bool,
):
    mock_create_task = MagicMock()

    mock_terminate_workspace = (
        Mock()
        if terminate_workspace_succeed
        else Mock(side_effect=ClickException("mock error"))
    )
    with patch.multiple(
        "anyscale.controllers.cloud_functional_verification_controller.CloudFunctionalVerificationController",
        create_workspace=Mock()
        if create_workspace_succeed
        else Mock(side_effect=ClickException("mock error")),
        poll_until_active=Mock()
        if poll_until_active_succeed
        else Mock(side_effect=ClickException("mock error")),
        _create_task=mock_create_task,
    ):
        controller = CloudFunctionalVerificationController(Mock())
        controller.anyscale_api_client.terminate_cluster = mock_terminate_workspace
        assert controller.verify_workspace(Mock(), Mock()) == expected_result
        task_count = 1 + create_workspace_succeed + poll_until_active_succeed
        assert mock_create_task.call_count == task_count


@pytest.mark.parametrize("create_service_succeed", [True, False])
@pytest.mark.parametrize("canary_percent", [None, 100])
def test_rollout_service(create_service_succeed: bool, canary_percent: Optional[int]):
    mock_cluster_compute_id = "mock_cluster_compute_id"
    mock_cluster_env_build_id = "mock_cluster_env_build_id"
    mock_project_id = "mock_project_id"
    mock_service_id = "mock_service_id"
    mock_cloud_id = "mock_cloud_id"
    mock_service_name = "mock_service_name"
    mock_version = "mock_version"
    mock_rollout_service = Mock(return_value=Mock(result=Mock(id=mock_service_id)))
    if not create_service_succeed:
        mock_rollout_service.side_effect = ClickException("mock error")
    with patch.multiple(
        "anyscale.controllers.cloud_functional_verification_controller.CloudFunctionalVerificationController",
        _prepare_verification=MagicMock(
            return_value=(
                mock_cluster_compute_id,
                mock_cluster_env_build_id,
                mock_project_id,
            )
        ),
    ):
        controller = CloudFunctionalVerificationController(Mock())
        controller.api_client.apply_service_api_v2_services_v2_apply_put = (
            mock_rollout_service
        )

        if not create_service_succeed:
            with pytest.raises(ClickException):
                controller.rollout_service(
                    mock_cloud_id,
                    Mock(),
                    version=mock_version,
                    service_name=mock_service_name,
                    canary_percent=canary_percent,
                )
        else:
            assert (
                controller.rollout_service(
                    mock_cloud_id,
                    Mock(),
                    version=mock_version,
                    service_name=mock_service_name,
                    canary_percent=canary_percent,
                ).id
                == mock_service_id
            )

        mock_rollout_service.assert_called_once_with(
            ApplyProductionServiceV2Model(
                name=mock_service_name,
                description=f"service for cloud {mock_cloud_id} functional verification",
                project_id=mock_project_id,
                ray_serve_config={
                    "applications": [
                        {
                            "import_path": "serve_hello:entrypoint",
                            "runtime_env": {
                                "working_dir": "https://github.com/anyscale/docs_examples/archive/refs/heads/main.zip",
                                "env_vars": {
                                    "SERVE_RESPONSE_MESSAGE": f"cloud functional verification {mock_version}",
                                },
                            },
                        }
                    ],
                },
                version=mock_version,
                build_id=mock_cluster_env_build_id,
                compute_config_id=mock_cluster_compute_id,
                config=ServiceConfig(
                    max_uptime_timeout_sec=SERVICE_VERIFICATION_TIMEOUT_MINUTES
                    * 2
                    * 60,
                ),
                canary_percent=canary_percent,
            )
        )


@pytest.mark.parametrize(
    (
        "deploy_service_succeed",
        "poll_until_active_succeed",
        "upgrade_service_succeed",
        "terminate_service_succeed",
    ),
    [
        pytest.param(True, True, True, True, id="happy-path"),
        pytest.param(False, False, False, False, id="deploy-service-failed"),
        pytest.param(True, False, False, False, id="poll-until-active-failed"),
        pytest.param(True, True, False, False, id="upgrade-service-failed"),
        pytest.param(True, True, True, False, id="terminate-service-failed"),
    ],
)
def test_verify_service(
    deploy_service_succeed: bool,
    poll_until_active_succeed: bool,
    upgrade_service_succeed: bool,
    terminate_service_succeed: bool,
):
    expected_result = (
        deploy_service_succeed
        and poll_until_active_succeed
        and upgrade_service_succeed
        and terminate_service_succeed
    )
    expected_task_num = (
        1 + deploy_service_succeed + poll_until_active_succeed + upgrade_service_succeed
    )

    mock_service_id = "mock_service_id"
    mock_service_name = "mock_service_name"

    mock_create_task = MagicMock()
    mock_rollout_service = Mock()
    if deploy_service_succeed and upgrade_service_succeed:
        mock_rollout_service = Mock(
            result=Mock(id=mock_service_id, name=mock_service_name)
        )
    elif deploy_service_succeed and not upgrade_service_succeed:
        mock_rollout_service.side_effect = [
            Mock(result=Mock(id=mock_service_id, name=mock_service_name)),
            ClickException("mock error"),
        ]
    else:
        mock_rollout_service.side_effect = ClickException("mock error")
    mock_terminate_service = Mock()
    if not terminate_service_succeed:
        mock_terminate_service.side_effect = ClickException("mock error")
    mock_poll_until_active = Mock()
    if not poll_until_active_succeed:
        mock_poll_until_active.side_effect = ClickException("mock error")

    with patch.multiple(
        "anyscale.controllers.cloud_functional_verification_controller.CloudFunctionalVerificationController",
        _create_task=mock_create_task,
        rollout_service=mock_rollout_service,
        poll_until_active=mock_poll_until_active,
    ):
        controller = CloudFunctionalVerificationController(Mock())
        controller.api_client.terminate_service_api_v2_services_v2_service_id_terminate_post = (
            mock_terminate_service
        )
        assert controller.verify_service(Mock(), Mock()) == expected_result
        assert mock_create_task.call_count == expected_task_num


@pytest.mark.parametrize(
    ("get_current_status_error", "status_not_allowed", "fail_fast", "expected_result"),
    [
        pytest.param(False, False, False, True, id="happy-path"),
        pytest.param(True, False, False, False, id="get-current-status-error"),
        pytest.param(False, True, False, False, id="status-not-allowed"),
        pytest.param(False, False, True, False, id="fail-fast"),
    ],
)
def test_poll_until_active(
    get_current_status_error, status_not_allowed, fail_fast, expected_result
):
    mock_function_type = Mock()
    mock_function_id = "mock_function_id"
    mock_cluster_id = "mock_cluster_id"
    mock_function = Mock(id=mock_function_id, cluster_id=mock_cluster_id)
    goal_status = "goal_status"
    mock_get_current_status = Mock(
        return_value="not_allowed" if status_not_allowed else goal_status
    )
    if get_current_status_error:
        mock_get_current_status.side_effect = ClickException("mock error")
    mock_render_event_log = Mock(return_value=not fail_fast)
    with patch.multiple(
        "anyscale.controllers.cloud_functional_verification_controller.CloudFunctionalVerificationController",
        _update_task_in_step_progress=Mock(),
        _render_event_log=mock_render_event_log,
    ), patch.multiple(
        "anyscale.controllers.cloud_functional_verification_controller",
        POLL_INTERVAL_SECONDS=0,
    ):
        controller = CloudFunctionalVerificationController(Mock())
        if expected_result:
            assert (
                controller.poll_until_active(
                    mock_function_type,
                    mock_function,
                    mock_get_current_status,
                    goal_status,
                    set(goal_status),
                    Mock(),
                    1,
                )
                == expected_result
            )
            mock_get_current_status.assert_called_once_with(mock_function_id)
        else:
            with pytest.raises(ClickException) as e:
                controller.poll_until_active(
                    mock_function_type,
                    mock_function,
                    mock_get_current_status,
                    goal_status,
                    set(goal_status),
                    Mock(),
                    1,
                )
                if get_current_status_error:
                    assert e.match("Failed to get")
                if status_not_allowed:
                    assert e.match("is in an unexpected state:")
                if fail_fast:
                    assert e.match(
                        "verification failed! Please check the logs and terminate"
                    )


@pytest.mark.parametrize(
    ("no_new_logs", "fail_fast"),
    [
        pytest.param(True, False, id="no-new-logs"),
        pytest.param(False, False, id="new-logs"),
        pytest.param(False, True, id="failed"),
    ],
)
def test_render_event_log_workspace(
    no_new_logs: bool, fail_fast: bool,
):
    controller = CloudFunctionalVerificationController(Mock())
    function = Mock(cluster_id="mock_cluster_id")
    mock_log_num = 10
    mock_new_log_num = 10 if no_new_logs else 14
    controller.event_log_num[CloudFunctionalVerificationType.WORKSPACE] = mock_log_num
    mock_add_row = Mock()
    controller.event_log_tables[CloudFunctionalVerificationType.WORKSPACE] = Mock(
        add_row=mock_add_row
    )
    mock_get_logs = Mock(
        return_value=Mock(
            result=Mock(
                lines="new-logs" if not fail_fast else "Failed to execute",
                num_lines=mock_new_log_num,
            )
        )
    )
    controller.api_client = Mock(
        get_startup_logs_api_v2_sessions_session_id_startup_logs_get=mock_get_logs
    )
    assert controller._render_event_log(
        CloudFunctionalVerificationType.WORKSPACE, function,
    ) == (not fail_fast)
    assert (
        controller.event_log_num[CloudFunctionalVerificationType.WORKSPACE]
        == mock_new_log_num
    )
    if no_new_logs:
        mock_add_row.assert_not_called()
    else:
        mock_add_row.assert_called_once()


@pytest.mark.parametrize("no_new_logs", [True, False])
def test_render_event_log_service(no_new_logs: bool):
    controller = CloudFunctionalVerificationController(Mock())
    controller._format_service_event_log = Mock()  # type: ignore
    function = Mock(id="mock_cluster_id")
    mock_log_num = 10
    mock_new_log_num = 10 if no_new_logs else 14
    controller.event_log_num[CloudFunctionalVerificationType.SERVICE] = mock_log_num
    mock_add_row = Mock()
    controller.event_log_tables[CloudFunctionalVerificationType.SERVICE] = Mock(
        add_row=mock_add_row
    )
    mock_get_logs = Mock(return_value=Mock(results=["log"] * mock_new_log_num))
    controller.api_client = Mock(
        get_service_events_api_v2_services_v2_service_id_events_get=mock_get_logs
    )
    assert (
        controller._render_event_log(CloudFunctionalVerificationType.SERVICE, function)
        is True
    )
    assert (
        controller.event_log_num[CloudFunctionalVerificationType.SERVICE]
        == mock_new_log_num
    )
    assert mock_add_row.call_count == mock_new_log_num - mock_log_num


def test_poll_until_active_timeout():
    mock_function_type = Mock()
    mock_function_id = "mock_function_id"
    mock_cluster_id = "mock_cluster_id"
    mock_function = Mock(id=mock_function_id, cluster_id=mock_cluster_id)
    goal_status = "goal_status"
    mock_status = "mock_status"
    allowed_status_set = {goal_status, mock_status}
    mock_get_current_status = Mock(return_value=mock_status)
    with patch.multiple(
        "anyscale.controllers.cloud_functional_verification_controller.CloudFunctionalVerificationController",
        _update_task_in_step_progress=Mock(),
    ), patch.multiple(
        "anyscale.controllers.cloud_functional_verification_controller",
        POLL_INTERVAL_SECONDS=0,
    ), pytest.raises(
        ClickException
    ) as e:
        controller = CloudFunctionalVerificationController(Mock())
        assert (
            controller.poll_until_active(
                mock_function_type,
                mock_function,
                mock_get_current_status,
                goal_status,
                allowed_status_set,
                Mock(),
                0,
            )
            is False
        )
        assert e.match("Timed out")


@pytest.mark.parametrize("verification_result", [True, False])
@pytest.mark.parametrize("cloud_provider", [CloudProviders.AWS, CloudProviders.GCP])
@pytest.mark.parametrize(
    "functions_to_verify",
    [
        [CloudFunctionalVerificationType.WORKSPACE],
        [
            CloudFunctionalVerificationType.WORKSPACE,
            CloudFunctionalVerificationType.SERVICE,
        ],
    ],
)
def test_start_verification(
    functions_to_verify: List[CloudFunctionalVerificationType],
    cloud_provider: CloudProviders,
    verification_result: bool,
):
    mock_cloud_id = "mock_cloud_id"

    with patch.multiple(
        "anyscale.controllers.cloud_functional_verification_controller.CloudFunctionalVerificationController",
        verify=Mock(return_value=verification_result),
        get_live_console=MagicMock(),
        _prepare_verification=Mock(),
    ):
        funciontal_verification_controller = CloudFunctionalVerificationController(
            Mock()
        )
        assert (
            funciontal_verification_controller.start_verification(
                mock_cloud_id, cloud_provider, functions_to_verify, yes=True
            )
            == verification_result
        )


@pytest.mark.parametrize(
    "functions_to_verify",
    [
        [CloudFunctionalVerificationType.WORKSPACE],
        [
            CloudFunctionalVerificationType.WORKSPACE,
            CloudFunctionalVerificationType.SERVICE,
        ],
    ],
)
def test_get_live_console(functions_to_verify):
    funciontal_verification_controller = CloudFunctionalVerificationController(Mock())
    funciontal_verification_controller.get_live_console(functions_to_verify)
    for function in functions_to_verify:
        assert funciontal_verification_controller.step_progress[function] is not None
        assert funciontal_verification_controller.overall_progress[function] is not None
        assert funciontal_verification_controller.task_ids[function] is not None


@pytest.mark.parametrize(
    ("no_cluster_env", "no_default_cluster_env"),
    [
        pytest.param(True, True, id="no-cluster-env"),
        pytest.param(False, True, id="no-default-cluster-env"),
        pytest.param(False, False, id="no-default-cluster-env"),
    ],
)
def test_get_default_cluster_env_build_id(no_cluster_env, no_default_cluster_env):
    mock_cluster_env_list = []
    mock_build_id = "mock_id"
    if not no_cluster_env:
        mock_cluster_env_list.append(
            MagicMock(
                is_default=not no_default_cluster_env,
                latest_build=MagicMock(id=mock_build_id),
            )
        )
        mock_cluster_env_list.append(
            MagicMock(is_default=False, latest_build=MagicMock(id="mock_id_2"))
        )

    mock_api_client = Mock()
    mock_api_client.list_application_templates_api_v2_application_templates_get = Mock(
        return_value=Mock(results=mock_cluster_env_list)
    )
    controller = CloudFunctionalVerificationController(Mock())
    controller.api_client = mock_api_client
    if no_cluster_env:
        with pytest.raises(ClickException) as e:
            controller.get_default_cluster_env_build_id()
        e.match("No cluster environments found")
    else:
        assert controller.get_default_cluster_env_build_id() == mock_build_id
