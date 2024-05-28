import re
from typing import Any, Tuple
from unittest.mock import Mock, patch

from click import ClickException
from google.auth.credentials import AnonymousCredentials
from google.auth.exceptions import DefaultCredentialsError, RefreshError
import pytest

from anyscale.cli_logger import CloudSetupLogger
from anyscale.client.openapi_client.models.gcp_file_store_config import (
    GCPFileStoreConfig,
)
from anyscale.utils.gcp_utils import (
    get_application_default_credentials,
    get_filestore_location_and_instance_id,
    get_gcp_filestore_config,
    get_gcp_memorystore_config,
    get_google_cloud_client_factory,
)


@pytest.mark.parametrize(
    ("filestore_id", "response", "not_found", "expected_result"),
    [
        pytest.param(
            "regional-filestore",
            ("200 OK", "regional_filestore.json"),
            False,
            GCPFileStoreConfig(
                instance_name="projects/anyscale-bridge-deadbeef/locations/us-central1/instances/regional-filestore",
                root_dir="something",
                mount_target_ip="172.22.236.2",
            ),
            id="regional",
        ),
        pytest.param(
            "zonal-filestore",
            ("200 OK", "zonal_filestore.json"),
            False,
            GCPFileStoreConfig(
                instance_name="projects/anyscale-bridge-deadbeef/locations/us-central1/instances/zonal-filestore",
                root_dir="test",
                mount_target_ip="172.27.155.250",
            ),
            id="zonal",
        ),
        pytest.param(
            "regional-filestore",
            ("200 OK", "regional_filestore_wrong_vpc.json"),
            False,
            None,
            id="wrong_vpc",
        ),
        pytest.param(
            "regional-filestore",
            ("200 OK", "regional_filestore_vpc_private_access.json"),
            False,
            GCPFileStoreConfig(
                instance_name="projects/anyscale-bridge-deadbeef/locations/us-central1/instances/regional-filestore",
                root_dir="something",
                mount_target_ip="172.22.236.2",
            ),
            id="regional-private-access",
        ),
        pytest.param(
            "regional-filestore", ("404 Not Found", None), True, None, id="not_found"
        ),
    ],
)
def test_get_gcp_filestore_config(
    setup_mock_server, filestore_id, capsys, response, not_found, expected_result,
):
    factory, tracker = setup_mock_server
    mock_project_id = "anyscale-bridge-deadbeef"
    mock_vpc_name = "vpc_one"
    mock_filestore_region = "us-central1"
    tracker.reset({".*": [response]})
    if expected_result:
        assert (
            get_gcp_filestore_config(
                factory,
                mock_project_id,
                mock_vpc_name,
                mock_filestore_region,
                filestore_id,
                CloudSetupLogger(),
            )
            == expected_result
        )
    elif not_found:
        with pytest.raises(ClickException) as e:
            get_gcp_filestore_config(
                factory,
                mock_project_id,
                mock_vpc_name,
                mock_filestore_region,
                filestore_id,
                CloudSetupLogger(),
            )
        e.match("Could not find Filestore with id")
    else:
        with pytest.raises(ClickException):
            get_gcp_filestore_config(
                factory,
                mock_project_id,
                mock_vpc_name,
                mock_filestore_region,
                filestore_id,
                CloudSetupLogger(),
            )
        _, err = capsys.readouterr()
        assert "This cannot be edited on an existing Filestore instance." in err


@pytest.mark.parametrize(
    ("enable_head_node_fault_tolerance", "response"),
    [
        pytest.param(True, ("200 OK", "regional_memorystore.json"),),
        pytest.param(False, (None, None),),
    ],
)
def test_get_gcp_memorystore_config(
    setup_mock_server, enable_head_node_fault_tolerance, response
):
    factory, tracker = setup_mock_server
    tracker.reset({".*": [response]})
    mock_redis_instance_name = (
        "projects/mock_project/locations/us-west1/instances/mock_redis_instance_name"
        if enable_head_node_fault_tolerance
        else None
    )
    memorystore_instance_config = get_gcp_memorystore_config(
        factory, mock_redis_instance_name
    )

    if enable_head_node_fault_tolerance:
        assert memorystore_instance_config is not None
        assert memorystore_instance_config.name == mock_redis_instance_name
    else:
        assert memorystore_instance_config is None


