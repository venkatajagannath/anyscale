import re
from typing import List, Optional

import click

from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models import ClusterManagementStackVersions
from anyscale.commands import cloud_commands_util
from anyscale.commands.util import OptionPromptNull
from anyscale.controllers.cloud_controller import CloudController
from anyscale.util import validate_non_negative_arg


log = BlockLogger()  # CLI Logger


@click.group(
    "cloud",
    short_help="Configure cloud provider authentication for Anyscale.",
    help="""Configure cloud provider authentication and setup
to allow Anyscale to launch instances in your account.""",
)
def cloud_cli() -> None:
    pass


@cloud_cli.command(name="delete", help="Delete a cloud.")
@click.argument("cloud-name", required=False)
@click.option("--name", "-n", help="Delete cloud by name.", type=str)
@click.option(
    "--cloud-id",
    "--id",
    help="Cloud id to delete. Alternative to cloud name.",
    required=False,
)
@click.option(
    "--yes", "-y", is_flag=True, default=False, help="Don't ask for confirmation."
)
def cloud_delete(
    cloud_name: Optional[str], name: Optional[str], cloud_id: Optional[str], yes: bool
) -> None:
    if cloud_name and name and cloud_name != name:
        raise click.ClickException(
            "The positional argument CLOUD_NAME and the keyword argument --name "
            "were both provided. Please only provide one of these two arguments."
        )
    CloudController().delete_cloud(
        cloud_name=cloud_name or name, cloud_id=cloud_id, skip_confirmation=yes
    )


@cloud_cli.command(
    name="set-default",
    help=(
        "Sets default cloud for your organization. This operation can only be performed "
        "by organization admins, and the default cloud must have organization level "
        "permissions."
    ),
)
@click.argument("cloud-name", required=False)
@click.option("--name", "-n", help="Set cloud as default by name.", type=str)
@click.option(
    "--cloud-id",
    "--id",
    help="Cloud id to set as default. Alternative to cloud name.",
    required=False,
)
def cloud_set_default(
    cloud_name: Optional[str], name: Optional[str], cloud_id: Optional[str]
) -> None:
    if cloud_name and name and cloud_name != name:
        raise click.ClickException(
            "The positional argument CLOUD_NAME and the keyword argument --name "
            "were both provided. Please only provide one of these two arguments."
        )
    CloudController().set_default_cloud(
        cloud_name=cloud_name or name, cloud_id=cloud_id
    )


