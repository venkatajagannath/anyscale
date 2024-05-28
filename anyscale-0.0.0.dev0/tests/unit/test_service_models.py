from dataclasses import dataclass
import os
import re
from typing import Optional

import pytest

from anyscale.compute_config.models import ComputeConfig, HeadNodeConfig
from anyscale.service.models import (
    RayGCSExternalStorageConfig,
    ServiceConfig,
    ServiceState,
    ServiceStatus,
    ServiceVersionState,
    ServiceVersionStatus,
)


@dataclass
class ServiceConfigFile:
    name: str
    expected_config: Optional[ServiceConfig] = None
    expected_error: Optional[str] = None

    def get_path(self) -> str:
        return os.path.join(
            os.path.dirname(__file__), "test_files/service_config_files", self.name
        )


TEST_CONFIG_FILES = [
    ServiceConfigFile(
        "minimal.yaml",
        expected_config=ServiceConfig(applications=[{"import_path": "main:app"}]),
    ),
    ServiceConfigFile(
        "full.yaml",
        expected_config=ServiceConfig(
            applications=[{"import_path": "main:app"}],
            name="test-name-from-file",
            image_uri="docker.io/library/test:latest",
            compute_config=ComputeConfig(
                cloud="test-cloud", head_node=HeadNodeConfig(instance_type="m5.2xlarge")
            ),
            working_dir="test-working-dir",
            excludes=["test"],
            requirements=["pip-install-test"],
            query_auth_token_enabled=False,
            http_options={"request_timeout_s": 10.0},
            grpc_options={"grpc_servicer_functions": ["hello.world"]},
            logging_config={"log_level": "DEBUG"},
        ),
    ),
    ServiceConfigFile(
        "points_to_requirements_file.yaml",
        expected_config=ServiceConfig(
            applications=[{"import_path": "main:app"}],
            requirements="some_requirements_file.txt",
        ),
    ),
    ServiceConfigFile(
        "unrecognized_option.yaml",
        expected_error=re.escape(
            "__init__() got an unexpected keyword argument 'bad_option'"
        ),
    ),
    ServiceConfigFile(
        "multiple_applications.yaml",
        expected_config=ServiceConfig(
            applications=[
                {
                    "name": "app1",
                    "import_path": "main:app1",
                    "runtime_env": {"env_vars": {"abc": "def"}},
                },
                {
                    "name": "app2",
                    "import_path": "main:app",
                    "args": {"abc": "def", "nested": {"key": "val"}},
                },
            ],
        ),
    ),
]


