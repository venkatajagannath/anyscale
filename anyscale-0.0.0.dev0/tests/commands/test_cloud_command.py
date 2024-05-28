from unittest import mock
from unittest.mock import Mock, patch

from click.testing import CliRunner
import pytest

from anyscale.client.openapi_client.models import ClusterManagementStackVersions
from anyscale.commands.cloud_commands import (
    cloud_config_update,
    register_cloud,
    setup_cloud,
)


@pytest.mark.parametrize("enable_head_node_fault_tolerance", [True, False])
@pytest.mark.parametrize("yes", [True, False])
def test_cloud_setup(enable_head_node_fault_tolerance, yes):
    runner = CliRunner()
    mock_cloud_controller = Mock()
    mock_setup_managed_cloud = Mock()
    mock_cloud_controller().setup_managed_cloud = mock_setup_managed_cloud

    provider = "aws"
    region = "us-west-2"
    name = "unit-test-cloud"

    args = ["--provider", provider, "--name", name, "--region", region]
    if yes:
        args.append("--yes")

    if enable_head_node_fault_tolerance:
        args.append("--enable-head-node-fault-tolerance")

    with patch(
        "anyscale.commands.cloud_commands.CloudController", new=mock_cloud_controller,
    ):
        runner.invoke(setup_cloud, args=args)

    mock_setup_managed_cloud.assert_called_once_with(
        provider=provider,
        region=region,
        name=name,
        functional_verify=None,
        cluster_management_stack_version=ClusterManagementStackVersions.V2,
        enable_head_node_fault_tolerance=enable_head_node_fault_tolerance,
        yes=yes,
        auto_add_user=True,
    )


@pytest.mark.parametrize(
    (("enable_head_node_fault_tolerance", "correct_memorystore_name")),
    [pytest.param(True, False), pytest.param(True, True), pytest.param(False, True)],
)
@pytest.mark.parametrize("host_project_id", [None, "host-project-id"])
def test_cloud_register(
    enable_head_node_fault_tolerance, correct_memorystore_name, caplog, host_project_id
):
    runner = CliRunner()
    mock_cloud_controller = Mock()
    mock_register_cloud = Mock()
    mock_cloud_controller().register_gcp_cloud = mock_register_cloud

    provider = "gcp"
    region = "us-west2"
    name = "unit-test-cloud"
    project_id = "mock_project_id"
    vpc_name = "vpc-cld-advbe8prrhdxx7cgnrgimtp8f4"
    subnet_names = "subnet-cld-advbe8prrhdxx7cgnrgimtp8f4"
    firewall_policy_names = "firewall-policy-cld-advbe8prrhdxx7cgnrgimtp8f4"
    cloud_storage_bucket_name = "storage-bucket-cld-advbe8prrhdxx7cgnrgimtp8f4"
    filestore_instance_id = "filestore-cld-advbe8prrhdxx7cgnrgimtp8f4"
    filestore_location = "us-west1-b"
    anyscale_service_account_email = (
        "anyscale-access-b11959be@allen-dev-396002.iam.gserviceaccount.com"
    )
    instance_service_account_email = (
        "cld-advbe8prrhdxx7cgnrgimtp8f4@allen-dev-396002.iam.gserviceaccount.com"
    )
    provider_name = "projects/604561082599/locations/global/workloadIdentityPools/anyscale-provider-pool-b11959be/providers/anyscale-access"
    if correct_memorystore_name:
        memorystore_instance_name = "projects/allen-dev-396002/locations/us-west1/instances/redis-cld-advbe8prrhdxx7cgnrgimtp8"
    else:
        memorystore_instance_name = "redis-cld-advbe8prrhdxx7cgnrgimtp8"

    args = [
        "--provider",
        provider,
        "--name",
        name,
        "--region",
        region,
        "--project-id",
        project_id,
        "--vpc-name",
        vpc_name,
        "--subnet-names",
        subnet_names,
        "--firewall-policy-names",
        firewall_policy_names,
        "--cloud-storage-bucket-name",
        cloud_storage_bucket_name,
        "--filestore-instance-id",
        filestore_instance_id,
        "--filestore-location",
        filestore_location,
        "--anyscale-service-account-email",
        anyscale_service_account_email,
        "--instance-service-account-email",
        instance_service_account_email,
        "--provider-name",
        provider_name,
    ]
    if host_project_id:
        args.extend(["--host-project-id", host_project_id])

    if enable_head_node_fault_tolerance:
        args.extend(["--memorystore-instance-name", memorystore_instance_name])

    with patch(
        "anyscale.commands.cloud_commands.CloudController", new=mock_cloud_controller,
    ):
        if not correct_memorystore_name:
            result = runner.invoke(register_cloud, args=args, catch_exceptions=False)
            assert "Please provide a valid memorystore instance name." in result.output
            mock_register_cloud.assert_not_called()
        else:
            runner.invoke(register_cloud, args=args)

            mock_register_cloud.assert_called_once_with(
                region=region,
                name=name,
                project_id=project_id,
                vpc_name=vpc_name,
                subnet_names=subnet_names.split(","),
                filestore_instance_id=filestore_instance_id,
                filestore_location=filestore_location,
                anyscale_service_account_email=anyscale_service_account_email,
                instance_service_account_email=instance_service_account_email,
                provider_id=provider_name,
                firewall_policy_names=firewall_policy_names.split(","),
                cloud_storage_bucket_name=cloud_storage_bucket_name,
                memorystore_instance_name=memorystore_instance_name
                if enable_head_node_fault_tolerance
                else None,
                host_project_id=host_project_id,
                functional_verify=None,
                private_network=False,
                cluster_management_stack_version=ClusterManagementStackVersions.V2,
                yes=False,
                skip_verifications=False,
                auto_add_user=False,
            )


@pytest.mark.parametrize(
    ("log_ingestion_option", "response_value", "mock_click_return_value"),
    [
        ("--enable-log-ingestion", True, "consent"),
        ("--enable-log-ingestion", False, "no consent"),
        ("--disable-log-ingestion", True, True),
        ("--disable-log-ingestion", False, False),
    ],
)
@mock.patch("click.prompt")
@mock.patch("click.confirm")
def test_cloud_config_update_with_log_ingestion(
    mock_click_confirm,
    mock_click_prompt,
    log_ingestion_option,
    response_value,
    mock_click_return_value,
):
    runner = CliRunner()
    mock_cloud_controller = Mock()
    mock_update_cloud_config = Mock()
    mock_cloud_controller().update_cloud_config = mock_update_cloud_config
    mock_click_confirm.return_value = mock_click_return_value
    mock_click_prompt.return_value = mock_click_return_value

    name = "unit-test-cloud"
    enable_log_ingestion = "enable" in log_ingestion_option
    args = ["--name", name, log_ingestion_option]

    with patch(
        "anyscale.commands.cloud_commands.CloudController", new=mock_cloud_controller,
    ):
        runner.invoke(cloud_config_update, args=args, catch_exceptions=False)

        if not response_value:
            mock_update_cloud_config.assert_not_called()
        else:
            mock_update_cloud_config.assert_called_once_with(
                cloud_name=name,
                cloud_id=None,
                enable_log_ingestion=enable_log_ingestion,
            )
