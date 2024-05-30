import re

import pytest

from anyscale._private.workload import WorkloadConfig
from anyscale.compute_config.models import ComputeConfig


class TestWorkloadConfig:
    def test_name(self):
        config = WorkloadConfig()
        assert config.name is None

        config = WorkloadConfig(name="my-custom-name")
        assert config.name == "my-custom-name"

        with pytest.raises(TypeError, match="'name' must be a string"):
            WorkloadConfig(name=123)

    def test_image_uri(self):
        config = WorkloadConfig()
        assert config.image_uri is None

        config = WorkloadConfig(image_uri="user/my-custom-image:1")
        assert config.image_uri == "user/my-custom-image:1"

    def test_compute_config(self):
        config = WorkloadConfig()
        assert config.compute_config is None

        config = WorkloadConfig(compute_config="my-custom-compute_config")
        assert config.compute_config == "my-custom-compute_config"

        config = WorkloadConfig(
            compute_config={"cloud": "cloud1", "zones": ["az1", "az2"]}
        )
        assert config.compute_config == ComputeConfig(
            cloud="cloud1", zones=["az1", "az2"]
        )

        config = WorkloadConfig(
            compute_config=ComputeConfig(cloud="cloud2", zones=["az1", "az2"])
        )
        assert config.compute_config == ComputeConfig(
            cloud="cloud2", zones=["az1", "az2"]
        )

        with pytest.raises(
            TypeError,
            match="'compute_config' must be a string, ComputeConfig, or corresponding dict",
        ):
            WorkloadConfig(compute_config=123)

    def test_options(self):
        config = WorkloadConfig()

        options = {
            "name": "test-name",
            "image_uri": "docker.io/libaray/test-image:latest",
            "compute_config": "test-compute-config",
            "excludes": ["some-path"],
        }

        # Test setting fields one at a time.
        for option, val in options.items():
            assert config.options(**{option: val}) == WorkloadConfig(**{option: val})

        # Test setting fields all at once.
        assert config.options(**options) == WorkloadConfig(**options)

    def test_invalid_requirements(self):
        WorkloadConfig(requirements="test")
        WorkloadConfig(requirements=["test"])

        with pytest.raises(
            TypeError,
            match=re.escape(
                "'requirements' must be a string (file path) or list of strings."
            ),
        ):
            WorkloadConfig(requirements=1)

        with pytest.raises(
            TypeError,
            match=re.escape(
                "'requirements' must be a string (file path) or list of strings."
            ),
        ):
            WorkloadConfig(requirements=[1])

    def test_invalid_working_dir(self):
        WorkloadConfig(working_dir="test")
        with pytest.raises(TypeError, match="'working_dir' must be a string."):
            WorkloadConfig(working_dir=1)

        with pytest.raises(TypeError, match="'excludes' must be a list of strings."):
            WorkloadConfig(excludes="test")

        with pytest.raises(TypeError, match="'excludes' must be a list of strings."):
            WorkloadConfig(excludes=["test", 1])

    def test_invalid_excludes(self):
        WorkloadConfig(excludes=["test"])
        with pytest.raises(TypeError, match="'excludes' must be a list of strings."):
            WorkloadConfig(excludes="test")

        with pytest.raises(TypeError, match="'excludes' must be a list of strings."):
            WorkloadConfig(excludes=["test", 1])

    def test_invalid_env_vars(self):
        WorkloadConfig(env_vars={"test": "test"})
        with pytest.raises(
            TypeError, match=re.escape("'env_vars' must be a Dict[str, str]."),
        ):
            WorkloadConfig(env_vars={"test": 1})
