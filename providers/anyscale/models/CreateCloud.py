from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class CloudProviders(Enum):
    AWS = "AWS"
    GCP = "GCP"
    CLOUDGATEWAY = "CLOUDGATEWAY"
    PCP = "PCP"

class ClusterManagementStackVersions(Enum):
    V1 = "v1"
    V2 = "v2"
    # Define versions as needed

@dataclass
class CloudConfig:
    max_stopped_instances: int = 0
    vpc_peering_ip_range: Optional[str] = None
    vpc_peering_target_project_id: Optional[str] = None
    vpc_peering_target_vpc_id: Optional[str] = None

@dataclass
class CreateCloud:
    name: Optional[str] = None
    provider: Optional[CloudProviders] = None
    region: Optional[str] = None
    credentials: Optional[str] = None
    config: Optional[CloudConfig] = None
    is_k8s: bool = False
    is_aioa: bool = False
    availability_zones: Optional[List[str]] = field(default_factory=list)
    is_bring_your_own_resource: Optional[bool] = None
    is_private_cloud: bool = False
    cluster_management_stack_version: Optional[ClusterManagementStackVersions] = None
    is_private_service_cloud: Optional[bool] = None
    auto_add_user: bool = False
