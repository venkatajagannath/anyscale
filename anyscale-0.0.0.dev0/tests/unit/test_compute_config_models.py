from dataclasses import dataclass
import os
import re
from typing import Optional

import pytest

from anyscale.compute_config.models import (
    ComputeConfig,
    ComputeConfigVersion,
    HeadNodeConfig,
    MarketType,
    WorkerNodeGroupConfig,
)


@dataclass
class ComputeConfigFile:
    name: str
    expected_config: Optional[ComputeConfig] = None
    expected_error: Optional[str] = None

    def get_path(self) -> str:
        return os.path.join(
            os.path.dirname(__file__), "test_files/compute_config_files", self.name
        )


TEST_CONFIG_FILES = [
    ComputeConfigFile(
        "minimal.yaml", expected_config=ComputeConfig(cloud="test-cloud-from-file"),
    ),
    ComputeConfigFile(
        "full.yaml",
        expected_config=ComputeConfig(
            cloud="test-cloud-from-file",
            zones=["zone1", "zone2"],
            enable_cross_zone_scaling=True,
            max_resources={"CPU": 10, "GPU": 1},
            head_node=HeadNodeConfig(
                instance_type="head-node-instance-type",
                resources={"CPU": 1},
                advanced_instance_config={"head": "config"},
            ),
            worker_nodes=[
                WorkerNodeGroupConfig(
                    name="worker-group-1",
                    instance_type="worker-group-1-instance-type",
                    resources={"CPU": 2},
                    min_nodes=2,
                    max_nodes=4,
                    market_type=MarketType.SPOT,
                    advanced_instance_config={"worker1": "config"},
                ),
                WorkerNodeGroupConfig(
                    name="worker-group-2",
                    instance_type="worker-group-2-instance-type",
                    resources={"GPU": 1, "CPU": 1},
                    min_nodes=0,
                    max_nodes=1,
                    market_type=MarketType.PREFER_SPOT,
                    advanced_instance_config={"worker2": "config"},
                ),
            ],
        ),
    ),
]


class TestHeadNodeConfig:
    def test_empty(self):
        with pytest.raises(
            TypeError,
            match=re.escape(
                "__init__() missing 1 required positional argument: 'instance_type'"
            ),
        ):
            HeadNodeConfig()

    def test_invalid_instance_type(self):
        with pytest.raises(TypeError, match="'instance_type' must be a string"):
            HeadNodeConfig(instance_type=123)

    def test_invalid_resources(self):
        with pytest.raises(
            TypeError, match=re.escape("'resources' must be a Dict[str, float]")
        ):
            HeadNodeConfig(instance_type="m5.2xlarge", resources=["CPU", "GPU"])

        with pytest.raises(TypeError, match="'resources' values must be floats"):
            HeadNodeConfig(instance_type="m5.2xlarge", resources={"CPU": "123"})

        with pytest.raises(TypeError, match="'resources' keys must be strings"):
            HeadNodeConfig(instance_type="m5.2xlarge", resources={123: 1})

    def test_invalid_advanced_instance_config(self):
        with pytest.raises(
            TypeError,
            match=re.escape("'advanced_instance_config' must be a Dict[str, Any]"),
        ):
            HeadNodeConfig(
                instance_type="m5.2xlarge", advanced_instance_config=["foobar"]
            )

    def test_options(self):
        config = HeadNodeConfig(instance_type="m5.2xlarge")

        options = {
            "resources": {"CPU": 1},
            "advanced_instance_config": {"foo": 123},
        }

        # Test setting fields one at a time.
        for option, val in options.items():
            assert config.options(**{option: val}) == HeadNodeConfig(
                instance_type="m5.2xlarge", **{option: val}
            )

        # Test setting fields all at once.
        assert config.options(**options) == HeadNodeConfig(
            instance_type="m5.2xlarge", **options
        )