@cloud_cli.command(name="setup", help="Set up a cloud provider.")
@click.option(
    "--provider",
    help="The cloud provider type.",
    required=True,
    prompt="Provider",
    type=click.Choice(["aws", "gcp"], case_sensitive=False),
)
@click.option(
    "--region",
    cls=OptionPromptNull,
    help="Region to set up the credentials in.",
    required=True,
    prompt="Region",
    default_option="provider",
    default=lambda p: "us-west-2" if p == "aws" else "us-west1",
    show_default=True,
)
@click.option("--name", "-n", help="Name of the cloud.", required=True, prompt="Name")
@click.option(
    "--project-id",
    help="Globally Unique project ID for GCP clouds (e.g., my-project-abc123)",
    required=False,
    type=str,
)
@click.option(
    "--functional-verify",
    help="Verify the cloud is functional. This will check that the cloud can launch workspace/service.",
    required=False,
    is_flag=False,
    flag_value="workspace",
)
@click.option(
    "--anyscale-managed",
    is_flag=True,
    default=False,
    help="Let anyscale create all the resources.",
)
@click.option(
    "--enable-head-node-fault-tolerance",
    is_flag=True,
    default=False,
    help="Whether to enable head node fault tolerance for services.",
)
@click.option(
    "--yes", "-y", is_flag=True, default=False, help="Skip asking for confirmation."
)
@click.option(
    "--disable-auto-add-user",
    is_flag=True,
    default=False,
    help=(
        "All users in the organization will be added to clouds created "
        "with `anyscale cloud setup` by default. Specify --disable-auto-add-user to "
        "disable this and instead manually grant users permissions to the cloud."
    ),
)
def setup_cloud(  # noqa: PLR0913
    provider: str,
    region: str,
    name: str,
    project_id: str,
    functional_verify: Optional[str],
    anyscale_managed: bool,  # noqa: ARG001
    enable_head_node_fault_tolerance: bool,
    yes: bool,
    disable_auto_add_user: bool,
) -> None:
    # TODO (congding): remove `anyscale_managed` in the future, now keeping it for compatibility
    if provider == "aws":
        CloudController().setup_managed_cloud(
            provider=provider,
            region=region,
            name=name,
            functional_verify=functional_verify,
            cluster_management_stack_version=ClusterManagementStackVersions.V2,
            enable_head_node_fault_tolerance=enable_head_node_fault_tolerance,
            yes=yes,
            auto_add_user=(not disable_auto_add_user),
        )
    elif provider == "gcp":
        if not project_id:
            project_id = click.prompt("GCP Project ID", type=str)
        if project_id[0].isdigit():
            # project ID should start with a letter
            raise click.ClickException(
                "Please provide a valid project ID. Note that project ID is not project number, see https://cloud.google.com/resource-manager/docs/creating-managing-projects#before_you_begin for details."
            )
        CloudController().setup_managed_cloud(
            provider=provider,
            region=region,
            name=name,
            project_id=project_id,
            functional_verify=functional_verify,
            cluster_management_stack_version=ClusterManagementStackVersions.V2,
            enable_head_node_fault_tolerance=enable_head_node_fault_tolerance,
            yes=yes,
            auto_add_user=(not disable_auto_add_user),
        )


@cloud_cli.command(
    name="list", help=("List information about clouds in your Anyscale organization."),
)
@click.option(
    "--name",
    "-n",
    required=False,
    default=None,
    help="Name of cloud to get information about.",
)
@click.option(
    "--cloud-id",
    "--id",
    required=False,
    default=None,
    help=("Id of cloud to get information about."),
)
@click.option(
    "--max-items",
    required=False,
    default=20,
    type=int,
    help="Max items to show in list.",
    callback=validate_non_negative_arg,
)
def list_cloud(name: Optional[str], cloud_id: Optional[str], max_items: int,) -> None:
    print(
        CloudController().list_clouds(
            cloud_name=name, cloud_id=cloud_id, max_items=max_items
        )
    )


@cloud_cli.group("config", help="Manage the configuration for a cloud.")
def cloud_config_group() -> None:
    pass


@cloud_cli.command(
    name="update", help=("Update managed cloud."),
)
@click.argument("cloud-name", required=False)
@click.option(
    "--cloud-id",
    "--id",
    help="Cloud id to update. Alternative to cloud name.",
    required=False,
)
@click.option("--name", "-n", help="Update configuration of cloud by name.", type=str)
@click.option(
    "--yes", "-y", is_flag=True, default=False, help="Skip asking for confirmation."
)
@click.option(
    "--functional-verify",
    help="Verify the cloud is functional. This will check that the cloud can launch workspace/service.",
    required=False,
    is_flag=False,
    flag_value="workspace",
)
@click.option(
    "--enable-head-node-fault-tolerance",
    is_flag=True,
    default=False,
    help="Whether to enable head node fault tolerance for services.",
)
@click.option(
    "--enable-auto-add-user/--disable-auto-add-user",
    default=None,
    help=(
        "If --enable-auto-add-user is specified for a cloud, all users in the organization "
        "will be added to the cloud by default. Note: There may be up to 30 sec delay for all users to be granted "
        "permissions after this feature is enabled.\n\n"
        "Specifying --disable-auto-add-user will require that users "
        "are manually granted permissions to access the cloud. No existing cloud permissions are altered by specifying this flag."
    ),
)
def cloud_update(
    cloud_name: Optional[str],
    name: Optional[str],
    cloud_id: Optional[str],
    functional_verify: Optional[str],
    enable_head_node_fault_tolerance: bool,
    yes: bool,
    enable_auto_add_user: Optional[bool],
) -> None:
    if cloud_name and name and cloud_name != name:
        raise click.ClickException(
            "The positional argument CLOUD_NAME and the keyword argument --name "
            "were both provided. Please only provide one of these two arguments."
        )
    if enable_head_node_fault_tolerance and (enable_auto_add_user is not None):
        raise click.ClickException(
            "Please only specify either --enable-head-node-fault-tolerance or "
            f"{'--enable-auto-add-user' if enable_auto_add_user else '--disable-auto-add-user'} for "
            "this call of `anyscale cloud update`. The other flag can be specified in a separate call "
            "to the command."
        )
    CloudController().update_managed_cloud(
        cloud_name=cloud_name or name,
        cloud_id=cloud_id,
        enable_head_node_fault_tolerance=enable_head_node_fault_tolerance,
        functional_verify=functional_verify,
        yes=yes,
        auto_add_user=enable_auto_add_user,
    )


