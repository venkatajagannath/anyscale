import json
import tempfile
from unittest.mock import Mock, patch

import click
import pytest

import anyscale
from anyscale.authenticate import AuthenticationBlock
from anyscale.client.openapi_client.rest import ApiException as ApiExceptionInternal
import anyscale.conf


def test_load_credentials_env_var(monkeypatch):
    """
    Test credentials loaded from environment variable even when credentials exist in file.
    """
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock", __init__=Mock(return_value=None)
    ):
        auth_api_client = AuthenticationBlock()

    monkeypatch.setenv("ANYSCALE_CLI_TOKEN", "sss_os_environ")
    with tempfile.NamedTemporaryFile("w") as temp_credentials_file:
        temp_credentials_file.write(json.dumps({"cli_token": "sss_file_credential"}))
        temp_credentials_file.flush()
        anyscale.authenticate.CREDENTIALS_FILE = temp_credentials_file.name
        assert auth_api_client._load_credentials() == (
            "sss_os_environ",
            "ANYSCALE_CLI_TOKEN",
        )


def test_load_credentials_file(monkeypatch):
    """
    Test credentials loaded from file when credentials don't exist in environment variable.
    """
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock", __init__=Mock(return_value=None)
    ):
        auth_api_client = AuthenticationBlock()

    monkeypatch.delenv("ANYSCALE_CLI_TOKEN", raising=False)
    with tempfile.NamedTemporaryFile("w") as temp_credentials_file:
        temp_credentials_file.write(json.dumps({"cli_token": "sss_file_credential"}))
        temp_credentials_file.flush()
        anyscale.authenticate.CREDENTIALS_FILE = temp_credentials_file.name
        assert auth_api_client._load_credentials() == (
            "sss_file_credential",
            anyscale.authenticate.CREDENTIALS_FILE,
        )


def test_validate_credentials_format() -> None:
    """
    Test credentials are of the correct format.
    """
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock", __init__=Mock(return_value=None)
    ):
        auth_api_client = AuthenticationBlock()

    with pytest.raises(click.ClickException):
        auth_api_client._validate_credentials_format("abc")

    with pytest.raises(click.ClickException):
        auth_api_client._validate_credentials_format("")

    # Should not raise an exception.
    auth_api_client._validate_credentials_format("sss_abcdefghjijklmnop")

    # Possible format of new tokens.
    auth_api_client._validate_credentials_format("ast_potential_new_token")


def test_validate_api_client_auth() -> None:
    """
    Test credentials are validated with by calling /api/v2/userinfo.
    """
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock", __init__=Mock(return_value=None)
    ):
        auth_api_client = AuthenticationBlock()

    # Test credentials are validated when /api/v2/userinfo returns successful response.
    auth_api_client.api_client = Mock()
    auth_api_client._validate_api_client_auth()

    # Test error is raised when /api/v2/userinfo returns 401 not authenticated response.
    auth_api_client.api_client.get_user_info_api_v2_userinfo_get = Mock(
        side_effect=ApiExceptionInternal(status=401)
    )
    with pytest.raises(click.ClickException):
        auth_api_client._validate_api_client_auth()


def test_warn_credential_file_permissions():
    """
    Test if logger warns when credentials file permissions are too open
    """
    with patch.multiple(
        "os.path",
        expanduser=Mock(return_value="/home/usr0/.anyscale/credentials.json"),
        exists=Mock(return_value=True),
    ), patch("os.stat", Mock()):
        mock_log_warning = Mock()

        nowarn_modes = [0o600, 0o700, 0o400]
        for mode in nowarn_modes:
            with patch("stat.S_IMODE", Mock(return_value=mode)), patch(
                "anyscale.cli_logger.BlockLogger.warning", mock_log_warning
            ):
                auth = AuthenticationBlock(cli_token="", validate_credentials=False)
                auth._warn_credential_file_permissions(
                    "/home/usr0/.anyscale/credentials.json"
                )
            mock_log_warning.assert_not_called()
            mock_log_warning.reset_mock()

        warn_modes = [0o644, 0o777, 0o640, 0o770]
        for mode in warn_modes:
            with patch("stat.S_IMODE", Mock(return_value=mode)), patch(
                "anyscale.cli_logger.BlockLogger.warning", mock_log_warning
            ):
                auth = AuthenticationBlock(cli_token="", validate_credentials=False)
                auth._warn_credential_file_permissions(
                    "/home/usr0/.anyscale/credentials.json"
                )
            mock_log_warning.assert_called()
            mock_log_warning.reset_mock()


def test_warn_credential_file_permissions_dont_on_windows():
    """
    Test that no warning is printed on Windows
    """
    mock_log_warning = Mock()
    with patch.multiple(
        "os.path",
        expanduser=Mock(return_value="/home/usr0/.anyscale/credentials.json"),
        exists=Mock(return_value=True),
    ), patch("os.stat", Mock()), patch(
        "anyscale.cli_logger.BlockLogger.warning", mock_log_warning
    ), patch(
        "platform.system", Mock(return_value="Windows")
    ):
        auth = AuthenticationBlock(cli_token="", validate_credentials=False)
        auth._warn_credential_file_permissions("/home/usr0/.anyscale/credentials.json")

    mock_log_warning.assert_not_called()