class TestWorkerNodeGroupConfig:
    def test_empty(self):
        with pytest.raises(
            TypeError,
            match=re.escape(
                "__init__() missing 1 required positional argument: 'instance_type'"
            ),
        ):
            WorkerNodeGroupConfig()

    def test_invalid_instance_type(self):
        with pytest.raises(TypeError, match="'instance_type' must be a string"):
            WorkerNodeGroupConfig(instance_type=123)

    def test_market_type(self):
        for valid_market_type in list(MarketType):
            assert (
                WorkerNodeGroupConfig(
                    instance_type="m5.2xlarge", market_type=valid_market_type
                ).market_type
                == valid_market_type
            )
            assert (
                WorkerNodeGroupConfig(
                    instance_type="m5.2xlarge", market_type=str(valid_market_type)
                ).market_type
                == valid_market_type
            )

        with pytest.raises(
            ValueError, match="'DOES_NOT_EXIST' is not a valid MarketType"
        ):
            WorkerNodeGroupConfig(
                instance_type="m5.2xlarge", market_type="DOES_NOT_EXIST"
            )

    def test_name_defaults_to_instance_type(self):
        assert WorkerNodeGroupConfig(instance_type="m5.2xlarge").name == "m5.2xlarge"
        assert (
            WorkerNodeGroupConfig(instance_type="m5.2xlarge", name="foobar").name
            == "foobar"
        )

    def test_invalid_name(self):
        with pytest.raises(TypeError, match="'name' must be a string"):
            WorkerNodeGroupConfig(instance_type="m5.2xlarge", name=123)

        with pytest.raises(ValueError, match="'name' cannot be empty"):
            WorkerNodeGroupConfig(instance_type="m5.2xlarge", name="")

    def test_invalid_min_nodes(self):
        WorkerNodeGroupConfig(instance_type="m5.2xlarge", min_nodes=0)
        with pytest.raises(TypeError, match="'min_nodes' must be an int"):
            WorkerNodeGroupConfig(instance_type="m5.2xlarge", min_nodes="foobar")

        with pytest.raises(TypeError, match="'min_nodes' must be an int"):
            WorkerNodeGroupConfig(instance_type="m5.2xlarge", min_nodes=1.5)

        with pytest.raises(ValueError, match="'min_nodes' must be >= 0"):
            WorkerNodeGroupConfig(instance_type="m5.2xlarge", min_nodes=-1)

    def test_invalid_max_nodes(self):
        WorkerNodeGroupConfig(instance_type="m5.2xlarge", max_nodes=1)

        with pytest.raises(TypeError, match="'max_nodes' must be an int"):
            WorkerNodeGroupConfig(instance_type="m5.2xlarge", max_nodes="foobar")

        with pytest.raises(TypeError, match="'max_nodes' must be an int"):
            WorkerNodeGroupConfig(instance_type="m5.2xlarge", max_nodes=1.5)

        with pytest.raises(ValueError, match="'max_nodes' must be >= 1"):
            WorkerNodeGroupConfig(instance_type="m5.2xlarge", max_nodes=0)

        with pytest.raises(
            ValueError, match=re.escape("'max_nodes' must be >= 'min_nodes' (2)")
        ):
            WorkerNodeGroupConfig(instance_type="m5.2xlarge", min_nodes=2, max_nodes=1)

    def test_invalid_resources(self):
        with pytest.raises(
            TypeError, match=re.escape("'resources' must be a Dict[str, float]")
        ):
            WorkerNodeGroupConfig(instance_type="m5.2xlarge", resources=["CPU", "GPU"])

        with pytest.raises(TypeError, match="'resources' values must be floats"):
            WorkerNodeGroupConfig(instance_type="m5.2xlarge", resources={"CPU": "123"})

        with pytest.raises(TypeError, match="'resources' keys must be strings"):
            WorkerNodeGroupConfig(instance_type="m5.2xlarge", resources={123: 1})

    def test_invalid_advanced_instance_config(self):
        with pytest.raises(
            TypeError,
            match=re.escape("'advanced_instance_config' must be a Dict[str, Any]"),
        ):
            WorkerNodeGroupConfig(
                instance_type="m5.2xlarge", advanced_instance_config=["foobar"]
            )

    def test_options(self):
        config = WorkerNodeGroupConfig(instance_type="m5.2xlarge")

        options = {
            "name": "foobar",
            "resources": {"CPU": 1},
            "advanced_instance_config": {"foo": 123},
            "min_nodes": 5,
            "max_nodes": 500,
        }

        # Test setting fields one at a time.
        for option, val in options.items():
            assert config.options(**{option: val}) == WorkerNodeGroupConfig(
                instance_type="m5.2xlarge", **{option: val}
            )

        # Test setting fields all at once.
        assert config.options(**options) == WorkerNodeGroupConfig(
            instance_type="m5.2xlarge", **options
        )