@cloud_config_group.command("get", help="Get the current configuration for a cloud.")
@click.argument("cloud-name", required=False)
@click.option("--name", "-n", help="Update configuration of cloud by name.", type=str)
@click.option(
    "--cloud-id",
    "--id",
    help="Cloud id to get details about. Alternative to cloud name.",
    required=False,
)
def cloud_config_get(
    cloud_name: Optional[str], name: Optional[str], cloud_id: Optional[str]
) -> None:
    if cloud_name and name and cloud_name != name:
        raise click.ClickException(
            "The positional argument CLOUD_NAME and the keyword argument --name "
            "were both provided. Please only provide one of these two arguments."
        )
    print(
        CloudController().get_cloud_config(
            cloud_name=cloud_name or name, cloud_id=cloud_id,
        )
    )


@cloud_config_group.command(
    "update", help="Update the current configuration for a cloud."
)
@click.argument("cloud-name", required=False)
@click.option("--name", "-n", help="Update configuration of cloud by name.", type=str)
@click.option(
    "--cloud-id",
    "--id",
    help="Cloud id to get details about. Alternative to cloud name.",
    required=False,
)
@click.option(
    "--enable-log-ingestion/--disable-log-ingestion",
    default=None,
    help=(
        "If --enable-log-ingestion is specified for a cloud, it will enable the log "
        "viewing and querying UI features for the clusters on this cloud. This will "
        "enable easier debugging. The logs produced by the clusters will "
        "be sent from the data plane to the control plane. Anyscale does not share "
        "this data with any third party or use it for any purpose other than serving "
        "the log UI for the customer. The log will be stored at most 30 days."
        "Please note by disable this feature again, Anyscale doesn't "
        "delete the logs that have already been ingested. Your clusters may incur "
        "extra data transfer cost from the cloud provider by enabling this feature."
    ),
)
def cloud_config_update(
    cloud_name: Optional[str],
    name: Optional[str],
    cloud_id: Optional[str],
    enable_log_ingestion: Optional[bool],
) -> None:
    if any([enable_log_ingestion is not None]):
        if enable_log_ingestion is True:
            consent_message = click.prompt(
                "--enable-log-ingestion is specified. Please note the logs produced by "
                "your cluster will be ingested into Anyscale's service in region "
                "us-west-2. Your clusters may incur extra data transfer cost from the "
                "cloud provider. If you are sure you want to enable this feature, "
                'please type "consent"',
                type=str,
            )
            if consent_message != "consent":
                raise click.ClickException(
                    'You must type "consent" to enable log ingestion.'
                )
        if enable_log_ingestion is False:
            confirm_response = click.confirm(
                "--disable-log-ingestion is specified. Please note the logs that's "
                "already ingested will not be deleted. Existing clusters will not stop"
                "the log ingestion until you restart them. Logs are automatically "
                "deleted after 30 days from the time of ingestion. Are you sure you "
                "want to disable log ingestion?"
            )
            if not confirm_response:
                raise click.ClickException("You must confirm to disable log ingestion.")

        CloudController().update_cloud_config(
            cloud_name=cloud_name or name,
            cloud_id=cloud_id,
            enable_log_ingestion=enable_log_ingestion,
        )
    else:
        raise click.ClickException(
            "Please provide at least one of the following arguments: --enable-log-ingestion, --disable-log-ingestion."
        )


