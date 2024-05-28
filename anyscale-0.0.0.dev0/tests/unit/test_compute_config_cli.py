import os
from typing import Generator, Optional
from unittest.mock import Mock, patch
import uuid

import click
from click.testing import CliRunner
import pytest

from anyscale._private.sdk import _LAZY_SDK_SINGLETONS
from anyscale.commands.compute_config_commands import (
    archive_compute_config,
    create_compute_config,
    get_compute_config,
)
from anyscale.compute_config.commands import _COMPUTE_CONFIG_SDK_SINGLETON_KEY
from anyscale.compute_config.models import ComputeConfig, ComputeConfigVersion


def _get_test_file_path(subpath: str) -> str:
    return os.path.join(os.path.dirname(__file__), "test_files/", subpath)


MINIMAL_CONFIG_PATH = _get_test_file_path("compute_config_files/minimal.yaml")
FULL_CONFIG_PATH = _get_test_file_path("compute_config_files/full.yaml")

DEFAULT_COMPUTE_CONFIG_ID = "default-fake-compute-config-id"


class FakeComputeConfigSDK:
    DEFAULT_COMPUTE_CONFIG_NAME = "default-fake-compute-config-name"
    DEFAULT_COMPUTE_CONFIG = ComputeConfig(cloud="custom-cloud")

    def __init__(self):
        # Create method.
        self.created_config: Optional[ComputeConfig] = None
        self.created_id: Optional[str] = None
        self.created_name: Optional[str] = None

        # Get method.
        self.fetched_name: Optional[str] = None
        self.fetched_id: Optional[str] = None
        self.fetched_include_archived: Optional[bool] = None

        # Archive method.
        self.archived_name: Optional[str] = None
        self.archived_id: Optional[str] = None

    def create_compute_config(self, config: ComputeConfig, *, name: Optional[str]):
        assert isinstance(config, ComputeConfig)
        self.created_config = config
        self.created_id = str(uuid.uuid4())
        self.created_name = name or self.DEFAULT_COMPUTE_CONFIG_NAME
        return f"{self.created_name}:1", self.created_id

    def get_compute_config(
        self,
        *,
        name: Optional[str],
        id: Optional[str],  # noqa: A002
        include_archived: bool = False,
    ):
        self.fetched_name = name
        self.fetched_id = id
        self.fetched_include_archived = include_archived

        returned_name = name or self.DEFAULT_COMPUTE_CONFIG_NAME
        if ":" not in returned_name:
            returned_name += ":1"
        return ComputeConfigVersion(
            name=returned_name, id=id or str(uuid.uuid4()), config=ComputeConfig(),
        )

    def archive_compute_config(
        self, *, name: Optional[str], id: Optional[str]  # noqa: A002
    ):
        self.archived_name = name
        self.archived_id = id


@pytest.fixture()
def mock_compute_config_controller() -> Generator[Mock, None, None]:
    mock_compute_config_controller = Mock(
        create=Mock(return_value=DEFAULT_COMPUTE_CONFIG_ID),
        get=Mock(return_value={"old": "format", "compute": "config"}),
    )
    mock_compute_config_controller_cls = Mock(
        return_value=mock_compute_config_controller
    )
    with patch(
        "anyscale.commands.compute_config_commands.ComputeConfigController",
        new=mock_compute_config_controller_cls,
    ):
        yield mock_compute_config_controller


@pytest.fixture()
def fake_compute_config_sdk() -> Generator[FakeComputeConfigSDK, None, None]:
    fake_compute_config_sdk = FakeComputeConfigSDK()
    _LAZY_SDK_SINGLETONS[_COMPUTE_CONFIG_SDK_SINGLETON_KEY] = fake_compute_config_sdk
    try:
        yield fake_compute_config_sdk
    finally:
        del _LAZY_SDK_SINGLETONS[_COMPUTE_CONFIG_SDK_SINGLETON_KEY]


def _assert_error_message(result: click.testing.Result, *, message: str):
    assert result.exit_code != 0
    assert message in result.stdout


