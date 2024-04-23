import json
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Any
from enum import Enum

class RolloutStrategy(Enum):
    ROLLOUT = 'ROLLOUT'
    IN_PLACE = 'IN_PLACE'

@dataclass
class HttpProtocolConfig:
    enabled: bool = True
    port: int = 8000

@dataclass
class GrpcProtocolConfig:
    enabled: bool = False
    port: int = 9000
    service_names: List[str] = field(default_factory=list)

@dataclass
class Protocols:
    http: Optional[HttpProtocolConfig] = None
    grpc: Optional[GrpcProtocolConfig] = None

@dataclass
class AccessConfig:
    use_bearer_token: bool = True

@dataclass
class ServiceConfig:
    max_uptime_timeout_sec: Optional[int] = 0
    access: Optional[AccessConfig] = None
    protocols: Optional[Protocols] = None

@dataclass
class RayGCSExternalStorageConfig:
    address: Optional[str] = None
    redis_certificate_path: str = "/etc/ssl/certs/ca-certificates.crt"
    enable: bool = True

@dataclass
class ApplyServiceModel:
    name: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[str] = None
    version: Optional[str] = None
    canary_percent: Optional[int] = None
    ray_serve_config: Optional[Any] = None
    build_id: Optional[str] = None
    compute_config_id: Optional[str] = None
    config: Optional[ServiceConfig] = None
    rollout_strategy: Optional[RolloutStrategy] = None
    ray_gcs_external_storage_config: Optional[RayGCSExternalStorageConfig] = None
    auto_complete_rollout: bool = True
    max_surge_percent: Optional[int] = None

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.value if isinstance(o, Enum) else o.__dict__)