@cloud_cli.command(
    name="register", help="Register an anyscale cloud with your own resources."
)
@click.option(
    "--provider",
    help="The cloud provider type.",
    required=True,
    type=click.Choice(["aws", "gcp"], case_sensitive=False),
)
@click.option(
    "--region",
    cls=OptionPromptNull,
    help="Region to set up the credentials in.",
    required=True,
    default_option="provider",
    default=lambda p: "us-west-2" if p == "aws" else "us-west1",
    show_default=True,
)
@click.option(
    "--name", "-n", help="Name of the cloud.", required=True,
)
@click.option(
    "--vpc-id", help="The ID of the VPC.", required=False, type=str,
)
@click.option(
    "--subnet-ids",
    help="Comma separated list of subnet ids.",
    required=False,
    type=str,
)
@click.option(
    "--efs-id", help="The EFS ID.", required=False, type=str,
)
@click.option(
    "--anyscale-iam-role-id",
    help="The Anyscale IAM Role ARN.",
    required=False,
    type=str,
)
@click.option(
    "--instance-iam-role-id",
    help="The instance IAM role ARN.",
    required=False,
    type=str,
)
@click.option(
    "--security-group-ids",
    help="IDs of the security groups.",
    required=False,
    type=str,
)
@click.option(
    "--s3-bucket-id", help="S3 bucket ID.", required=False, type=str,
)
@click.option(
    "--memorydb-cluster-id", help="Memorydb cluster ID", required=False, type=str,
)
@click.option(
    "--project-id",
    help="Globally Unique project ID for GCP clouds (e.g., my-project-abc123)",
    required=False,
    type=str,
)
@click.option(
    "--vpc-name", help="VPC name for GCP clouds", required=False, type=str,
)
@click.option(
    "--subnet-names",
    help="Comma separated list of subnet names for GCP clouds",
    required=False,
    type=str,
)
@click.option(
    "--filestore-instance-id",
    help="Filestore instance ID for GCP clouds.",
    required=False,
    type=str,
)
@click.option(
    "--filestore-location",
    help="Filestore location for GCP clouds.",
    required=False,
    type=str,
)
@click.option(
    "--anyscale-service-account-email",
    help="Anyscale service account email for GCP clouds.",
    required=False,
    type=str,
)
@click.option(
    "--instance-service-account-email",
    help="Instance service account email for GCP clouds.",
    required=False,
    type=str,
)
@click.option(
    "--provider-name",
    help="Workload Identity Federation provider name for Anyscale access.",
    required=False,
    type=str,
)
@click.option(
    "--firewall-policy-names",
    help="Filewall policy names for GCP clouds",
    required=False,
    type=str,
)
@click.option(
    "--cloud-storage-bucket-name",
    help="Cloud storage bucket name for GCP clouds",
    required=False,
    type=str,
)
@click.option(
    "--memorystore-instance-name",
    help="Memorystore instance name for GCP clouds",
    required=False,
    type=str,
)
@click.option(
    "--host-project-id",
    help="Host project ID for shared VPC",
    required=False,
    type=str,
)
@click.option(
    "--private-network", help="Use private network.", is_flag=True, default=False,
)
@click.option(
    "--functional-verify",
    help="Verify the cloud is functional. This will check that the cloud can launch workspace/service.",
    required=False,
    is_flag=False,
    flag_value="workspace",
)
@click.option(
    "--yes", "-y", is_flag=True, default=False, help="Skip asking for confirmation."
)
@click.option(
    "--skip-verifications",
    help="Skip verifications. This will skip all verifications.",
    required=False,
    is_flag=True,
    type=bool,
    default=False,
)
@click.option(
    "--enable-auto-add-user",
    is_flag=True,
    default=False,
    help=(
        "If --enable-auto-add-user is specified for a cloud, all users in the organization "
        "will be added to the cloud by default. Otherwise users will need to be manually granted "
        "permissions to the cloud. Note: There may be up to 30 sec delay for all users to be granted "
        "permissions after the cloud is created."
    ),
)
def register_cloud(  # noqa: PLR0913, PLR0912
    provider: str,
    region: str,
    name: str,
    vpc_id: str,
    subnet_ids: str,
    efs_id: str,
    anyscale_iam_role_id: str,
    instance_iam_role_id: str,
    security_group_ids: str,
    s3_bucket_id: str,
    memorydb_cluster_id: str,
    project_id: str,
    vpc_name: str,
    subnet_names: str,
    filestore_instance_id: str,
    filestore_location: str,
    anyscale_service_account_email: str,
    instance_service_account_email: str,
    provider_name: str,
    firewall_policy_names: str,
    cloud_storage_bucket_name: str,
    memorystore_instance_name: str,
    host_project_id: Optional[str],
    functional_verify: Optional[str],
    private_network: bool,
    yes: bool,
    skip_verifications: bool,
    enable_auto_add_user: bool,
) -> None:
    missing_args: List[str] = []
    if provider == "aws":
        # Check for missing required arguments for AWS clouds
        # The only optional argument is `memorydb_cluster_id`
        for resource in [
            (vpc_id, "--vpc-id"),
            (subnet_ids, "--subnet-ids"),
            (efs_id, "--efs-id"),
            (anyscale_iam_role_id, "--anyscale-iam-role-id"),
            (instance_iam_role_id, "--instance-iam-role-id"),
            (security_group_ids, "--security-group-ids"),
            (s3_bucket_id, "--s3-bucket-id"),
        ]:
            if resource[0] is None:
                missing_args.append(resource[1])

        if len(missing_args) > 0:
            raise click.ClickException(f"Please provide a value for {missing_args}")

        CloudController().register_aws_cloud(
            region=region,
            name=name,
            vpc_id=vpc_id,
            subnet_ids=subnet_ids.split(","),
            efs_id=efs_id,
            anyscale_iam_role_id=anyscale_iam_role_id,
            instance_iam_role_id=instance_iam_role_id,
            security_group_ids=security_group_ids.split(","),
            s3_bucket_id=s3_bucket_id,
            memorydb_cluster_id=memorydb_cluster_id,
            functional_verify=functional_verify,
            private_network=private_network,
            cluster_management_stack_version=ClusterManagementStackVersions.V2,
            yes=yes,
            skip_verifications=skip_verifications,
            auto_add_user=enable_auto_add_user,
        )
    elif provider == "gcp":
        # Keep the parameter naming ({resource}_name or {resource}_id) consistent with GCP to reduce confusion for customers
        # Check if all required parameters are provided
        # memorystore_instance_name and host_project_id are optional for GCP clouds
        for resource in [
            (project_id, "--project-id"),
            (vpc_name, "--vpc-name"),
            (subnet_names, "--subnet-names"),
            (filestore_instance_id, "--filestore-instance-id"),
            (filestore_location, "--filestore-location"),
            (anyscale_service_account_email, "--anyscale-service-account-email"),
            (instance_service_account_email, "--instance-service-account-email"),
            (provider_name, "--provider-name"),
            (firewall_policy_names, "--firewall-policy-names"),
            (cloud_storage_bucket_name, "--cloud-storage-bucket-name"),
        ]:
            if resource[0] is None:
                missing_args.append(resource[1])

        if len(missing_args) > 0:
            raise click.ClickException(f"Please provide a value for {missing_args}")

        if project_id[0].isdigit():
            # project ID should start with a letter
            raise click.ClickException(
                "Please provide a valid project ID. Note that project ID is not project number, see https://cloud.google.com/resource-manager/docs/creating-managing-projects#before_you_begin for details."
            )

        if (
            re.search(
                "projects/[0-9]*/locations/global/workloadIdentityPools/.+/providers/.+",
                provider_name,
            )
            is None
        ):
            raise click.ClickException(
                "Please provide a valid, fully qualified provider name. Example: projects/<project number>/locations/global/workloadIdentityPools/<pool name>/providers/<provider id>"
            )

        if (
            memorystore_instance_name is not None
            and not cloud_commands_util.validate_memorystore_instance_name(
                memorystore_instance_name
            )
        ):
            raise click.ClickException(
                "Please provide a valid memorystore instance name. Example: projects/<project number>/locations/<location>/instances/<instance id>"
            )

        if host_project_id is not None and host_project_id[0].isdigit():
            # project ID should start with a letter
            raise click.ClickException(
                "Please provide a valid project ID for `--host-project-id`. Note that project ID is not project number, see https://cloud.google.com/resource-manager/docs/creating-managing-projects#before_you_begin for details."
            )

        CloudController().register_gcp_cloud(
            region=region,
            name=name,
            project_id=project_id,
            vpc_name=vpc_name,
            subnet_names=subnet_names.split(","),
            filestore_instance_id=filestore_instance_id,
            filestore_location=filestore_location,
            anyscale_service_account_email=anyscale_service_account_email,
            instance_service_account_email=instance_service_account_email,
            # TODO (allenyin): use provider_name instead of provider_id everywhere.
            provider_id=provider_name,
            firewall_policy_names=firewall_policy_names.split(","),
            cloud_storage_bucket_name=cloud_storage_bucket_name,
            memorystore_instance_name=memorystore_instance_name,
            host_project_id=host_project_id,
            functional_verify=functional_verify,
            private_network=private_network,
            cluster_management_stack_version=ClusterManagementStackVersions.V2,
            yes=yes,
            skip_verifications=skip_verifications,
            auto_add_user=enable_auto_add_user,
        )
    else:
        raise click.ClickException(
            f"Invalid Cloud provider: {provider}. Available providers are [aws, gcp]."
        )


