import json
from typing import Any, Dict, IO, List, Optional, Union

import click
from click import ClickException
import tabulate
import yaml
from yaml.loader import SafeLoader

from anyscale.anyscale_pydantic import (
    BaseModel,
    Field,
    root_validator,
    validator,
)
from anyscale.cli_logger import BlockLogger
from anyscale.cloud import get_cloud_id_and_name
from anyscale.cluster_compute import get_cluster_compute_from_name
from anyscale.conf import IDLE_TIMEOUT_DEFAULT_MINUTES
from anyscale.controllers.base_controller import BaseController
from anyscale.sdk.anyscale_client.models.cluster_compute_config import (
    ClusterComputeConfig,
)
from anyscale.sdk.anyscale_client.models.create_cluster_compute import (
    CreateClusterCompute,
)
from anyscale.sdk.anyscale_client.models.create_cluster_compute_config import (
    CreateClusterComputeConfig,
)
from anyscale.util import get_endpoint
from anyscale.utils.entity_arg_utils import EntityType, IdBasedEntity, NameBasedEntity
from anyscale.utils.name_utils import gen_valid_name


log = BlockLogger()  # Anyscale CLI Logger


class CreateClusterComputeConfigModel(BaseModel):
    """
    Schema for ClusterClusterCompute that is accepted from the CLI. Supports specifying
    `cloud` name instead of `cloud_id`, and preprocesses so fields have the correct
    values to call POST `/ext/v0/cluster_computes`.
    """

    cloud_id: Optional[str] = Field(
        None, description="The ID of the Anyscale cloud to use for launching Clusters.",
    )
    cloud: Optional[str] = Field(
        None,
        description="The name of the Anyscale cloud to use for launching Clusters.",
    )
    max_workers: Optional[int] = Field(
        None, description="Desired limit on total running workers for this Cluster."
    )

    allowed_azs: Optional[List[str]] = Field(
        None,
        description='The availability zones that clusters are allowed to be launched in, e.g. "us-west-2a". If not specified, any AZ may be used.',
    )

    head_node_type: Any = Field(
        ..., description="Node configuration to use for the head node. ",
    )

    worker_node_types: List[Any] = Field(
        ..., description="A list of node types to use for worker nodes. "
    )

    aws: Optional[Any] = Field(
        None,
        description="Fields specific to AWS node types.",
        alias="aws_advanced_configurations_json",
    )

    gcp: Optional[Any] = Field(
        None,
        description="Fields specific to GCP node types.",
        alias="gcp_advanced_configurations_json",
    )

    azure: Optional[Any] = Field(
        None, description="Fields specific to Azure node types.",
    )

    maximum_uptime_minutes: Optional[int] = Field(
        None,
        description="If set to a positive number, Anyscale will terminate the cluster this many minutes after cluster start.",
    )

    idle_termination_minutes: int = Field(
        IDLE_TIMEOUT_DEFAULT_MINUTES,
        description=(
            "If set to a positive number, Anyscale will terminate the cluster this many minutes after the cluster is idle. "
            "Idle time is defined as the time during which a Cluster is not running a user command. "
            "Time spent running commands on Jupyter or ssh is still considered 'idle'. "
            "To disable, set this field to 0."
        ),
        ge=0,
    )

    auto_select_worker_config: Optional[bool] = Field(
        False,
        description="If set to true, worker node groups will automatically be selected based on workload.",
    )

    flags: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="A set of advanced flags that can be used to configure a particular workload.",
    )

    @validator("allowed_azs")
    def check_any_option(cls, v: Optional[List[str]]):
        if not v:
            return v
        if "any" in v and len(v) > 1:
            raise ValueError("Cannot specify 'any' and other AZs.")
        return v

    @root_validator
    def fill_cloud_id(cls: Any, values: Any) -> Any:
        cloud_id, cloud = (
            values.get("cloud_id"),
            values.get("cloud"),
        )
        if cloud_id and cloud:
            raise click.ClickException(
                "Only one of `cloud_id` or `cloud` can be provided in the cluster compute config file. "
            )
        if cloud:
            cloud_id, _ = get_cloud_id_and_name(
                api_client=None, cloud_id=None, cloud_name=cloud
            )
            values["cloud_id"] = cloud_id
        elif not cloud_id:
            raise click.ClickException(
                "Please provide either `cloud_id` or `cloud` in the cluster compute config file. "
            )
        return values

    class Config:
        # This setting will cause pydantic (and fastAPI) to accept the field name as well as the alias
        # (eg. "cpu" or "CPU"). But note that openapi does not respect this setting.
        # Generated models will require the alias.
        allow_population_by_field_name = True


