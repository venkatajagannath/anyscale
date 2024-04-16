from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Union, Any
import json
import yaml

@dataclass
class RayRuntimeEnvConfig:
    working_dir: Optional[str] = None
    py_modules: Optional[List[str]] = field(default_factory=list)
    pip: Optional[List[str]] = field(default_factory=list)
    conda: Optional[Union[Dict[str, Any], str]] = None
    env_vars: Optional[Dict[str, str]] = field(default_factory=dict)
    upload_path: str = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), sort_keys=False)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

# Assuming CreateClusterComputeConfig is defined elsewhere
# from your_module import CreateClusterComputeConfig

@dataclass
class JobConfiguration:
    entrypoint: Optional[str] = ""
    ray_serve_config: Optional[object] = None  # Define or replace as needed
    runtime_env: Optional[RayRuntimeEnvConfig] = None
    build_id: Optional[str] = None
    compute_config_id: Optional[str] = None
    compute_config: Optional[dict] = None  # Adjusted to use CreateClusterComputeConfig
    max_retries: Optional[int] = 5

    def to_dict(self) -> dict:
        # Using a custom approach to include nested data classes
        result = asdict(self)
        if self.runtime_env is not None:
            result['runtime_env'] = self.runtime_env.to_dict()
        return result

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), sort_keys=False)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

