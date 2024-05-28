from contextlib import redirect_stderr, redirect_stdout
import io
import os
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError
import click
from google.api_core.exceptions import GoogleAPICallError
from googleapiclient.errors import HttpError
import pytest

from anyscale.authenticate import get_auth_api_client
from anyscale.cli_logger import BlockLogger, CloudSetupLogger
from anyscale.client.openapi_client.models import CloudAnalyticsEventCloudResource
from anyscale.client.openapi_client.rest import ApiException as ApiExceptionInternal
from anyscale.sdk.anyscale_client.rest import ApiException as ApiExceptionExternal


def test_warning_to_stderr():
    # Test warnings are printed to stderr
    log = BlockLogger()
    f = io.StringIO()
    warning_message = "test_warning"
    with redirect_stderr(f):
        log.warning(warning_message)

    assert warning_message in f.getvalue()


def test_block():
    log = BlockLogger()

    # Test opening block, writing info, closing block
    log.open_block(block_label="block1")
    log.info("msg1", block_label="block1")
    log.close_block(block_label="block1")

    # Test error raised when opening two blocks without closing first
    log.open_block(block_label="block1")
    with pytest.raises(Exception):  # noqa: PT011
        log.open_block(block_label="block2")

    # Test error raised when closing block that wasn't opened
    with pytest.raises(Exception):  # noqa: PT011
        log.close_block(block_label="block2")

    # Test error raised when writing to block that wasn't opened
    with pytest.raises(Exception):  # noqa: PT011
        log.info("msg2", block_label="block2")


def test_debug_env_var():
    log = BlockLogger()
    f = io.StringIO()
    debug_message = "test_debug"

    # Test debug message is not printed to stdout if ANYSCALE_DEBUG != 1
    os.environ.pop("ANYSCALE_DEBUG", None)
    with redirect_stdout(f):
        log.debug(debug_message)
    assert f.getvalue() == ""

    # Test debug message is printed to stdout if ANYSCALE_DEBUG == 1
    os.environ["ANYSCALE_DEBUG"] = "1"
    with redirect_stdout(f):
        log.debug(debug_message)
    assert debug_message in f.getvalue()


def test_format_api_exception_internal():
    # Tests that API exceptions are correctly formatted for the internal API
    BlockLogger()
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock",
        _validate_api_client_auth=Mock(),
        _validate_credentials_format=Mock(),
    ):
        mock_api_client = get_auth_api_client(
            cli_token="fake_cli_token", host="fake_host"
        ).api_client

    # Test non ApiExceptions are not caught by log.format_api_exception
    with patch.multiple(
        "anyscale.api.openapi_client.ApiClient",
        call_api=Mock(side_effect=ZeroDivisionError()),
    ), pytest.raises(ZeroDivisionError):
        mock_api_client.get_project_api_v2_projects_project_id_get("bad_project_id")

    e = ApiExceptionInternal()
    e.headers = Mock(_container={})
    with patch.multiple(
        "anyscale.api.openapi_client.ApiClient", call_api=Mock(side_effect=e),
    ):
        # Test original ApiException is raised if ANYSCALE_DEBUG == 1
        os.environ["ANYSCALE_DEBUG"] = "1"
        with pytest.raises(ApiExceptionInternal):
            mock_api_client.get_project_api_v2_projects_project_id_get("bad_project_id")

        # Test formatted ClickException is raised if ANYSCALE_DEBUG != 1
        os.environ.pop("ANYSCALE_DEBUG", None)
        with pytest.raises(click.ClickException):
            mock_api_client.get_project_api_v2_projects_project_id_get("bad_project_id")


def test_format_api_exception_external():
    # Tests that API exceptions are correctly formatted for the external API
    BlockLogger()
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock",
        _validate_api_client_auth=Mock(),
        _validate_credentials_format=Mock(),
    ):
        mock_api_client = get_auth_api_client(
            cli_token="fake_cli_token", host="fake_host"
        ).anyscale_api_client

    # Test non ApiExceptions are not caught by log.format_api_exception
    with patch.multiple(
        "anyscale.sdk.anyscale_client.ApiClient",
        call_api=Mock(side_effect=ZeroDivisionError()),
    ), pytest.raises(ZeroDivisionError):
        mock_api_client.list_projects()

    e = ApiExceptionExternal()
    e.headers = Mock(_container={})
    with patch.multiple(
        "anyscale.sdk.anyscale_client.ApiClient", call_api=Mock(side_effect=e),
    ):
        # Test original ApiException is raised if ANYSCALE_DEBUG == 1
        os.environ["ANYSCALE_DEBUG"] = "1"
        with pytest.raises(ApiExceptionExternal):
            mock_api_client.list_projects()

        # Test formatted ClickException is raised if ANYSCALE_DEBUG != 1
        os.environ.pop("ANYSCALE_DEBUG", None)
        with pytest.raises(click.ClickException):
            mock_api_client.list_projects()