class TestCreate:
    def test_no_config_file(
        self, fake_compute_config_sdk, mock_compute_config_controller
    ):
        runner = CliRunner()
        result = runner.invoke(create_compute_config)
        _assert_error_message(
            result,
            message="Either the --config-file flag or [COMPUTE_CONFIG_FILE] argument must be provided",
        )

    def test_config_file_argument_and_flag(
        self, fake_compute_config_sdk, mock_compute_config_controller
    ):
        runner = CliRunner()
        result = runner.invoke(
            create_compute_config, ["-f", "flag.yaml", MINIMAL_CONFIG_PATH]
        )
        _assert_error_message(
            result,
            message="Only one of the --config-file flag or [COMPUTE_CONFIG_FILE] argument can be provided",
        )

    def test_config_file_argument_not_found(
        self, fake_compute_config_sdk, mock_compute_config_controller
    ):
        runner = CliRunner()
        result = runner.invoke(create_compute_config, ["missing_config.yaml"])
        _assert_error_message(
            result, message="'missing_config.yaml': No such file or directory",
        )

    def test_config_file_flag_not_found(
        self, fake_compute_config_sdk, mock_compute_config_controller
    ):
        runner = CliRunner()
        result = runner.invoke(create_compute_config, ["-f", "missing_config.yaml"])
        assert isinstance(result.exception, FileNotFoundError)
        assert "No such file or directory: 'missing_config.yaml'" in str(
            result.exception
        )

    def test_config_file_argument(
        self, fake_compute_config_sdk, mock_compute_config_controller
    ):
        runner = CliRunner()
        result = runner.invoke(create_compute_config, [MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout
        assert fake_compute_config_sdk.created_config is None
        mock_compute_config_controller.create.assert_called_once()

    @pytest.mark.parametrize(
        "name", [None, "test-name"],
    )
    @pytest.mark.parametrize(
        "config_file", [MINIMAL_CONFIG_PATH, FULL_CONFIG_PATH],
    )
    def test_config_file_flag(
        self, fake_compute_config_sdk, mock_compute_config_controller, config_file, name
    ):
        runner = CliRunner()
        args = ["-f", config_file]
        if name is not None:
            args += ["-n", name]
        result = runner.invoke(create_compute_config, args)
        assert result.exit_code == 0, result.stdout
        mock_compute_config_controller.create.assert_not_called()
        assert fake_compute_config_sdk.created_config.cloud == "test-cloud-from-file"
        if name is None:
            assert (
                fake_compute_config_sdk.created_name
                == fake_compute_config_sdk.DEFAULT_COMPUTE_CONFIG_NAME
            )
        else:
            assert fake_compute_config_sdk.created_name == name


class TestGet:
    def test_missing_name_and_id(
        self, fake_compute_config_sdk, mock_compute_config_controller
    ):
        runner = CliRunner()
        result = runner.invoke(get_compute_config, [])
        _assert_error_message(
            result,
            message="Either -n/--name or --id/--compute-config-id must be provided",
        )

    def test_name_and_id(self, fake_compute_config_sdk, mock_compute_config_controller):
        runner = CliRunner()
        result = runner.invoke(
            get_compute_config, ["-n", "test-name", "--id", "test-id"]
        )
        _assert_error_message(
            result, message="Only one of name or ID can be provided",
        )

    def test_positional_and_flag_name(
        self, fake_compute_config_sdk, mock_compute_config_controller
    ):
        runner = CliRunner()
        result = runner.invoke(
            get_compute_config, ["-n", "test-name", "test-positional-name"]
        )
        _assert_error_message(
            result, message="Both -n/--name and [COMPUTE_CONFIG_NAME] were provided",
        )

    @pytest.mark.parametrize("include_archived", [False, True])
    @pytest.mark.parametrize("positional_name", [False, True])
    def test_get_by_name(
        self,
        fake_compute_config_sdk,
        mock_compute_config_controller,
        positional_name,
        include_archived,
    ):
        runner = CliRunner()
        if positional_name:
            args = ["test-name"]
        else:
            args = ["-n", "test-name"]

        if include_archived:
            args = ["--include-archived"] + args

        result = runner.invoke(get_compute_config, args)
        assert result.exit_code == 0, result.stdout
        mock_compute_config_controller.get.assert_not_called()
        assert fake_compute_config_sdk.fetched_name == "test-name"
        assert fake_compute_config_sdk.fetched_id is None
        assert fake_compute_config_sdk.fetched_include_archived is include_archived

    @pytest.mark.parametrize("include_archived", [False, True])
    def test_get_by_id(
        self, fake_compute_config_sdk, mock_compute_config_controller, include_archived
    ):
        runner = CliRunner()
        args = ["--id", "test-id"]
        if include_archived:
            args = ["--include-archived"] + args

        result = runner.invoke(get_compute_config, args)
        assert result.exit_code == 0, result.stdout
        mock_compute_config_controller.get.assert_not_called()
        assert fake_compute_config_sdk.fetched_name is None
        assert fake_compute_config_sdk.fetched_id == "test-id"
        assert fake_compute_config_sdk.fetched_include_archived is include_archived

    @pytest.mark.parametrize("include_archived", [False, True])
    @pytest.mark.parametrize("positional_name", [False, True])
    def test_old_format_by_name(
        self,
        fake_compute_config_sdk,
        mock_compute_config_controller,
        positional_name,
        include_archived,
    ):
        runner = CliRunner()
        if positional_name:
            args = ["test-name"]
        else:
            args = ["-n", "test-name"]

        if include_archived:
            args = ["--include-archived"] + args

        args = ["--old-format"] + args

        result = runner.invoke(get_compute_config, args)
        assert result.exit_code == 0, result.stdout
        mock_compute_config_controller.get.assert_called_once_with(
            cluster_compute_name="test-name",
            cluster_compute_id=None,
            include_archived=include_archived,
        )
        assert fake_compute_config_sdk.fetched_name is None
        assert fake_compute_config_sdk.fetched_id is None
        assert fake_compute_config_sdk.fetched_include_archived is None

    @pytest.mark.parametrize("include_archived", [False, True])
    def test_old_format_by_id(
        self, fake_compute_config_sdk, mock_compute_config_controller, include_archived
    ):
        runner = CliRunner()
        args = ["--old-format", "--id", "test-id"]

        if include_archived:
            args = ["--include-archived"] + args

        result = runner.invoke(get_compute_config, args)
        assert result.exit_code == 0, result.stdout
        mock_compute_config_controller.get.assert_called_once_with(
            cluster_compute_name=None,
            cluster_compute_id="test-id",
            include_archived=include_archived,
        )
        assert fake_compute_config_sdk.fetched_name is None
        assert fake_compute_config_sdk.fetched_id is None
        assert fake_compute_config_sdk.fetched_include_archived is None


class TestArchive:
    def test_missing_name_and_id(self, fake_compute_config_sdk):
        runner = CliRunner()
        result = runner.invoke(archive_compute_config, [])
        _assert_error_message(
            result,
            message="Either -n/--name or --id/--compute-config-id must be provided",
        )

    def test_name_and_id(self, fake_compute_config_sdk):
        runner = CliRunner()
        result = runner.invoke(
            archive_compute_config, ["-n", "test-name", "--id", "test-id"]
        )
        _assert_error_message(
            result, message="Only one of name or ID can be provided",
        )

    def test_positional_and_flag_name(self, fake_compute_config_sdk):
        runner = CliRunner()
        result = runner.invoke(
            archive_compute_config, ["-n", "test-name", "test-positional-name"]
        )
        _assert_error_message(
            result, message="Both -n/--name and [COMPUTE_CONFIG_NAME] were provided",
        )

    @pytest.mark.parametrize("positional_name", [False, True])
    def test_get_by_name(self, fake_compute_config_sdk, positional_name):
        runner = CliRunner()
        if positional_name:
            args = ["test-name"]
        else:
            args = ["-n", "test-name"]

        result = runner.invoke(archive_compute_config, args)
        assert result.exit_code == 0, result.stdout
        assert fake_compute_config_sdk.archived_name == "test-name"
        assert fake_compute_config_sdk.archived_id is None

    def test_get_by_id(self, fake_compute_config_sdk):
        runner = CliRunner()
        args = ["--id", "test-id"]

        result = runner.invoke(archive_compute_config, args)
        assert result.exit_code == 0, result.stdout
        assert fake_compute_config_sdk.archived_name is None
        assert fake_compute_config_sdk.archived_id == "test-id"