class TestServiceConfig:
    def test_empty_applications(self):
        with pytest.raises(ValueError, match="'applications' cannot be empty."):
            ServiceConfig()

        with pytest.raises(ValueError, match="'applications' cannot be empty."):
            ServiceConfig(applications=[])

    def test_bad_applications_type(self):
        with pytest.raises(TypeError, match="'applications' must be a list."):
            ServiceConfig(applications={})

    def test_invalid_import_paths(self):
        with pytest.raises(TypeError, match="'import_path' must be a string"):
            ServiceConfig(applications=[{"import_path": 1}])

        with pytest.raises(ValueError, match="'import_path' must be"):
            ServiceConfig(applications=[{"import_path": "hello"}])

        with pytest.raises(ValueError, match="'import_path' must be"):
            ServiceConfig(applications=[{"import_path": "hello."}])

        with pytest.raises(ValueError, match="'import_path' must be"):
            ServiceConfig(applications=[{"import_path": "hello:"}])

        with pytest.raises(ValueError, match="'import_path' must be"):
            ServiceConfig(applications=[{"import_path": ":hello"}])

        with pytest.raises(ValueError, match="'import_path' must be"):
            ServiceConfig(applications=[{"import_path": ".hello"}])

    def test_query_auth_token_enabled(self):
        config = ServiceConfig(applications=[{"import_path": "main:app"}],)
        assert config.query_auth_token_enabled is True

        config = ServiceConfig(applications=[{"import_path": "main:app"}],)
        assert config.query_auth_token_enabled is True

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}], query_auth_token_enabled=False,
        )
        assert config.query_auth_token_enabled is False
        assert config.options().query_auth_token_enabled is False
        assert (
            config.options(query_auth_token_enabled=True).query_auth_token_enabled
            is True
        )

        with pytest.raises(
            TypeError, match="'query_auth_token_enabled' must be a boolean."
        ):
            ServiceConfig(
                applications=[{"import_path": "main:app"}],
                query_auth_token_enabled="foobar",
            )

    def test_http_options(self):
        config = ServiceConfig(applications=[{"import_path": "main:app"}],)
        assert config.http_options is None

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            http_options={"request_timeout_s": 10.0},
        )
        assert config.http_options == {"request_timeout_s": 10.0}

        with pytest.raises(TypeError, match="'http_options' must be a dict."):
            ServiceConfig(
                applications=[{"import_path": "main:app"}],
                http_options=["request_timeout_s"],
            )

        with pytest.raises(
            ValueError,
            match="The following provided 'http_options' are not permitted in Anyscale: {'host'}.",
        ):
            ServiceConfig(
                applications=[{"import_path": "main:app"}],
                http_options={"request_timeout_s": 10.0, "host": "0.0.0.0"},
            )

    def test_grpc_options(self):
        config = ServiceConfig(applications=[{"import_path": "main:app"}],)
        assert config.grpc_options is None

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            grpc_options={"grpc_servicer_functions": ["hello.world"]},
        )
        assert config.grpc_options == {"grpc_servicer_functions": ["hello.world"]}

        with pytest.raises(TypeError, match="'grpc_options' must be a dict."):
            ServiceConfig(
                applications=[{"import_path": "main:app"}],
                grpc_options=["grpc_servicer_functions"],
            )

        with pytest.raises(
            ValueError,
            match="The following provided 'http_options' are not permitted in Anyscale: {'port'}.",
        ):
            ServiceConfig(
                applications=[{"import_path": "main:app"}],
                http_options={"grpc_servicer_functions": ["hello.world"], "port": 9001},
            )

    def test_logging_config(self):
        config = ServiceConfig(applications=[{"import_path": "main:app"}])
        assert config.logging_config is None

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            logging_config={"log_level": "DEBUG"},
        )
        assert config.logging_config == {"log_level": "DEBUG"}

        with pytest.raises(TypeError, match="'logging_config' must be a dict."):
            ServiceConfig(
                applications=[{"import_path": "main:app"}],
                logging_config=["log_level"],
            )

    def test_ray_gcs_external_storage_config(self):
        config = ServiceConfig(applications=[{"import_path": "main:app"}])
        assert config.ray_gcs_external_storage_config is None

        config = ServiceConfig(
            applications=[{"import_path": "main:app"}],
            ray_gcs_external_storage_config=RayGCSExternalStorageConfig(
                address="host:1234"
            ),
        )
        assert config.ray_gcs_external_storage_config == RayGCSExternalStorageConfig(
            address="host:1234"
        )

        with pytest.raises(
            TypeError,
            match="'ray_gcs_external_storage_config' must be a RayGCSExternalStorageConfig.",
        ):
            ServiceConfig(
                applications=[{"import_path": "main:app"}],
                ray_gcs_external_storage_config=["address"],
            )

    def test_options(self):
        config = ServiceConfig(applications=[{"import_path": "main:app"}])

        options = {
            "name": "test-name",
            "image_uri": "docker.io/libaray/test-image:latest",
            "compute_config": "test-compute-config",
            "requirements": ["pip-install-test"],
            "working_dir": ".",
            "excludes": ["some-path"],
            "query_auth_token_enabled": False,
            "http_options": {"request_timeout_s": 10.0},
            "grpc_options": {"grpc_servicer_functions": ["hello.world"]},
            "logging_config": {"log_level": "DEBUG"},
            "ray_gcs_external_storage_config": RayGCSExternalStorageConfig(
                address="host:1234"
            ),
            "env_vars": {"k1": "v1"},
        }

        # Test setting fields one at a time.
        for option, val in options.items():
            assert config.options(**{option: val}) == ServiceConfig(
                applications=[{"import_path": "main:app"}], **{option: val}
            )

            assert config.options(**{option: val}) == ServiceConfig(
                applications=[{"import_path": "main:app"}], **{option: val}
            )

        # Test setting fields all at once.
        assert config.options(**options) == ServiceConfig(
            applications=[{"import_path": "main:app"}], **options
        )

    @pytest.mark.parametrize("config_file", TEST_CONFIG_FILES)
    def test_from_config_file(self, config_file: ServiceConfigFile):
        if config_file.expected_error is not None:
            with pytest.raises(Exception, match=config_file.expected_error):
                ServiceConfig.from_yaml(config_file.get_path())

            return

        assert config_file.expected_config == ServiceConfig.from_yaml(
            config_file.get_path()
        )