def test_get_application_default_credentials_success(capsys):
    mock_run = Mock()
    with patch(
        "anyscale.utils.gcp_utils.google.auth",
        default=Mock(return_value=(Mock(), "project_abc")),
    ), patch("anyscale.utils.gcp_utils.subprocess", run=mock_run):
        credentials, project = get_application_default_credentials(CloudSetupLogger())
        assert credentials is not None
        assert project == "project_abc"

    _, err = capsys.readouterr()
    assert err == ""

    mock_run.assert_not_called()


@pytest.mark.parametrize(
    ("refresh_error", "expected_output"),
    [
        pytest.param(True, "Reauthentication is needed", id="ReAuthNeeded"),
        pytest.param(False, "GCloud", id="NoAuthFound"),
    ],
)
def test_get_application_default_credentials_reauth(
    capsys, refresh_error: bool, expected_output: str
):
    num_calls = 0

    def default(*args: Any, **kwargs: Any) -> Tuple[Any, str]:
        nonlocal num_calls
        num_calls += 1
        if num_calls > 1:
            return Mock(), "project_abc"
        if refresh_error:
            mock_credentials = Mock()
            mock_credentials.refresh = Mock(side_effect=RefreshError)
            return mock_credentials, ""
        raise DefaultCredentialsError("abc")

    mock_run = Mock()
    mock_run.return_value.returncode = 0
    with patch(
        "anyscale.utils.gcp_utils.google.auth", default=Mock(side_effect=default)
    ), patch("anyscale.utils.gcp_utils.subprocess", run=mock_run):
        credentials, project = get_application_default_credentials(CloudSetupLogger())
        assert credentials is not None
        assert project == "project_abc"

    assert num_calls == 2
    mock_run.assert_called_once()
    _, err = capsys.readouterr()
    assert re.search(expected_output, err), err


@pytest.mark.parametrize(
    ("response", "valid_credentials"),
    [
        pytest.param(("200 OK", "service_get.json"), True, id="success"),
        pytest.param(("403 Forbidden", None), False, id="permission_denied"),
    ],
)
def test_get_google_cloud_client_factory(
    response, setup_mock_server, valid_credentials
):
    factory, tracker = setup_mock_server
    tracker.reset({".*": [response]})
    mock_project_id = "anyscale-bridge-deadbeef"
    if valid_credentials:
        with patch.multiple(
            "anyscale.utils.gcp_utils",
            get_application_default_credentials=Mock(
                return_value=(AnonymousCredentials(), mock_project_id)
            ),
            GoogleCloudClientFactory=Mock(return_value=factory),
        ):
            assert (
                get_google_cloud_client_factory(CloudSetupLogger(), mock_project_id)
                is not None
            )
    else:
        with patch.multiple(
            "anyscale.utils.gcp_utils",
            get_application_default_credentials=Mock(
                return_value=(AnonymousCredentials(), mock_project_id)
            ),
        ), pytest.raises(ClickException) as e:
            get_google_cloud_client_factory(CloudSetupLogger(), mock_project_id)
        e.match("Please make sure")


def test_get_filestore_location_and_instance_id():
    gcp_filestore_config = GCPFileStoreConfig(
        instance_name="projects/project_id/locations/fake_location/instances/fake_instance_id",
        root_dir="fake_root_dir",
        mount_target_ip="fake_mount_target_ip",
    )
    location, instance_id = get_filestore_location_and_instance_id(gcp_filestore_config)
    assert location == "fake_location"
    assert instance_id == "fake_instance_id"


def test_get_filestore_location_and_instance_id_exception():
    gcp_filestore_config = GCPFileStoreConfig(
        instance_name="projects/project_id",
        root_dir="fake_root_dir",
        mount_target_ip="fake_mount_target_ip",
    )
    with pytest.raises(ClickException) as e:
        get_filestore_location_and_instance_id(gcp_filestore_config)
    e.match("Could not parse Filestore instance name")