class ComputeConfigController(BaseController):
    """
    This controller powers functionalities related to Anyscale
    cluster compute configuration.
    """

    def __init__(
        self, log: Optional[BlockLogger] = None, initialize_auth_api_client: bool = True
    ):
        if log is None:
            log = BlockLogger()

        super().__init__(initialize_auth_api_client=initialize_auth_api_client)
        self.log = log
        self.log.open_block("Output")

    def create(self, cluster_compute_file: IO[bytes], name: Optional[str]) -> None:
        """Builds a new cluster compute template
        If name is not provided, a default cluster-compute-name will be used and returned in the command output

        Information in output: Link to cluster compute in UI, cluster compute id
        """
        enable_compute_config_versioning = self.api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get(
            "compute-config-versioning"
        ).result.is_on

        if not enable_compute_config_versioning and name and ":" in name:
            log.warning(
                "The compute config's name contains colons (`:`). "
                "Colons will be a reserved character after 04/01/2024, "
                "and before then, we are discouraging using colons in the name of compute configs. "
                "Also, all existing colons will be replaced by hyphens at 04/01/2024 "
                "as the versioning feature is enabled."
            )

        try:
            cluster_compute: Dict[str, Any] = yaml.load(
                cluster_compute_file, Loader=SafeLoader
            )
        except Exception as e:  # noqa: BLE001
            raise ClickException(f"Could not load compute config file: {e}")

        cluster_compute_config_model = CreateClusterComputeConfigModel(
            **cluster_compute
        )
        if cluster_compute_config_model.max_workers is not None:
            log.warning(
                "Warning: global `max_workers` is deprecated for Anyscale Ray 2.7+. Please use global resource max instead: https://docs.anyscale.com/configure/compute-configs/global-resource-min-max"
            )
        cluster_compute_config = CreateClusterComputeConfig(
            cloud_id=cluster_compute_config_model.cloud_id,
            max_workers=cluster_compute_config_model.max_workers,
            allowed_azs=cluster_compute_config_model.allowed_azs,
            region=None,
            head_node_type=cluster_compute_config_model.head_node_type,
            worker_node_types=cluster_compute_config_model.worker_node_types,
            aws_advanced_configurations_json=cluster_compute_config_model.aws,
            gcp_advanced_configurations_json=cluster_compute_config_model.gcp,
            maximum_uptime_minutes=cluster_compute_config_model.maximum_uptime_minutes,
            idle_termination_minutes=cluster_compute_config_model.idle_termination_minutes,
            auto_select_worker_config=cluster_compute_config_model.auto_select_worker_config,
            flags=cluster_compute_config_model.flags,
        )
        if name is None:
            name = gen_valid_name("cli-config")

        cluster_compute_response = self.anyscale_api_client.create_cluster_compute(
            CreateClusterCompute(
                name=name,
                config=cluster_compute_config,
                new_version=enable_compute_config_versioning,
            )
        )
        created_cluster_compute = cluster_compute_response.result
        cluster_compute_id = created_cluster_compute.id
        cluster_compute_name = created_cluster_compute.name
        cluster_compute_version = created_cluster_compute.version
        url = get_endpoint(f"/configurations/cluster-computes/{cluster_compute_id}")
        if enable_compute_config_versioning and cluster_compute_version > 1:
            log.info(f"A new version of {cluster_compute_name} was created.")
        else:
            log.info("A new compute config was created.")

        log.info(f"View this compute config at: {url}.")
        log.info(f"Compute config id: {cluster_compute_id}.")
        log.info(f"Compute config name: {cluster_compute_name}.")
        if enable_compute_config_versioning:
            log.info(f"Compute config version: {cluster_compute_version}.")

    def archive(
        self, compute_config_entity: Union[IdBasedEntity, NameBasedEntity]
    ) -> None:
        """
        Archives the cluster compute with the given name or id.
        Exactly one of cluster_compute_name or id must be provided.
        """
        if compute_config_entity.type is EntityType.ID:
            compute_config = self.anyscale_api_client.get_compute_template(
                compute_config_entity.id
            ).result
            compute_config_id = compute_config_entity.id
            compute_config_name = compute_config.name
        else:
            compute_config = get_cluster_compute_from_name(
                compute_config_entity.name, self.api_client,
            )
            compute_config_id = compute_config.id
            compute_config_name = compute_config.name
        self.api_client.archive_compute_template_api_v2_compute_templates_compute_template_id_archive_post(
            compute_config_id
        )
        log.info(f"Successfully archived compute config: {compute_config_name}.")

    def list(
        self,
        cluster_compute_name: Optional[str],
        cluster_compute_id: Optional[str],
        include_shared: bool,
        max_items: int,
    ) -> None:
        cluster_compute_list = []
        if cluster_compute_id:
            cluster_compute_list = [
                self.anyscale_api_client.get_cluster_compute(cluster_compute_id).result
            ]
        elif cluster_compute_name:
            cluster_compute_list = self.anyscale_api_client.search_cluster_computes(
                {"name": {"equals": cluster_compute_name}, "paging": {"count": 1}}
            ).results
        else:
            creator_id = (
                self.api_client.get_user_info_api_v2_userinfo_get().result.id
                if not include_shared
                else None
            )
            resp = self.anyscale_api_client.search_cluster_computes(
                {"creator_id": creator_id, "paging": {"count": 20}}
            )
            cluster_compute_list.extend(resp.results)
            paging_token = resp.metadata.next_paging_token
            has_more = (paging_token is not None) and (
                len(cluster_compute_list) < max_items
            )
            while has_more:
                resp = self.anyscale_api_client.search_cluster_computes(
                    {
                        "creator_id": creator_id,
                        "paging": {"count": 20, "paging_token": paging_token},
                    }
                )
                cluster_compute_list.extend(resp.results)
                paging_token = resp.metadata.next_paging_token
                has_more = (paging_token is not None) and (
                    len(cluster_compute_list) < max_items
                )
            cluster_compute_list = cluster_compute_list[:max_items]

        cluster_compute_table = [
            [
                cluster_compute.id,
                cluster_compute.name,
                self.anyscale_api_client.get_cloud(
                    cluster_compute.config.cloud_id
                ).result.name
                if cluster_compute.config.cloud_id
                else None,
                cluster_compute.last_modified_at.strftime("%m/%d/%Y, %H:%M:%S"),
                get_endpoint(f"configurations/cluster-computes/{cluster_compute.id}"),
            ]
            for cluster_compute in cluster_compute_list
        ]

        table = tabulate.tabulate(
            cluster_compute_table,
            headers=["ID", "NAME", "CLOUD", "LAST MODIFIED AT", "URL"],
            tablefmt="plain",
        )
        print(f"Compute configs:\n{table}")

    def get(
        self,
        cluster_compute_name: Optional[str],
        cluster_compute_id: Optional[str],
        include_archived: Optional[bool] = False,
    ) -> None:
        if (
            int(cluster_compute_name is not None) + int(cluster_compute_id is not None)
            != 1
        ):
            raise click.ClickException(
                "Please only provide one of `compute-config-name` or `--id`."
            )
        if cluster_compute_name:
            cluster_compute_id = get_cluster_compute_from_name(
                cluster_compute_name, self.api_client, include_archived=include_archived
            ).id
        compute_config: ClusterComputeConfig = self.anyscale_api_client.get_cluster_compute(
            cluster_compute_id
        ).result.config

        compute_config_dict = {
            key: val for key, val in compute_config.to_dict().items() if val is not None
        }
        formatted_config_json = json.dumps(compute_config_dict, indent=2)
        print(formatted_config_json)