class TestComputeConfig:
    def test_empty(self):
        ComputeConfig()

    def test_invalid_cloud(self):
        ComputeConfig(cloud="test-cloud")

        with pytest.raises(TypeError, match="'cloud' must be a string"):
            ComputeConfig(cloud=123)

    def test_invalid_zones(self):
        ComputeConfig(zones=["us-west-2a", "us-west-2b"])

        with pytest.raises(TypeError, match=re.escape("'zones' must be a List[str]")):
            ComputeConfig(zones={"hi"})

        with pytest.raises(TypeError, match=re.escape("'zones' must be a List[str]")):
            ComputeConfig(zones=["hi", 123])

        with pytest.raises(
            ValueError, match=re.escape("'zones' must not be an empty list")
        ):
            ComputeConfig(zones=[])

    def test_enable_cross_zone_scaling(self):
        assert ComputeConfig().enable_cross_zone_scaling is False
        assert (
            ComputeConfig(enable_cross_zone_scaling=False).enable_cross_zone_scaling
            is False
        )
        assert (
            ComputeConfig(enable_cross_zone_scaling=True).enable_cross_zone_scaling
            is True
        )

        with pytest.raises(
            TypeError, match="'enable_cross_zone_scaling' must be a boolean"
        ):
            ComputeConfig(enable_cross_zone_scaling="True")

    def test_invalid_advanced_instance_config(self):
        with pytest.raises(
            TypeError,
            match=re.escape("'advanced_instance_config' must be a Dict[str, Any]"),
        ):
            ComputeConfig(advanced_instance_config=["foobar"])

    def test_invalid_max_resources(self):
        with pytest.raises(
            TypeError, match=re.escape("'max_resources' must be a Dict[str, float]")
        ):
            ComputeConfig(max_resources=["CPU", "GPU"])

        with pytest.raises(TypeError, match="'max_resources' values must be floats"):
            ComputeConfig(max_resources={"CPU": "123"})

        with pytest.raises(
            ValueError,
            match="Only 'CPU' and 'GPU' are currently supported in 'max_resources', but got: {'custom'}",
        ):
            ComputeConfig(max_resources={"custom": 1})

    def test_invalid_head_node(self):
        ComputeConfig(head_node=HeadNodeConfig(instance_type="m5.2xlarge"))

        with pytest.raises(
            TypeError,
            match=re.escape(
                "'head_node' must be a HeadNodeConfig or corresponding dict"
            ),
        ):
            ComputeConfig(head_node=[123])

    def test_head_node_as_dict(self):
        assert ComputeConfig(
            head_node={"instance_type": "m5.2xlarge"}
        ).head_node == HeadNodeConfig(instance_type="m5.2xlarge")

    def test_invalid_worker_nodes(self):
        ComputeConfig(
            worker_nodes=[
                WorkerNodeGroupConfig(instance_type="m5.2xlarge"),
                WorkerNodeGroupConfig(instance_type="m5.4xlarge"),
            ]
        )

        with pytest.raises(
            TypeError,
            match=re.escape(
                "'worker_nodes' must be a list of WorkerNodeGroupConfigs or corresponding dicts"
            ),
        ):
            ComputeConfig(
                worker_nodes=[WorkerNodeGroupConfig(instance_type="m5.2xlarge"), 123]
            )

        with pytest.raises(
            TypeError,
            match=re.escape(
                "'worker_nodes' must be a list of WorkerNodeGroupConfigs or corresponding dicts"
            ),
        ):
            ComputeConfig(
                worker_nodes=[
                    WorkerNodeGroupConfig(instance_type="m5.2xlarge"),
                    HeadNodeConfig,
                ]
            )

    def test_worker_nodes_duplicate_names(self):
        with pytest.raises(
            ValueError,
            match="'worker_nodes' names must be unique, but got duplicate names: {'m5.2xlarge'}",
        ):
            ComputeConfig(
                worker_nodes=[
                    WorkerNodeGroupConfig(instance_type="m5.2xlarge"),
                    WorkerNodeGroupConfig(instance_type="m5.2xlarge"),
                ]
            )

        with pytest.raises(
            ValueError,
            match="'worker_nodes' names must be unique, but got duplicate names: {'foobar'}",
        ):
            ComputeConfig(
                worker_nodes=[
                    WorkerNodeGroupConfig(instance_type="m5.2xlarge", name="foobar"),
                    WorkerNodeGroupConfig(instance_type="m5.2xlarge", name="foobar"),
                ]
            )

        ComputeConfig(
            worker_nodes=[
                WorkerNodeGroupConfig(instance_type="m5.2xlarge"),
                WorkerNodeGroupConfig(instance_type="m5.2xlarge", name="foobar"),
            ]
        )

    def test_worker_nodes_as_dicts(self):
        assert ComputeConfig(
            worker_nodes=[
                {"instance_type": "m5.2xlarge"},
                {"instance_type": "m5.4xlarge"},
                WorkerNodeGroupConfig(instance_type="m5.8xlarge"),
            ]
        ).worker_nodes == [
            WorkerNodeGroupConfig(instance_type="m5.2xlarge"),
            WorkerNodeGroupConfig(instance_type="m5.4xlarge"),
            WorkerNodeGroupConfig(instance_type="m5.8xlarge"),
        ]

    @pytest.mark.parametrize("config_file", TEST_CONFIG_FILES)
    def test_from_config_file(self, config_file: ComputeConfigFile):
        if config_file.expected_error is not None:
            with pytest.raises(Exception, match=config_file.expected_error):
                ComputeConfig.from_yaml(config_file.get_path())

            return

        assert config_file.expected_config == ComputeConfig.from_yaml(
            config_file.get_path()
        )


class TestComputeConfigVersion:
    def test_missing_fields(self):
        with pytest.raises(TypeError, match="missing 3 required positional arguments"):
            ComputeConfigVersion()

        with pytest.raises(TypeError, match="missing 2 required positional arguments"):
            ComputeConfigVersion(name="foobar")

        with pytest.raises(TypeError, match="missing 1 required positional argument"):
            ComputeConfigVersion(name="foobar", id="barbaz")

    def test_must_have_version_tag(self):
        with pytest.raises(
            ValueError, match="'name' must be in the format: '<name>:<version>'"
        ):
            ComputeConfigVersion(
                name="test-name-no-version", id="test-id", config=ComputeConfig(),
            )

    def test_basic(self):
        ComputeConfigVersion(
            name="test-name:1", id="test-id", config=ComputeConfig(),
        )
