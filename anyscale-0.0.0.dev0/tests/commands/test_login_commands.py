from unittest.mock import Mock, patch

from click.testing import CliRunner
import pytest

from anyscale.client.openapi_client import (
    CreateOTPReturnApiModel,
    RequestOTPReturnApiModel,
)
from anyscale.client.openapi_client.models import (
    CreateotpreturnapimodelResponse,
    RequestotpreturnapimodelResponse,
)
from anyscale.commands.login_commands import anyscale_login, anyscale_logout


@pytest.mark.parametrize(
    "webbrowser_error", [False, True],
)
def test_anyscale_login(webbrowser_error: bool) -> None:
    runner = CliRunner()

    mock_api_client = Mock()
    mock_api_client.create_one_time_password_api_v2_users_create_otp_token_get = Mock(
        return_value=CreateotpreturnapimodelResponse(
            result=CreateOTPReturnApiModel(
                url="https://console.anyscale.com/otp/fake-otp-token",
                otp="fake-otp-token",
            )
        )
    )
    mock_api_client.check_one_time_password_api_v2_users_request_otp_token_otp_get = Mock(
        return_value=RequestotpreturnapimodelResponse(
            result=RequestOTPReturnApiModel(
                valid=True, server_session_id="fake-session-id",
            )
        )
    )
    mock_auth_controller_set = Mock()
    if webbrowser_error:
        mock_webbrowser_open = Mock(side_effect=Exception("some error"))
    else:
        mock_webbrowser_open = Mock()

    with patch.multiple(
        "anyscale.commands.login_commands",
        get_unauthenticated_openapi_client=Mock(return_value=mock_api_client),
        webbrowser=Mock(),
    ), patch.multiple(
        "anyscale.commands.login_commands.AuthController", set=mock_auth_controller_set,
    ), patch.multiple(
        "anyscale.commands.login_commands.webbrowser", open=mock_webbrowser_open,
    ):
        runner.invoke(anyscale_login)

        mock_api_client.create_one_time_password_api_v2_users_create_otp_token_get.assert_called_once()
        mock_api_client.check_one_time_password_api_v2_users_request_otp_token_otp_get.assert_called_once_with(
            "fake-otp-token"
        )
        mock_auth_controller_set.assert_called_once_with("fake-session-id")
        mock_webbrowser_open.assert_called_once_with(
            "https://console.anyscale.com/otp/fake-otp-token"
        )


def test_anyscale_logout() -> None:
    runner = CliRunner()

    mock_auth_controller_remove = Mock()
    with patch.multiple(
        "anyscale.commands.login_commands.AuthController",
        remove=mock_auth_controller_remove,
    ):
        runner.invoke(anyscale_logout)
        mock_auth_controller_remove.assert_called_once_with(ask=False)