@pytest.mark.parametrize(
    "exception_class", [Exception, GoogleAPICallError, HttpError, ClientError,]
)
@pytest.mark.parametrize("code_exists", [True, False])
@pytest.mark.parametrize("reason_exists", [True, False])
@pytest.mark.parametrize("valid_error_details", [True, False])
def test_log_resource_exception(
    exception_class, code_exists, reason_exists, valid_error_details: bool
):
    logger = CloudSetupLogger()
    mock_log_error = Mock()
    mock_cloud_resource = Mock()
    mock_exception = Mock(spec=exception_class)
    mock_error_reason = "mock_error_reason" if reason_exists else None
    mock_error_code = 404 if code_exists else None
    if exception_class == ClientError:
        mock_exception.response = {
            "Error": {"Code": mock_error_reason},
            "ResponseMetadata": {"HTTPStatusCode": mock_error_code},
        }
    elif exception_class == GoogleAPICallError:
        mock_exception.code = mock_error_code
        mock_exception.reason = mock_error_reason
    elif exception_class == HttpError:
        mock_exception.status_code = mock_error_code
        mock_exception.error_details = (
            [{"reason": mock_error_reason}] if valid_error_details else "wrong_format"
        )
    with patch.multiple(
        "anyscale.cli_logger.CloudSetupLogger", log_resource_error=mock_log_error,
    ):
        if exception_class in (GoogleAPICallError, HttpError):
            logger.log_resource_exception(
                CloudAnalyticsEventCloudResource.GCP_PROJECT, mock_exception
            )
            if exception_class == GoogleAPICallError:
                mock_log_error.assert_called_once_with(
                    CloudAnalyticsEventCloudResource.GCP_PROJECT,
                    mock_error_reason,
                    mock_error_code,
                    "GoogleAPICallError",
                )
            else:
                expected_error_reason = (
                    mock_error_reason if valid_error_details else None
                )
                mock_log_error.assert_called_once_with(
                    CloudAnalyticsEventCloudResource.GCP_PROJECT,
                    expected_error_reason,
                    mock_error_code,
                    "HttpError",
                )
        else:
            logger.log_resource_exception(mock_cloud_resource, mock_exception)
            if exception_class == ClientError:
                mock_log_error.assert_called_once_with(
                    mock_cloud_resource,
                    mock_error_reason,
                    mock_error_code,
                    "ClientError",
                )
            else:
                mock_log_error.assert_called_once_with(
                    mock_cloud_resource,
                    None,
                    None,
                    f"UnknownExceptionType_{Exception.__name__}",
                )


@pytest.mark.parametrize("error_reason", ["not_found", None])
@pytest.mark.parametrize("status_code", [404, None])
@pytest.mark.parametrize("unhandled_exception", ["MockException", None])
def test_log_resource_error(error_reason, status_code, unhandled_exception):
    logger = CloudSetupLogger()
    mock_cloud_resource = Mock()
    logger.log_resource_error(
        mock_cloud_resource, error_reason, status_code, unhandled_exception
    )
    assert len(logger.cloud_resource_errors) == 1
    cloud_resource_error = logger.cloud_resource_errors[0]
    assert cloud_resource_error.cloud_resource == mock_cloud_resource
    expected_error_code = f"{error_reason if error_reason else 'unknown'}"
    if status_code:
        expected_error_code = f"{expected_error_code},{status_code}"
    if unhandled_exception:
        expected_error_code = f"{expected_error_code},{unhandled_exception}"
    assert cloud_resource_error.error_code == expected_error_code

    # Log duplicated error
    logger.log_resource_error(
        mock_cloud_resource, error_reason, status_code, unhandled_exception
    )
    assert len(logger.cloud_resource_errors) == 1


def test_get_cloud_provider_errors():
    logger = CloudSetupLogger()
    mock_cloud_resource = Mock()
    logger.log_resource_error(mock_cloud_resource, "not_found", 404)
    errors = logger.get_cloud_provider_errors()
    assert len(errors) == 1
    assert errors[0].cloud_resource == mock_cloud_resource
    assert errors[0].error_code == "not_found,404"


def test_clear_cloud_provider_errors():
    logger = CloudSetupLogger()
    mock_cloud_resource = Mock()
    logger.log_resource_error(mock_cloud_resource, "not_found", 404)
    logger.clear_cloud_provider_errors()
    assert len(logger.cloud_resource_errors) == 0