class TestServiceStatus:
    @pytest.mark.parametrize(
        "canary_version",
        [
            None,
            ServiceVersionStatus(
                state=ServiceVersionState.STARTING,
                id="test-canary-version",
                weight=0,
                config=ServiceConfig(
                    applications=[
                        {"import_path": "main:app", "args": {"version": "canary"}}
                    ],
                    image_uri="docker.io/library/test-image:latest",
                    compute_config="test-compute-config",
                ),
            ),
        ],
    )
    @pytest.mark.parametrize(
        "primary_version",
        [
            None,
            ServiceVersionStatus(
                state=ServiceVersionState.RUNNING,
                id="test-primary-version",
                weight=100,
                config=ServiceConfig(
                    applications=[
                        {"import_path": "main:app", "args": {"version": "primary"}}
                    ],
                    image_uri="docker.io/library/test-image:latest",
                    compute_config="test-compute-config",
                ),
            ),
        ],
    )
    @pytest.mark.parametrize("query_auth_token", [None, "test_abc123"])
    @pytest.mark.parametrize("state", list(ServiceState))  # type: ignore
    def test_to_dict_and_back(
        self,
        state: ServiceState,
        query_auth_token: Optional[str],
        primary_version: Optional[ServiceVersionStatus],
        canary_version: Optional[ServiceVersionStatus],
    ):
        """Test that all fields can be serialized to and from dictionaries."""
        status = ServiceStatus(
            id="test-service-id",
            name="test-service-name",
            state=state,
            query_url="http://test.com/",
            query_auth_token=query_auth_token,
            primary_version=primary_version,
            canary_version=canary_version,
        )

        assert ServiceStatus.from_dict(status.to_dict()) == status

    @pytest.mark.parametrize("state", list(ServiceVersionState))  # type: ignore
    def test_version_states(self, state: ServiceVersionState):
        assert (
            ServiceVersionStatus(
                id="test-version",
                state=state,
                weight=100,
                config=ServiceConfig(
                    applications=[
                        {"import_path": "main:app", "args": {"version": "primary"}}
                    ],
                ),
            ).state
            == state
        )

    def test_unknown_states(self):
        with pytest.raises(
            ValueError, match="'SOME_FAKE_NEWS_STATE' is not a valid ServiceState"
        ):
            ServiceStatus(
                id="test-service-id",
                name="test-service-name",
                state="SOME_FAKE_NEWS_STATE",
                query_url="http://test.com/",
                query_auth_token=None,
                primary_version=None,
                canary_version=None,
            )

        with pytest.raises(
            ValueError,
            match="'SOME_FAKE_NEWS_STATE' is not a valid ServiceVersionState",
        ):
            ServiceVersionStatus(
                id="test-primary-version",
                state="SOME_FAKE_NEWS_STATE",
                weight=100,
                config=ServiceConfig(
                    applications=[
                        {"import_path": "main:app", "args": {"version": "primary"}}
                    ],
                    image_uri="docker.io/library/test-image:latest",
                    compute_config="test-compute-config",
                ),
            ),
