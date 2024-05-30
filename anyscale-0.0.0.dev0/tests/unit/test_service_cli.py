import os
from typing import Any, Dict, Generator, Optional

import click
from click.testing import CliRunner
import pytest

from anyscale._private.sdk import _LAZY_SDK_SINGLETONS
from anyscale.commands.service_commands import deploy, status, wait
from anyscale.compute_config.models import ComputeConfig, HeadNodeConfig
from anyscale.service.commands import _SERVICE_SDK_SINGLETON_KEY
from anyscale.service.models import (
    ServiceConfig,
    ServiceState,
    ServiceStatus,
    ServiceVersionState,
    ServiceVersionStatus,
)


def _get_test_file_path(subpath: str) -> str:
    return os.path.join(os.path.dirname(__file__), "test_files/", subpath,)


EMPTY_CONFIG_PATH = _get_test_file_path("service_config_files/empty.yaml")
MINIMAL_CONFIG_PATH = _get_test_file_path("service_config_files/minimal.yaml")
FULL_CONFIG_PATH = _get_test_file_path("service_config_files/full.yaml")
NAME_AND_GIBBERISH_CONFIG_PATH = _get_test_file_path(
    "service_config_files/name_and_gibberish.yaml"
)
MULTI_LINE_REQUIREMENTS_PATH = _get_test_file_path("requirements_files/multi_line.txt")


class FakeServiceSDK:
    DEFAULT_SERVICE_ID = "default-fake-service-id"
    DEFAULT_SERVICE_NAME = "default-fake-service-name"

    def __init__(self):
        self.deployed_config: Optional[ServiceConfig] = None
        self.deployed_kwargs: Dict[str, Any] = {}
        self.fetched_name: Optional[str] = None
        self.waited_name: Optional[str] = None
        self.waited_state: Optional[ServiceState] = None
        self.waited_timeout_s: Optional[float] = None

    def deploy(self, config: ServiceConfig, **kwargs):
        assert isinstance(config, ServiceConfig)
        self.deployed_config = config
        self.deployed_kwargs = kwargs

    def status(self, name: Optional[str] = None) -> ServiceStatus:
        self.fetched_name = name
        return ServiceStatus(
            id=self.DEFAULT_SERVICE_ID,
            name=name or self.DEFAULT_SERVICE_NAME,
            state=ServiceState.TERMINATED,
            query_url="http://fake-service-url/",
            query_auth_token="asdf1234",
            primary_version=ServiceVersionStatus(
                id="primary",
                state=ServiceVersionState.RUNNING,
                weight=100,
                config=ServiceConfig(applications=[{"import_path": "main:app"}]),
            ),
            canary_version=ServiceVersionStatus(
                id="canary",
                state=ServiceVersionState.STARTING,
                weight=0,
                config=ServiceConfig(applications=[{"import_path": "main:app"}]),
            ),
        )

    def wait(
        self, name: str, *, state: ServiceState, timeout_s: float, interval_s: float,
    ):
        self.waited_name = name
        self.waited_state = state
        self.waited_timeout_s = timeout_s


@pytest.fixture()
def fake_service_sdk() -> Generator[FakeServiceSDK, None, None]:
    fake_service_sdk = FakeServiceSDK()
    _LAZY_SDK_SINGLETONS[_SERVICE_SDK_SINGLETON_KEY] = fake_service_sdk
    try:
        yield fake_service_sdk
    finally:
        del _LAZY_SDK_SINGLETONS[_SERVICE_SDK_SINGLETON_KEY]


def _assert_error_message(result: click.testing.Result, *, message: str):
    assert result.exit_code != 0
    assert message in result.stdout