@cloud_cli.command(name="verify", help="Checks the healthiness of a cloud.")
@click.argument("cloud-name", required=False)
@click.option("--name", "-n", help="Verify cloud by name.", type=str)
@click.option(
    "--cloud-id",
    "--id",
    help="Verify cloud by cloud id, alternative to cloud name.",
    required=False,
)
@click.option(
    "--functional-verify",
    help="Verify the cloud is functional. This will check that the cloud can launch workspace/service.",
    required=False,
    is_flag=False,
    flag_value="workspace",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Strict Verify. Treat warnings as failures.",
)
def cloud_verify(
    cloud_name: Optional[str],
    name: Optional[str],
    cloud_id: Optional[str],
    functional_verify: Optional[str],
    strict: bool = False,
) -> bool:
    if cloud_name and name and cloud_name != name:
        raise click.ClickException(
            "The positional argument CLOUD_NAME and the keyword argument --name "
            "were both provided. Please only provide one of these two arguments."
        )

    return CloudController().verify_cloud(
        cloud_name=cloud_name or name,
        cloud_id=cloud_id,
        functional_verify=functional_verify,
        strict=strict,
    )


@cloud_cli.command(name="edit", help="Edit anyscale cloud resource.")
@click.argument("cloud-name", required=False)
@click.option("--name", "-n", help="Edit cloud by name.", type=str)
@click.option(
    "--cloud-id",
    "--id",
    help="Edit cloud by id, alternative to cloud name.",
    required=False,
)
@click.option(
    "--aws-s3-id", help="New S3 bucket ID.", required=False, type=str,
)
@click.option("--aws-efs-id", help="New EFS ID.", required=False, type=str)
@click.option(
    "--aws-efs-mount-target-ip",
    help="New EFS mount target IP.",
    required=False,
    type=str,
)
@click.option(
    "--memorydb-cluster-id",
    help="New AWS Memorydb cluster ID.",
    required=False,
    type=str,
)
@click.option(
    "--gcp-filestore-instance-id",
    help="New GCP filestore instance id.",
    required=False,
    type=str,
)
@click.option(
    "--gcp-filestore-location",
    help="New GCP filestore location.",
    required=False,
    type=str,
)
@click.option(
    "--gcp-cloud-storage-bucket-name",
    help="New GCP Cloud storage bucket name.",
    required=False,
    type=str,
)
@click.option(
    "--memorystore-instance-name",
    help="New Memorystore instance name for GCP clouds",
    required=False,
    type=str,
)
@click.option(
    "--functional-verify",
    help="Verify the cloud is functional. This will check that the cloud can launch workspace/service.",
    required=False,
    is_flag=False,
    flag_value="workspace",
)
@click.option(
    "--enable-auto-add-user/--disable-auto-add-user",
    default=None,
    help=(
        "If --enable-auto-add-user is specified for a cloud, all users in the organization "
        "will be added to the cloud by default. Note: There may be up to 30 sec delay for all users to be granted "
        "permissions after this feature is enabled.\n\n"
        "Specifying --disable-auto-add-user will require that users "
        "are manually granted permissions to access the cloud. No existing cloud permissions are altered by specifying this flag."
    ),
)
def cloud_edit(  # noqa: PLR0913
    cloud_name: Optional[str],
    name: Optional[str],
    cloud_id: Optional[str],
    aws_s3_id: Optional[str],
    aws_efs_id: Optional[str],
    aws_efs_mount_target_ip: Optional[str],
    memorydb_cluster_id: Optional[str],
    gcp_filestore_instance_id: Optional[str],
    gcp_filestore_location: Optional[str],
    gcp_cloud_storage_bucket_name: Optional[str],
    memorystore_instance_name: Optional[str],
    functional_verify: Optional[str],
    enable_auto_add_user: Optional[bool],
) -> None:
    if cloud_name and name and cloud_name != name:
        raise click.ClickException(
            "The positional argument CLOUD_NAME and the keyword argument --name "
            "were both provided. Please only provide one of these two arguments."
        )
    if any(
        [
            aws_s3_id,
            aws_efs_id,
            aws_efs_mount_target_ip,
            memorydb_cluster_id,
            gcp_filestore_instance_id,
            gcp_filestore_location,
            gcp_cloud_storage_bucket_name,
            memorystore_instance_name,
            enable_auto_add_user is not None,
        ]
    ):
        if any([gcp_filestore_instance_id, gcp_filestore_location]) and not all(
            [gcp_filestore_instance_id, gcp_filestore_location]
        ):
            # Make sure both gcp_filestore_instance_id and gcp_filestore_location are provided if you want to edit filestore.
            raise click.ClickException(
                "Please provide both --gcp-filestore-instance-id and --gcp-filestore-location if you want to edit filestore."
            )
        if (
            memorystore_instance_name is not None
            and not cloud_commands_util.validate_memorystore_instance_name(
                memorystore_instance_name
            )
        ):
            raise click.ClickException(
                "Please provide a valid memorystore instance name. Example: projects/<project number>/locations/<location>/instances/<instance id>"
            )
        CloudController().edit_cloud(
            cloud_name=cloud_name or name,
            cloud_id=cloud_id,
            aws_s3_id=aws_s3_id,
            aws_efs_id=aws_efs_id,
            aws_efs_mount_target_ip=aws_efs_mount_target_ip,
            memorydb_cluster_id=memorydb_cluster_id,
            gcp_filestore_instance_id=gcp_filestore_instance_id,
            gcp_filestore_location=gcp_filestore_location,
            gcp_cloud_storage_bucket_name=gcp_cloud_storage_bucket_name,
            memorystore_instance_name=memorystore_instance_name,
            functional_verify=functional_verify,
            auto_add_user=enable_auto_add_user,
        )
    else:
        raise click.ClickException(
            "Please provide at least one of the following arguments: --aws-s3-id, --aws-efs-id, --aws-efs-mount-target-ip, --memorydb-cluster-id, --gcp-filestore-instance-id, --gcp-filestore-location, --gcp-cloud-storage-bucket-name, --memorystore-instance-name, --enable-auto-add-user, --disable-auto-add-user."
        )