class TestDeploy:
    def test_deploy_no_arg(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(deploy)
        _assert_error_message(
            result, message="Either config file or import path must be provided."
        )

    def test_deploy_from_import_path(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(deploy, ["main:app"])
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(applications=[{"import_path": "main:app"}])
        assert (
            fake_service_sdk.deployed_config.applications
            == expected_config.applications
        )

    def test_deploy_from_import_path_with_args(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(deploy, ["main:app", "arg1=val1", "arg2=val2"])
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(
            applications=[
                {"import_path": "main:app", "args": {"arg1": "val1", "arg2": "val2"},}
            ],
        )
        assert (
            fake_service_sdk.deployed_config.applications
            == expected_config.applications
        )

    def test_deploy_from_import_path_with_bad_arg(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(deploy, ["main:app", "bad_arg"])
        _assert_error_message(
            result,
            message="Invalid key-value string 'bad_arg'. Must be of the form 'key=value'.",
        )

    def test_deploy_from_file(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(deploy, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(applications=[{"import_path": "main:app"}])
        assert (
            fake_service_sdk.deployed_config.applications
            == expected_config.applications
        )

    def test_deploy_from_file_with_import_path(self, fake_service_sdk):
        runner = CliRunner()
        os.path.join(
            os.path.dirname(__file__), "test_service_config_files", "minimal.yaml",
        )

        result = runner.invoke(
            deploy, ["-f", MINIMAL_CONFIG_PATH, "main:app", "arg1=val1"]
        )
        _assert_error_message(
            result,
            message="When a config file is provided, import path and application arguments can't be.",
        )

        result = runner.invoke(deploy, ["-f", MINIMAL_CONFIG_PATH, "main:app"])
        _assert_error_message(
            result,
            message="When a config file is provided, import path and application arguments can't be.",
        )

    @pytest.mark.parametrize("flag", ["--in-place", "-i"])
    def test_deploy_in_place(self, fake_service_sdk, flag: str):
        runner = CliRunner()
        result = runner.invoke(deploy, ["main:app", flag])
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(applications=[{"import_path": "main:app"}])
        assert (
            fake_service_sdk.deployed_config.applications
            == expected_config.applications
        )
        assert fake_service_sdk.deployed_kwargs == {
            "canary_percent": None,
            "in_place": True,
            "max_surge_percent": None,
        }

    def test_deploy_canary_percent(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(deploy, ["main:app", "--canary-percent", "50"])
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(applications=[{"import_path": "main:app"}])
        assert (
            fake_service_sdk.deployed_config.applications
            == expected_config.applications
        )
        assert fake_service_sdk.deployed_kwargs == {
            "canary_percent": 50,
            "in_place": False,
            "max_surge_percent": None,
        }

    def test_deploy_max_surge_percent(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(deploy, ["main:app", "--max-surge-percent", "50"])
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(applications=[{"import_path": "main:app"}])
        assert (
            fake_service_sdk.deployed_config.applications
            == expected_config.applications
        )
        assert fake_service_sdk.deployed_kwargs == {
            "canary_percent": None,
            "in_place": False,
            "max_surge_percent": 50,
        }

    def test_deploy_excludes(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(deploy, ["main:app"])
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(applications=[{"import_path": "main:app"}])
        assert (
            fake_service_sdk.deployed_config.applications
            == expected_config.applications
        )

        # Pass a single exclusion.
        result = runner.invoke(deploy, ["--exclude", "path1", "main:app"])
        assert result.exit_code == 0, result.stdout
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(
            applications=[{"import_path": "main:app"}], excludes=["path1"]
        )
        assert (
            fake_service_sdk.deployed_config.applications
            == expected_config.applications
        )

        # Pass multiple exclusions.
        result = runner.invoke(
            deploy, ["--exclude", "path1", "-e", "path2", "main:app"]
        )
        assert result.exit_code == 0, result.stdout
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(
            applications=[{"import_path": "main:app"}], excludes=["path1", "path2"]
        )
        assert (
            fake_service_sdk.deployed_config.applications
            == expected_config.applications
        )

    def test_deploy_both_image_uri_and_containerfile(self):
        runner = CliRunner()
        result = runner.invoke(
            deploy, ["main:app", "--image-uri", "image", "--containerfile", "file"]
        )
        _assert_error_message(
            result,
            message="Only one of '--containerfile' and '--image-uri' can be provided.",
        )

    def test_deploy_from_file_override_options(self, fake_service_sdk):
        runner = CliRunner()

        # No overrides, should match the config in the file.
        result = runner.invoke(deploy, ["-f", FULL_CONFIG_PATH])
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None

        inline_compute_config = ComputeConfig(
            cloud="test-cloud", head_node=HeadNodeConfig(instance_type="m5.2xlarge")
        )

        expected_config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-name-from-file",
            image_uri="docker.io/library/test:latest",
            compute_config=inline_compute_config,
            working_dir="test-working-dir",
            excludes=["test"],
            requirements=["pip-install-test"],
            query_auth_token_enabled=False,
            http_options={"request_timeout_s": 10.0},
            grpc_options={"grpc_servicer_functions": ["hello.world"]},
            logging_config={"log_level": "DEBUG"},
        )
        assert fake_service_sdk.deployed_config == expected_config

        # Override name.
        result = runner.invoke(
            deploy, ["-f", FULL_CONFIG_PATH, "--name", "override-name"]
        )
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="override-name",
            image_uri="docker.io/library/test:latest",
            compute_config=inline_compute_config,
            working_dir="test-working-dir",
            excludes=["test"],
            requirements=["pip-install-test"],
            query_auth_token_enabled=False,
            http_options={"request_timeout_s": 10.0},
            grpc_options={"grpc_servicer_functions": ["hello.world"]},
            logging_config={"log_level": "DEBUG"},
        )
        assert fake_service_sdk.deployed_config == expected_config

        # Override image URI.
        result = runner.invoke(
            deploy,
            [
                "-f",
                FULL_CONFIG_PATH,
                "--image-uri",
                "docker.io/user/override-image:latest",
            ],
        )
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-name-from-file",
            image_uri="docker.io/user/override-image:latest",
            compute_config=inline_compute_config,
            working_dir="test-working-dir",
            excludes=["test"],
            requirements=["pip-install-test"],
            query_auth_token_enabled=False,
            http_options={"request_timeout_s": 10.0},
            grpc_options={"grpc_servicer_functions": ["hello.world"]},
            logging_config={"log_level": "DEBUG"},
        )
        assert fake_service_sdk.deployed_config == expected_config

        # Override compute_config.
        result = runner.invoke(
            deploy,
            ["-f", FULL_CONFIG_PATH, "--compute-config", "override-compute-config"],
        )
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-name-from-file",
            image_uri="docker.io/library/test:latest",
            compute_config="override-compute-config",
            working_dir="test-working-dir",
            excludes=["test"],
            requirements=["pip-install-test"],
            query_auth_token_enabled=False,
            http_options={"request_timeout_s": 10.0},
            grpc_options={"grpc_servicer_functions": ["hello.world"]},
            logging_config={"log_level": "DEBUG"},
        )
        assert fake_service_sdk.deployed_config == expected_config

        # Override working_dir.
        result = runner.invoke(
            deploy, ["-f", FULL_CONFIG_PATH, "--working-dir", "override-working-dir"]
        )
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-name-from-file",
            image_uri="docker.io/library/test:latest",
            compute_config=inline_compute_config,
            working_dir="override-working-dir",
            excludes=["test"],
            requirements=["pip-install-test"],
            query_auth_token_enabled=False,
            http_options={"request_timeout_s": 10.0},
            grpc_options={"grpc_servicer_functions": ["hello.world"]},
            logging_config={"log_level": "DEBUG"},
        )
        assert fake_service_sdk.deployed_config == expected_config

        # Override requirements.
        result = runner.invoke(
            deploy,
            ["-f", FULL_CONFIG_PATH, "--requirements", MULTI_LINE_REQUIREMENTS_PATH],
        )
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None

        expected_config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-name-from-file",
            image_uri="docker.io/library/test:latest",
            compute_config=inline_compute_config,
            working_dir="test-working-dir",
            excludes=["test"],
            requirements=MULTI_LINE_REQUIREMENTS_PATH,
            query_auth_token_enabled=False,
            http_options={"request_timeout_s": 10.0},
            grpc_options={"grpc_servicer_functions": ["hello.world"]},
            logging_config={"log_level": "DEBUG"},
        )
        assert fake_service_sdk.deployed_config == expected_config

        # Override environment variables.
        result = runner.invoke(
            deploy,
            [
                "-f",
                FULL_CONFIG_PATH,
                "--env",
                "FOO=BAR_override",
                "--env",
                "FOO2=BAR2",
            ],
        )
        print(result.stdout)
        assert result.exit_code == 0
        assert fake_service_sdk.deployed_config is not None
        expected_config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-name-from-file",
            image_uri="docker.io/library/test:latest",
            compute_config=inline_compute_config,
            working_dir="test-working-dir",
            excludes=["test"],
            requirements=["pip-install-test"],
            query_auth_token_enabled=False,
            http_options={"request_timeout_s": 10.0},
            grpc_options={"grpc_servicer_functions": ["hello.world"]},
            logging_config={"log_level": "DEBUG"},
            env_vars={"FOO": "BAR_override", "FOO2": "BAR2"},
        )
        assert fake_service_sdk.deployed_config == expected_config


class TestStatus:
    def test_no_name(self, fake_service_sdk):
        # Test passing no name (would be picked up as workspace name).
        runner = CliRunner()
        result = runner.invoke(status)
        _assert_error_message(
            result,
            message="Service name must be provided using '--name' or in a config file using '-f'",
        )

    def test_name_and_config_file(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(status, ["-n", "custom-name", "-f", "file-name.yaml"])
        _assert_error_message(
            result, message="Only one of '--name' and '--config-file' can be provided."
        )

    def test_name(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(status, ["-n", "custom-name"])
        assert result.exit_code == 0
        assert fake_service_sdk.fetched_name == "custom-name"

    def test_service_config_file_not_found(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(status, ["-f", "nonexistent.yaml"])
        _assert_error_message(
            result, message="Config file not found at path: 'nonexistent.yaml'."
        )

    def test_empty_config_file(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(status, ["-f", EMPTY_CONFIG_PATH])
        _assert_error_message(
            result,
            message=f"No 'name' property found in config file '{EMPTY_CONFIG_PATH}'.",
        )

    def test_service_config_file_missing_name(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(status, ["-f", MINIMAL_CONFIG_PATH])
        _assert_error_message(
            result,
            message=f"No 'name' property found in config file '{MINIMAL_CONFIG_PATH}'.",
        )

    def test_service_config_file(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(status, ["-f", FULL_CONFIG_PATH])
        assert result.exit_code == 0
        assert fake_service_sdk.fetched_name == "test-name-from-file"

    def test_service_config_file_only_reads_name(self, fake_service_sdk):
        # `status` CLI path should ignore any other fields in the config file aside from `name`.
        runner = CliRunner()
        result = runner.invoke(status, ["-f", NAME_AND_GIBBERISH_CONFIG_PATH])
        assert result.exit_code == 0
        assert fake_service_sdk.fetched_name == "service-name-from-file"

    def test_verbose_flag(self, fake_service_sdk):
        runner = CliRunner()

        # No verbose flag -- exclude details.
        result = runner.invoke(status, ["-n", "custom-name"])
        assert result.exit_code == 0
        assert fake_service_sdk.fetched_name == "custom-name"
        assert "primary_version" in result.stdout
        assert "canary_version" in result.stdout
        assert "query_url" in result.stdout
        assert "query_auth_token" in result.stdout
        assert "config" not in result.stdout
        assert "applications" not in result.stdout

        # Verbose flag -- include details.
        result = runner.invoke(status, ["-n", "custom-name", "-v"])
        assert result.exit_code == 0
        assert fake_service_sdk.fetched_name == "custom-name"
        assert "primary_version" in result.stdout
        assert "canary_version" in result.stdout
        assert "query_url" in result.stdout
        assert "query_auth_token" in result.stdout
        assert "config" in result.stdout
        assert "applications" in result.stdout


class TestWait:
    def test_no_name(self, fake_service_sdk):
        # Test passing no name (would be picked up as workspace name).
        runner = CliRunner()
        result = runner.invoke(wait)
        _assert_error_message(
            result,
            message="Service name must be provided using '--name' or in a config file using '-f'",
        )

    def test_name(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(wait, ["-n", "custom-name"])
        assert result.exit_code == 0
        assert fake_service_sdk.waited_name == "custom-name"

    def test_service_config_file_not_found(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(wait, ["-f", "nonexistent.yaml"])
        _assert_error_message(
            result, message="Config file not found at path: 'nonexistent.yaml'."
        )

    def test_empty_config_file(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(wait, ["-f", EMPTY_CONFIG_PATH])
        _assert_error_message(
            result,
            message=f"No 'name' property found in config file '{EMPTY_CONFIG_PATH}'.",
        )

    def test_service_config_file_missing_name(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(wait, ["-f", MINIMAL_CONFIG_PATH])
        _assert_error_message(
            result,
            message=f"No 'name' property found in config file '{MINIMAL_CONFIG_PATH}'.",
        )

    def test_service_config_file(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(wait, ["-f", FULL_CONFIG_PATH])
        assert result.exit_code == 0
        assert fake_service_sdk.waited_name == "test-name-from-file"

    def test_service_config_file_only_reads_name(self, fake_service_sdk):
        # `wait` CLI path should ignore any other fields in the config file aside from `name`.
        runner = CliRunner()
        result = runner.invoke(wait, ["-f", NAME_AND_GIBBERISH_CONFIG_PATH])
        assert result.exit_code == 0
        assert fake_service_sdk.waited_name == "service-name-from-file"

    def test_state(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(wait, ["-n", "custom-name", "--state", "TERMINATED"])
        assert result.exit_code == 0
        assert fake_service_sdk.waited_name == "custom-name"
        assert fake_service_sdk.waited_state == ServiceState.TERMINATED

    def test_bad_state(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(wait, ["-n", "custom-name", "--state", "FOOBAR"])
        assert result.exit_code == 1
        assert "'FOOBAR' is not a valid ServiceState" in str(result.stdout)

    def test_timeout(self, fake_service_sdk):
        runner = CliRunner()
        result = runner.invoke(wait, ["-n", "custom-name", "--timeout-s=30"])
        assert result.exit_code == 0
        assert fake_service_sdk.waited_timeout_s == 30
