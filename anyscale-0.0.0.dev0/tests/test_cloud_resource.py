import json
import os
import random
import re
import string
import sys
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import Mock, patch

import boto3
from botocore.exceptions import ClientError
from click import ClickException
from moto import mock_cloudformation, mock_ec2, mock_efs, mock_iam, mock_s3
import pytest

from anyscale.aws_iam_policies import (
    AMAZON_ECR_READONLY_ACCESS_POLICY_ARN,
    AMAZON_S3_FULL_ACCESS_POLICY_ARN,
    ANYSCALE_IAM_PERMISSIONS_EC2_INITIAL_RUN,
    ANYSCALE_IAM_PERMISSIONS_EC2_STEADY_STATE,
    ANYSCALE_IAM_PERMISSIONS_SERVICE_STEADY_STATE,
    get_anyscale_aws_iam_assume_role_policy,
)
from anyscale.cli_logger import CloudSetupLogger
from anyscale.client.openapi_client.models.aws_memory_db_cluster_config import (
    AWSMemoryDBClusterConfig,
)
from anyscale.client.openapi_client.models.create_cloud_resource import (
    CreateCloudResource,
)
from anyscale.client.openapi_client.models.subnet_id_with_availability_zone_aws import (
    SubnetIdWithAvailabilityZoneAWS,
)
from anyscale.cloud_resource import (
    _verify_aws_efs_policy,
    is_internal_communication_allowed,
    verify_aws_cloudformation_stack,
    verify_aws_efs,
    verify_aws_iam_roles,
    verify_aws_memorydb_cluster,
    verify_aws_s3,
    verify_aws_security_groups,
    verify_aws_subnets,
    verify_aws_vpc,
)
from anyscale.conf import ANYSCALE_IAM_ROLE_NAME
from anyscale.shared_anyscale_utils.aws import AwsRoleArn
from anyscale.shared_anyscale_utils.conf import ANYSCALE_CORS_ORIGIN
from anyscale.utils.network_verification import AWS_SUBNET_CAPACITY


DEFAULT_RAY_IAM_ROLE = "ray-autoscaler-v1"


def _create_roles(anyscale_account: str):
    iam = boto3.client("iam")
    suffix = "".join(random.choices(string.ascii_lowercase, k=10))
    control_plane_role = iam.create_role(
        RoleName=ANYSCALE_IAM_ROLE_NAME + suffix,
        AssumeRolePolicyDocument=json.dumps(
            get_anyscale_aws_iam_assume_role_policy(
                anyscale_aws_account=anyscale_account
            )
        ),
    )["Role"]["Arn"]

    # Create & Configure the Dataplane Role
    dataplane_role_name = DEFAULT_RAY_IAM_ROLE + suffix
    dataplane_role = iam.create_role(
        RoleName=dataplane_role_name,
        AssumeRolePolicyDocument=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Allow",
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }
        ),
    )["Role"]["Arn"]

    iam.attach_role_policy(
        RoleName=dataplane_role_name, PolicyArn=AMAZON_ECR_READONLY_ACCESS_POLICY_ARN
    )
    iam.attach_role_policy(
        RoleName=dataplane_role_name, PolicyArn=AMAZON_S3_FULL_ACCESS_POLICY_ARN
    )
    return [control_plane_role, dataplane_role]


def _delete_role(role_arn: str) -> None:
    iam = boto3.client("iam")
    role_name = AwsRoleArn.from_string(role_arn).to_role_name()

    policies = iam.list_attached_role_policies(RoleName=role_name)["AttachedPolicies"]

    for policy in policies:
        iam.detach_role_policy(RoleName=role_name, PolicyArn=policy["PolicyArn"])

    iam.delete_role(RoleName=role_name)


def generate_cloud_resource_mock_aws(
    enable_head_node_fault_tolerance: bool = False,
) -> CreateCloudResource:
    return CreateCloudResource(
        aws_vpc_id="fake_aws_vpc_id",
        aws_subnet_ids_with_availability_zones=[
            SubnetIdWithAvailabilityZoneAWS(
                subnet_id="fake_aws_subnet_id_0", availability_zone="fake_aws_az_0"
            ),
            SubnetIdWithAvailabilityZoneAWS(
                subnet_id="fake_aws_subnet_id_1", availability_zone="fake_aws_az_1"
            ),
        ],
        aws_iam_role_arns=[
            "arn:aws:iam::123:role/mock_anyscale_role",
            "arn:aws:iam::123:role/mock_dataplane_role",
        ],
        aws_security_groups=["fake_aws_security_group_0"],
        aws_s3_id="fake_aws_s3_id",
        aws_efs_id="fake_aws_efs_id",
        aws_cloudformation_stack_id="fake_aws_cloudformation_stack_id",
        memorydb_cluster_config=AWSMemoryDBClusterConfig(
            id="fake_memorydb_id", endpoint="fake_memorydb_endpoint:6379"
        )
        if enable_head_node_fault_tolerance
        else None,
    )


def _attach_iam_roles_to_role(role_arn: str) -> None:
    iam = boto3.client("iam")
    role_name = AwsRoleArn.from_string(role_arn).to_role_name()

    steady_state = iam.create_policy(
        PolicyName="".join(random.choices(string.ascii_lowercase, k=10)),
        PolicyDocument=json.dumps(ANYSCALE_IAM_PERMISSIONS_EC2_STEADY_STATE),
    )["Policy"]["Arn"]
    iam.attach_role_policy(RoleName=role_name, PolicyArn=steady_state)

    service_steady_state = iam.create_policy(
        PolicyName="".join(random.choices(string.ascii_lowercase, k=10)),
        PolicyDocument=json.dumps(ANYSCALE_IAM_PERMISSIONS_SERVICE_STEADY_STATE),
    )["Policy"]["Arn"]
    iam.attach_role_policy(RoleName=role_name, PolicyArn=service_steady_state)

    initial_run = iam.create_policy(
        PolicyName="".join(random.choices(string.ascii_lowercase, k=10)),
        PolicyDocument=json.dumps(ANYSCALE_IAM_PERMISSIONS_EC2_INITIAL_RUN),
    )["Policy"]["Arn"]
    iam.attach_role_policy(RoleName=role_name, PolicyArn=initial_run)


def _attach_inline_iam_policy_to_role(role_arn: str) -> None:
    iam = boto3.client("iam")
    role_name = AwsRoleArn.from_string(role_arn).to_role_name()

    iam.put_role_policy(
        RoleName=role_name,
        PolicyName="".join(random.choices(string.ascii_lowercase, k=10)),
        PolicyDocument=json.dumps(ANYSCALE_IAM_PERMISSIONS_EC2_STEADY_STATE),
    )
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName="".join(random.choices(string.ascii_lowercase, k=10)),
        PolicyDocument=json.dumps(ANYSCALE_IAM_PERMISSIONS_SERVICE_STEADY_STATE),
    )
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName="".join(random.choices(string.ascii_lowercase, k=10)),
        PolicyDocument=json.dumps(ANYSCALE_IAM_PERMISSIONS_EC2_INITIAL_RUN),
    )


def _create_instance_profile_for_role(
    role_arn: str, instance_profile_name: Optional[str]
) -> None:
    role_name = AwsRoleArn.from_string(role_arn).to_role_name()
    if instance_profile_name is None:
        instance_profile_name = role_name

    iam = boto3.client("iam")
    iam.create_instance_profile(InstanceProfileName=instance_profile_name)
    iam.add_role_to_instance_profile(
        RoleName=role_name, InstanceProfileName=instance_profile_name,
    )


def _create_vpc(cidr_block: str = "10.0.0.0/16", region: str = "us-west-2") -> str:
    ec2 = boto3.client("ec2", region_name=region)
    vpc = ec2.create_vpc(CidrBlock=cidr_block)
    return vpc["Vpc"]["VpcId"]


def _create_subnets(
    vpc_id: str,
    region: str,
    num_subnets: int = 2,
    assign_public_ip: bool = False,
    use_single_availability_zone: bool = False,
) -> List[SubnetIdWithAvailabilityZoneAWS]:
    ec2 = boto3.client("ec2", region_name=region)
    subnet_ids = []
    for i in range(num_subnets):
        subnet = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=f"10.0.{i}.0/24",
            AvailabilityZone=f"{region}a"
            if use_single_availability_zone
            else f"{region}{string.ascii_lowercase[i]}",
        )
        subnet_id = subnet["Subnet"]["SubnetId"]
        subnet_az = subnet["Subnet"]["AvailabilityZone"]
        subnet_ids.append(
            SubnetIdWithAvailabilityZoneAWS(
                subnet_id=subnet_id, availability_zone=subnet_az
            )
        )
        # MapPublicIpOnLaunch is by default False.
        if assign_public_ip:
            ec2.modify_subnet_attribute(
                SubnetId=subnet_id, MapPublicIpOnLaunch={"Value": True},
            )

    return subnet_ids


def _create_security_group(region: str) -> str:
    ec2 = boto3.client("ec2", region_name=region)
    vpc_id = _create_vpc(region=region)

    security_group = ec2.create_security_group(
        VpcId=vpc_id, GroupName="mock_security_group", Description="mock_security_group"
    )
    security_group_id = security_group["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                "IpProtocol": "-1",
                "FromPort": -1,
                "ToPort": -1,
                "UserIdGroupPairs": [{"GroupId": security_group_id,}],
            }
        ],
    )

    return security_group_id


def _create_security_group_given_permissions(
    permissions: List[str], region: str
) -> str:
    ec2 = boto3.client("ec2", region_name=region)
    vpc_id = _create_vpc(region=region)

    security_group = ec2.create_security_group(
        VpcId=vpc_id, GroupName="mock_security_group", Description="mock_security_group"
    )
    security_group_id = security_group["GroupId"]

    port_number = {"https": 443, "ssh": 22, "self": -1, "excess": 123}

    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                "IpProtocol": "-1" if permission == "self" else "tcp",
                "FromPort": port_number[permission],
                "ToPort": port_number[permission],
                "UserIdGroupPairs": [{"GroupId": security_group_id}],
            }
            for permission in permissions
        ],
    )

    return security_group_id


def _create_security_group_inbound_permission_expected(region: str) -> str:
    ec2 = boto3.client("ec2", region_name=region)
    vpc_id = _create_vpc(region=region)

    security_group = ec2.create_security_group(
        VpcId=vpc_id, GroupName="mock_security_group", Description="mock_security_group"
    )
    security_group_id = security_group["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",  # use tcp instead of -1 because of moto impl issue
                "FromPort": 443,
                "ToPort": 443,
                "UserIdGroupPairs": [{"GroupId": security_group_id}],
            },
            {
                "IpProtocol": "tcp",  # use tcp instead of -1 because of moto impl issue
                "FromPort": 22,
                "ToPort": 22,
                "UserIdGroupPairs": [{"GroupId": security_group_id}],
            },
            {
                "IpProtocol": "-1",  # -1 is needed for check here: https://github.com/anyscale/product/blob/master/frontend/cli/anyscale/cloud_resource.py#L378
                "FromPort": -1,
                "ToPort": -1,
                "UserIdGroupPairs": [{"GroupId": security_group_id}],
            },
        ],
    )
    return security_group_id


def _create_security_group_inbound_permission_excessive_permission(region: str) -> str:
    ec2 = boto3.client("ec2", region_name=region)
    vpc_id = _create_vpc(region=region)

    security_group = ec2.create_security_group(
        VpcId=vpc_id, GroupName="mock_security_group", Description="mock_security_group"
    )
    security_group_id = security_group["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",  # use tcp instead of -1 because of moto impl issue
                "FromPort": 443,
                "ToPort": 443,
                "UserIdGroupPairs": [{"GroupId": security_group_id}],
            },
            {
                "IpProtocol": "tcp",  # use tcp instead of -1 because of moto impl issue
                "FromPort": 22,
                "ToPort": 22,
                "UserIdGroupPairs": [{"GroupId": security_group_id}],
            },
            {
                "IpProtocol": "tcp",  # use tcp instead of -1 because of moto impl issue
                "FromPort": 123,
                "ToPort": 123,
                "UserIdGroupPairs": [{"GroupId": security_group_id}],
            },
            {
                "IpProtocol": "-1",  # -1 is needed for check here: https://github.com/anyscale/product/blob/master/frontend/cli/anyscale/cloud_resource.py#L378
                "FromPort": -1,
                "ToPort": -1,
                "UserIdGroupPairs": [{"GroupId": security_group_id}],
            },
        ],
    )
    return security_group_id


def _create_bucket(
    bucket_name: str = "mock_bucket", cors_rules: Any = None, region: str = "us-east-1"
) -> Any:
    s3 = boto3.client("s3")
    kwargs = {}
    if region != "us-east-1":
        kwargs["CreateBucketConfiguration"] = {"LocationConstraint": region}

    s3.create_bucket(Bucket=bucket_name, **kwargs)  # type: ignore
    if cors_rules:
        s3.put_bucket_cors(
            Bucket=bucket_name, CORSConfiguration={"CORSRules": cors_rules}
        )
    return boto3.resource("s3").Bucket(bucket_name)


def _create_efs(
    region: str,
    subnet_ids: List[str],
    security_group_ids: List[str],
    mount_target_ips: Any = None,
    backup: bool = False,
):
    efs = boto3.client("efs", region_name=region)
    create_resp = efs.create_file_system(CreationToken="mock_efs", Backup=backup)
    efs_id = create_resp["FileSystemId"]

    for subnet_id in subnet_ids:
        if mount_target_ips:
            efs.create_mount_target(
                FileSystemId=efs_id,
                SubnetId=subnet_id,
                SecurityGroups=security_group_ids,
                IpAddress=mount_target_ips[subnet_id],
            )
        else:
            efs.create_mount_target(
                FileSystemId=efs_id,
                SubnetId=subnet_id,
                SecurityGroups=security_group_ids,
            )
    return efs_id


def _create_cloudformation_stack(region: str) -> str:
    cloudformation = boto3.client("cloudformation", region_name=region)
    cfn = cloudformation.create_stack(
        StackName="mock_cloudformation_stack",
        TemplateBody=json.dumps(
            {
                "Resources": {
                    "mock_resource": {
                        "Type": "AWS::EC2::Instance",
                        "Properties": {
                            "InstanceType": "t2.micro",
                            "ImageId": "ami-0b69ea66ff7391e80",
                        },
                    }
                }
            }
        ),
    )

    return cfn["StackId"]


@pytest.mark.parametrize(
    ("vpc_exists", "vpc_cidr_block", "expected_result", "expected_log_message"),
    [
        pytest.param(False, "0.0.0.0/0", False, r"Could not find"),
        # Happy sizes
        pytest.param(True, "0.0.0.0/16", True, r"verification succeeded."),
        pytest.param(True, "0.0.0.0/20", True, r"verification succeeded."),
        # Warn sizes
        pytest.param(
            True, "0.0.3.0/21", True, r"but this VPC only supports up to \d+ addresses",
        ),
        pytest.param(
            True, "0.0.4.0/24", True, r"but this VPC only supports up to \d+ addresses",
        ),
        # Error sizes
        pytest.param(
            True,
            "0.0.4.0/25",
            False,
            r"Please reach out to support if this is an issue!",
        ),
    ],
)
@mock_ec2
def test_verify_aws_vpc(
    capsys,
    vpc_exists: bool,
    vpc_cidr_block: str,
    expected_result: bool,
    expected_log_message: str,
):
    cloud_resource_mock = generate_cloud_resource_mock_aws()
    region = "us-west-2"
    if vpc_exists:
        vpc_id = _create_vpc(cidr_block=vpc_cidr_block, region=region)
        cloud_resource_mock.aws_vpc_id = vpc_id

    result = verify_aws_vpc(
        cloud_resource=cloud_resource_mock,
        boto3_session=boto3.Session(region_name=region),
        logger=CloudSetupLogger(),
    )
    assert result == expected_result

    stdout, stderr = capsys.readouterr()
    sys.stdout.write(stdout)
    sys.stderr.write(stderr)

    if expected_log_message:
        assert re.search(expected_log_message, stderr)


@pytest.mark.parametrize(
    ("is_private_network"), [False, True],
)
@pytest.mark.parametrize(
    ("assign_public_ip"), [False, True],
)
@mock_ec2
def test_verify_aws_subnets(capsys, is_private_network: bool, assign_public_ip: bool):
    cloud_resource_mock = generate_cloud_resource_mock_aws()
    region = "us-west-2"
    vpc_id = _create_vpc(region=region)
    subnet_ids = _create_subnets(
        vpc_id=vpc_id, region=region, assign_public_ip=assign_public_ip
    )

    cloud_resource_mock.aws_vpc_id = vpc_id
    cloud_resource_mock.aws_subnet_ids_with_availability_zones = subnet_ids

    result = verify_aws_subnets(
        cloud_resource=cloud_resource_mock,
        region=region,
        is_private_network=is_private_network,
        logger=CloudSetupLogger(),
    )

    _, stderr = capsys.readouterr()

    assert result
    assert ("does not have the 'Auto-assign Public IP' option enabled" in stderr) == (
        not is_private_network and not assign_public_ip
    )
    assert ("remove the `--private-network` flag" in stderr) == (
        is_private_network and assign_public_ip
    )
    assert re.search(r"verification succeeded.", stderr)


@mock_ec2
def test_verify_aws_subnets_warn_about_not_assigning_public_ip_in_public_subnets(
    capsys,
):
    cloud_resource_mock = generate_cloud_resource_mock_aws()
    region = "us-west-2"
    vpc_id = _create_vpc(region=region)
    subnet_ids = _create_subnets(vpc_id=vpc_id, region=region, assign_public_ip=False)

    cloud_resource_mock.aws_vpc_id = vpc_id
    cloud_resource_mock.aws_subnet_ids_with_availability_zones = subnet_ids

    result = verify_aws_subnets(
        cloud_resource=cloud_resource_mock,
        region=region,
        is_private_network=False,
        logger=CloudSetupLogger(),
    )

    _, stderr = capsys.readouterr()

    assert result
    assert re.search(
        r"does not have the 'Auto-assign Public IP' option enabled", stderr
    )
    assert re.search(r"verification succeeded.", stderr)


@mock_ec2
def test_verify_aws_subnets_vpc_subnet_mismatch(capsys):
    cloud_resource_mock = generate_cloud_resource_mock_aws()

    region = "us-west-2"
    vpc_id = _create_vpc(region=region)
    subnet_ids = _create_subnets(vpc_id=vpc_id, region=region, num_subnets=2)

    irrevalent_vpc_id = _create_vpc(region=region)

    cloud_resource_mock.aws_vpc_id = irrevalent_vpc_id
    cloud_resource_mock.aws_subnet_ids_with_availability_zones = subnet_ids

    result = verify_aws_subnets(
        cloud_resource=cloud_resource_mock,
        region=region,
        is_private_network=False,
        logger=CloudSetupLogger(),
    )

    _, stderr = capsys.readouterr()

    assert not result
    assert re.search(r"is not in a vpc of this cloud.", stderr)


@mock_ec2
def test_verify_aws_subnets_insufficient_subnets(capsys):
    cloud_resource_mock = generate_cloud_resource_mock_aws()

    region = "us-west-2"
    vpc_id = _create_vpc(region=region)
    subnet_ids = _create_subnets(vpc_id=vpc_id, region=region, num_subnets=1)

    cloud_resource_mock.aws_vpc_id = vpc_id
    cloud_resource_mock.aws_subnet_ids_with_availability_zones = subnet_ids

    result = verify_aws_subnets(
        cloud_resource=cloud_resource_mock,
        region=region,
        is_private_network=False,
        logger=CloudSetupLogger(),
    )
    assert result is False
    _, stderr = capsys.readouterr()
    assert re.search(r"Need at least 2 subnets for a cloud.", stderr)


@mock_ec2
def test_verify_aws_subnets_insufficient_azs(capsys):
    cloud_resource_mock = generate_cloud_resource_mock_aws()

    region = "us-west-2"
    vpc_id = _create_vpc(region=region)
    subnet_ids = _create_subnets(
        vpc_id=vpc_id, region=region, num_subnets=2, use_single_availability_zone=True
    )

    cloud_resource_mock.aws_vpc_id = vpc_id
    cloud_resource_mock.aws_subnet_ids_with_availability_zones = subnet_ids

    result = verify_aws_subnets(
        cloud_resource=cloud_resource_mock,
        region=region,
        is_private_network=False,
        logger=CloudSetupLogger(),
    )
    assert result is False
    _, stderr = capsys.readouterr()
    assert re.search(r"Subnets should be in at least 2 Availability Zones", stderr)


@mock_ec2
def test_verify_aws_subnets_no_subnets():
    cloud_resource_mock = generate_cloud_resource_mock_aws()

    cloud_resource_mock.aws_subnet_ids_with_availability_zones = None

    result = verify_aws_subnets(
        cloud_resource=cloud_resource_mock,
        region="us-west-2",
        is_private_network=False,
        logger=CloudSetupLogger(),
    )
    assert result is False


@pytest.mark.parametrize(
    ("subnet_cidr", "has_capacity", "expected_log_message"),
    [
        # Happy sizes
        ("10.0.0.0/16", True, None),
        ("0.0.0.0/0", True, None),
        ("0.0.1.0/24", True, None),
        # Warn sizes
        ("0.0.2.0/25", True, r"but this Subnet only supports up to \d+ addresses"),
        ("0.0.3.0/28", True, r"but this Subnet only supports up to \d+ addresses"),
        # Error sizes
        ("0.0.3.0/29", False, r"Please reach out to support if this is an issue!"),
    ],
)
def test_aws_subnet_has_enough_capacity(
    subnet_cidr, has_capacity, expected_log_message, capsys
):
    subnet = Mock()
    subnet.id = "vpc-fake_id"
    subnet.cidr_block = subnet_cidr

    assert (
        AWS_SUBNET_CAPACITY.verify_network_capacity(
            cidr_block_str=subnet_cidr,
            resource_name="Subnet",
            logger=CloudSetupLogger(),
        )
        == has_capacity
    )

    stdout, stderr = capsys.readouterr()
    sys.stdout.write(stdout)
    sys.stderr.write(stderr)

    if expected_log_message:
        assert re.search(expected_log_message, stderr)


@mock_iam
@pytest.mark.parametrize(
    ("iam_roles_mock_fn", "expect_warning"),
    [
        pytest.param(lambda _: None, True, id="No Policies"),
        pytest.param(_attach_iam_roles_to_role, False, id="Separate Policies"),
        pytest.param(_attach_inline_iam_policy_to_role, False, id="Inline Policies"),
    ],
)
def test_verify_aws_iam_roles(
    iam_roles_mock_fn: Callable[[str], None], expect_warning: bool
):
    cloud_resource_mock = generate_cloud_resource_mock_aws()
    cp_role_arn, dp_role_arn = _create_roles("fake_anyscale_aws_account")
    _create_instance_profile_for_role(dp_role_arn, None)
    cloud_resource_mock.aws_iam_role_arns = [cp_role_arn, dp_role_arn]
    iam_roles_mock_fn(cp_role_arn)
    mock_logger = Mock()
    assert verify_aws_iam_roles(
        cloud_resource=cloud_resource_mock,
        boto3_session=boto3.Session(),
        anyscale_aws_account="fake_anyscale_aws_account",
        logger=mock_logger,
        cloud_id="fake_cloud_id",
    )

    if expect_warning:
        assert len(mock_logger.warning.mock_calls) == 1
    else:
        mock_logger.warning.assert_not_called()

    assert len(mock_logger.info.mock_calls) == 2


@mock_iam
@pytest.mark.parametrize("include_service_permissions", [True, False])
def test_verify_aws_iam_service_permissions(include_service_permissions: bool,):
    """Test service permission validation
    """
    cloud_resource_mock = generate_cloud_resource_mock_aws()
    cp_role_arn, dp_role_arn = _create_roles("fake_anyscale_aws_account")
    _create_instance_profile_for_role(dp_role_arn, None)
    cloud_resource_mock.aws_iam_role_arns = [cp_role_arn, dp_role_arn]

    iam = boto3.client("iam")
    role_name = AwsRoleArn.from_string(cp_role_arn).to_role_name()

    iam.put_role_policy(
        RoleName=role_name,
        PolicyName="".join(random.choices(string.ascii_lowercase, k=10)),
        PolicyDocument=json.dumps(ANYSCALE_IAM_PERMISSIONS_EC2_STEADY_STATE),
    )
    if include_service_permissions:
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName="".join(random.choices(string.ascii_lowercase, k=10)),
            PolicyDocument=json.dumps(ANYSCALE_IAM_PERMISSIONS_SERVICE_STEADY_STATE),
        )
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName="".join(random.choices(string.ascii_lowercase, k=10)),
        PolicyDocument=json.dumps(ANYSCALE_IAM_PERMISSIONS_EC2_INITIAL_RUN),
    )

    mock_logger = Mock()
    test_status = verify_aws_iam_roles(
        cloud_resource=cloud_resource_mock,
        boto3_session=boto3.Session(),
        anyscale_aws_account="fake_anyscale_aws_account",
        logger=mock_logger,
        cloud_id="fake_cloud_id",
    )

    assert test_status

    if include_service_permissions:

        mock_logger.warning.assert_not_called()
        assert len(mock_logger.info.mock_calls) == 2

    else:
        assert len(mock_logger.confirm_missing_permission.mock_calls) == 1


@mock_iam
@pytest.mark.parametrize(
    ("cp_role_exist", "dp_role_exist"),
    [pytest.param(True, False), pytest.param(False, True),],
)
def test_verify_aws_iam_roles_not_exist(cp_role_exist: bool, dp_role_exist: bool):
    cloud_resource_mock = generate_cloud_resource_mock_aws()
    cp_role_arn, dp_role_arn = _create_roles("fake_anyscale_aws_account")

    if not cp_role_exist:
        _delete_role(cp_role_arn)

    if not dp_role_exist:
        _delete_role(dp_role_arn)

    assert not verify_aws_iam_roles(
        cloud_resource=cloud_resource_mock,
        boto3_session=boto3.Session(),
        anyscale_aws_account="fake_anyscale_aws_account",
        logger=CloudSetupLogger(),
        cloud_id="fake_cloud_id",
    )


@mock_iam
def test_verify_aws_iam_data_plane_role_trust_policy():
    """Tests that the dataplane role only passes validation if it
    gives trust to AWS service EC2."""
    cloud_resource_mock = generate_cloud_resource_mock_aws()
    cp_role_arn, dp_role_arn = _create_roles("fake_anyscale_aws_account")
    cloud_resource_mock.aws_iam_role_arns = [cp_role_arn, dp_role_arn]
    mock_logger = Mock()
    session = boto3.Session()
    print(
        verify_aws_iam_roles(
            cloud_resource=cloud_resource_mock,
            boto3_session=session,
            anyscale_aws_account="fake_anyscale_aws_account",
            logger=mock_logger,
            cloud_id="fake_cloud_id",
        )
    )

    iam = boto3.client("iam")
    suffix = "".join(random.choices(string.ascii_lowercase, k=10))
    dataplane_role_name = DEFAULT_RAY_IAM_ROLE + suffix
    # create a dataplane role without assume role policy document:
    dp_role_arn = iam.create_role(
        RoleName=dataplane_role_name, AssumeRolePolicyDocument="{}"
    )["Role"]["Arn"]

    iam.attach_role_policy(
        RoleName=dataplane_role_name, PolicyArn=AMAZON_ECR_READONLY_ACCESS_POLICY_ARN
    )
    iam.attach_role_policy(
        RoleName=dataplane_role_name, PolicyArn=AMAZON_S3_FULL_ACCESS_POLICY_ARN
    )
    cloud_resource_mock.aws_iam_role_arns = [cp_role_arn, dp_role_arn]

    # No AssumeRolePolicyDocument for role
    assert not verify_aws_iam_roles(
        cloud_resource=cloud_resource_mock,
        boto3_session=session,
        anyscale_aws_account="fake_anyscale_aws_account",
        logger=mock_logger,
        cloud_id="fake_cloud_id",
    )


@mock_iam
def test_verify_aws_iam_roles_instance_profiles():
    """Tests that the dataplane role only passes validation if it has
    an InstanceProfile with the same name as the Role."""
    cloud_resource_mock = generate_cloud_resource_mock_aws()
    cp_role_arn, dp_role_arn = _create_roles("fake_anyscale_aws_account")
    cloud_resource_mock.aws_iam_role_arns = [cp_role_arn, dp_role_arn]
    mock_logger = Mock()

    # No instance profile for role
    assert not verify_aws_iam_roles(
        cloud_resource=cloud_resource_mock,
        boto3_session=boto3.Session(),
        anyscale_aws_account="fake_anyscale_aws_account",
        logger=mock_logger,
        cloud_id="fake_cloud_id",
    )

    # Create an instance profile for the role, but with the wrong name
    _create_instance_profile_for_role(dp_role_arn, "wrong_name")
    assert not verify_aws_iam_roles(
        cloud_resource=cloud_resource_mock,
        boto3_session=boto3.Session(),
        anyscale_aws_account="fake_anyscale_aws_account",
        logger=mock_logger,
        cloud_id="fake_cloud_id",
    )

    # Create a correct insance profile with the role!
    _create_instance_profile_for_role(dp_role_arn, None)
    assert verify_aws_iam_roles(
        cloud_resource=cloud_resource_mock,
        boto3_session=boto3.Session(),
        anyscale_aws_account="fake_anyscale_aws_account",
        logger=mock_logger,
        cloud_id="fake_cloud_id",
    )


@mock_iam
def test_verify_aws_iam_roles_different_account(capsys):
    """Tests that the IAM roles must be in the same account."""
    cloud_resource_mock = generate_cloud_resource_mock_aws()
    cp_role_arn, _ = _create_roles("fake_anyscale_aws_account")
    with patch.dict(os.environ, {"MOTO_ACCOUNT_ID": "112233445566"}):
        _, dp_role_arn = _create_roles("fake_anyscale_aws_account")
    cloud_resource_mock.aws_iam_role_arns = [cp_role_arn, dp_role_arn]

    assert not verify_aws_iam_roles(
        cloud_resource=cloud_resource_mock,
        boto3_session=boto3.Session(),
        anyscale_aws_account="fake_anyscale_aws_account",
        logger=CloudSetupLogger(),
        cloud_id="fake_cloud_id",
    )

    _, stderr = capsys.readouterr()
    assert "All IAM roles must be in the same AWS account:" in stderr


@pytest.mark.parametrize(
    ("sg_list", "expected_result", "expected_log_message"),
    [
        pytest.param([], False, r"Missing security group IDs", id="SG-Does-Not-Exist"),
        pytest.param([False], False, r"Could not find", id="SG-Exists-Not-Valid"),
        pytest.param([True], True, None, id="SG-Exists-And-Valid"),
        pytest.param(
            [True, False], False, r"Could not find", id="2SG-Exists-Not-Valid"
        ),
        pytest.param([True, True], True, None, id="2SG-Exists-And-Valid"),
    ],
)
@mock_ec2
def test_verify_aws_security_groups_exist_and_valid(
    capsys, sg_list: List[bool], expected_result: bool, expected_log_message: str,
):
    cloud_resource_mock = generate_cloud_resource_mock_aws()

    region = "us-west-2"
    cloud_resource_mock.aws_security_groups = []
    for sg_valid in sg_list:
        if sg_valid:  # True means valid sg, False throws not found error
            sg_id = _create_security_group(region)
        else:
            sg_id = "Invalid_SG"
        cloud_resource_mock.aws_security_groups.append(sg_id)

    result = verify_aws_security_groups(
        cloud_resource=cloud_resource_mock,
        boto3_session=boto3.Session(region_name=region),
        logger=CloudSetupLogger(),
    )

    stdout, stderr = capsys.readouterr()
    sys.stdout.write(stdout)
    sys.stderr.write(stderr)

    assert result == expected_result
    if expected_log_message:
        assert re.search(expected_log_message, stderr)


@pytest.mark.parametrize(
    ("not_enough_permission", "excessive_permission", "expected_log_message"),
    [
        pytest.param(False, False, None, id="Expected_Permission"),
        pytest.param(
            True,
            False,
            r"not contain inbound permission for ports",
            id="Not_Enough_Permission",
        ),
        pytest.param(
            False, True, r"allows access to more than", id="Excessive_Permission"
        ),
    ],
)
@mock_ec2
def test_verify_aws_security_groups_inbound_permissions(
    capsys,
    not_enough_permission: bool,
    excessive_permission: bool,
    expected_log_message: str,
):
    cloud_resource_mock = generate_cloud_resource_mock_aws()

    region = "us-west-2"

    if not_enough_permission:
        sg_id = _create_security_group(region)
    elif excessive_permission:
        sg_id = _create_security_group_inbound_permission_excessive_permission(region)
    else:  # expected permission
        sg_id = _create_security_group_inbound_permission_expected(region)

    cloud_resource_mock.aws_security_groups = [sg_id]

    result = verify_aws_security_groups(
        cloud_resource=cloud_resource_mock,
        boto3_session=boto3.Session(region_name=region),
        logger=CloudSetupLogger(),
    )
    stdout, stderr = capsys.readouterr()
    sys.stdout.write(stdout)
    sys.stderr.write(stderr)

    assert result
    if expected_log_message:
        assert re.search(expected_log_message, stderr)


@pytest.mark.parametrize(
    ("ip_permissions", "aws_security_group_ids", "expected_result"),
    [
        pytest.param(
            [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 123,
                    "ToPort": 123,
                    "IpRanges": [{"CidrIp": "0.0.0.0/10"}],
                }
            ],
            ["mock_group_id"],
            False,
        ),
        pytest.param(
            [{"IpProtocol": "-1", "UserIdGroupPairs": [{"GroupId": "unknown"}]}],
            ["mock_group_id"],
            False,
        ),
        pytest.param(
            [{"IpProtocol": "-1", "UserIdGroupPairs": [{"GroupId": "mock_group_id"}]}],
            ["mock_group_id"],
            True,
        ),
        pytest.param(
            [
                {
                    "IpProtocol": "-1",
                    "UserIdGroupPairs": [{"GroupId": "mock_group_id"}],
                },
                {
                    "IpProtocol": "-1",
                    "UserIdGroupPairs": [{"GroupId": "mock_group_id_2"}],
                },
            ],
            ["mock_group_id", "mock_group_id_3"],
            True,
        ),
    ],
)
def test_is_internal_communication_allowed(
    ip_permissions, aws_security_group_ids, expected_result
):
    assert (
        is_internal_communication_allowed(ip_permissions, aws_security_group_ids)
        == expected_result
    )


@pytest.mark.parametrize(
    ("security_groups_permissions", "expected_result", "expected_log_message"),
    [
        pytest.param(
            [["https"], ["ssh"], ["self"]], True, None, id="Expected_Permission"
        ),
        pytest.param(
            [["https", "ssh", "self"], ["ssh", "self"], ["https"]],
            True,
            None,
            id="Expected_Permission_With_Duplicates",
        ),
        pytest.param(
            [["https", "self"], ["self"]],
            True,
            r"not contain inbound permission for ports",
            id="Missing_Permission",
        ),
        pytest.param(
            [["https", "ssh"], ["https"]],
            False,
            r"not contain inbound permission for all ports for traffic from the same",
            id="Missing_Self_Permission",
        ),
        pytest.param(
            [["https", "excess"], ["ssh"], ["self"]],
            True,
            r"allows access to more than",
            id="Excessive_Permission",
        ),
    ],
)
@mock_ec2
def test_verify_aws_security_groups_multiple_security_groups(
    capsys,
    security_groups_permissions: List[List[str]],
    expected_result,
    expected_log_message: str,
):
    """Tests permission check is correct for multiple security groups"""
    cloud_resource_mock = generate_cloud_resource_mock_aws()

    region = "us-west-2"
    sg_ids = []

    for security_group_permission in security_groups_permissions:
        sg_id = _create_security_group_given_permissions(
            security_group_permission, region
        )
        sg_ids.append(sg_id)

    cloud_resource_mock.aws_security_groups = sg_ids

    result = verify_aws_security_groups(
        cloud_resource=cloud_resource_mock,
        boto3_session=boto3.Session(region_name=region),
        logger=CloudSetupLogger(),
    )
    stdout, stderr = capsys.readouterr()
    sys.stdout.write(stdout)
    sys.stderr.write(stderr)

    assert result == expected_result
    if expected_log_message:
        assert re.search(expected_log_message, stderr)


@pytest.mark.parametrize(
    ("s3_exists", "expected_result"),
    [
        pytest.param(False, False, id="S3-Does-Not-Exist"),
        pytest.param(True, True, id="S3-Exists"),
    ],
)
@pytest.mark.parametrize(
    ("cors_rules", "expected_warning_call_count"),
    [
        pytest.param(
            [
                {
                    "AllowedHeaders": ["*"],
                    "AllowedMethods": ["GET"],
                    "AllowedOrigins": [ANYSCALE_CORS_ORIGIN],
                    "ExposeHeaders": [],
                }
            ],
            0,
            id="CorrectCORS",
        ),
        pytest.param(
            [
                {
                    "AllowedHeaders": ["*"],
                    "AllowedMethods": ["GET"],
                    "AllowedOrigins": ["openai.com"],
                    "ExposeHeaders": [],
                }
            ],
            1,
            id="ImproperCORS",
        ),
        pytest.param([], 2, id="NoCORS"),
    ],
)
@mock_s3
@mock_iam
def test_verify_aws_s3(
    s3_exists: bool,
    expected_result: bool,
    cors_rules: List[Dict[str, List[str]]],
    expected_warning_call_count: int,
):
    cloud_resource_mock = generate_cloud_resource_mock_aws()

    region = "us-west-2"
    if s3_exists:
        bucket = _create_bucket(cors_rules=cors_rules, region=region)
        cloud_resource_mock.aws_s3_id = bucket.name

    cp_role_arn, dp_role_arn = _create_roles("fake_anyscale_aws_account")

    cloud_resource_mock.aws_iam_role_arns = [cp_role_arn, dp_role_arn]

    mock_logger = Mock()

    with patch.multiple(
        "anyscale.cloud_resource", verify_s3_access=Mock(return_value=True),
    ):
        result = verify_aws_s3(
            cloud_resource=cloud_resource_mock,
            boto3_session=boto3.Session(region_name=region),
            region=region,
            logger=mock_logger,
        )

    if s3_exists:
        assert mock_logger.warning.call_count == expected_warning_call_count
    else:
        assert mock_logger.error.call_count == 1
        assert mock_logger.warning.call_count == 0

    assert result == expected_result


@mock_s3
@mock_iam
def test_verify_aws_s3_wrong_region(capsys):
    cloud_resource_mock = generate_cloud_resource_mock_aws()

    region = "us-west-2"
    bucket = _create_bucket(region="us-east-1")
    cloud_resource_mock.aws_s3_id = bucket.name

    cp_role_arn, dp_role_arn = _create_roles("fake_anyscale_aws_account")
    cloud_resource_mock.aws_iam_role_arns = [cp_role_arn, dp_role_arn]

    with patch.multiple(
        "anyscale.cloud_resource", verify_s3_access=Mock(return_value=True),
    ):
        verify_aws_s3(
            cloud_resource=cloud_resource_mock,
            boto3_session=boto3.Session(region_name=region),
            region=region,
            logger=CloudSetupLogger(),
        )

    _, stderr = capsys.readouterr()

    assert re.search("S3 bucket .* is in region us-east-1, .* us-west-2", stderr)


@pytest.mark.parametrize(
    (
        "efs_exists",
        "num_subnets_to_use",
        "use_security_group",
        "expected_result",
        "warning",
        "enable_backup",
    ),
    [
        pytest.param(False, 2, True, False, False, True),
        pytest.param(True, 0, False, False, False, True),
        pytest.param(True, 1, True, True, True, True),
        pytest.param(True, 1, False, True, True, True),
        pytest.param(True, 2, True, True, False, True),
        pytest.param(True, 2, False, True, True, True),
        pytest.param(True, 2, False, True, True, False),
    ],
)
@mock_efs
@mock_ec2
def test_verify_aws_efs(
    capsys,
    efs_exists: bool,
    num_subnets_to_use: int,
    use_security_group: bool,
    expected_result: bool,
    warning: bool,
    enable_backup: bool,
):
    cloud_resource_mock = generate_cloud_resource_mock_aws()

    region = "us-west-2"
    if efs_exists:
        vpc_id = _create_vpc(region=region)
        aws_subnet_ids = _create_subnets(vpc_id, region, num_subnets=2)
        assert len(aws_subnet_ids) == 2
        security_group_id = _create_security_group(region)
        subnet_ids_in_efs = [
            subnet.subnet_id for subnet in aws_subnet_ids[:num_subnets_to_use]
        ]
        security_groups_in_efs = [security_group_id] if use_security_group else []
        efs_id = _create_efs(
            region, subnet_ids_in_efs, security_groups_in_efs, backup=enable_backup
        )
        cloud_resource_mock.aws_subnet_ids_with_availability_zones = aws_subnet_ids
        cloud_resource_mock.aws_security_groups = [security_group_id]
        cloud_resource_mock.aws_efs_id = efs_id

    with patch.multiple(
        "anyscale.cloud_resource", _verify_aws_efs_policy=Mock(return_value=True),
    ):
        result = verify_aws_efs(
            cloud_resource=cloud_resource_mock,
            boto3_session=boto3.Session(region_name=region),
            logger=CloudSetupLogger(),
        )
        _, stderr = capsys.readouterr()
        if warning:
            assert re.search(r"does not contain a mount target with the subnet", stderr)
        if enable_backup:
            assert not re.search(r"backup policy is not enabled", stderr)
            assert not re.search(r"backup policy not found", stderr)
        else:
            assert re.search(r"backup policy is not enabled", stderr) or re.search(
                r"backup policy not found", stderr
            )
        assert result == expected_result


@pytest.mark.parametrize("strict", [True, False])
@pytest.mark.parametrize(
    "policy",
    [
        None,
        [
            "elasticfilesystem:ClientRootAccess",
            "elasticfilesystem:ClientWrite",
            "elasticfilesystem:ClientMount",
        ],
        ["elasticfilesystem:ClientWrite", "elasticfilesystem:ClientMount"],
    ],
)
def test_verify_aws_efs_policy(strict: bool, policy: Optional[List[str]], capsys):
    mock_boto3 = Mock()
    efs_id = "mock-efs"

    mock_efs_client = Mock()
    if policy:
        mock_policy_dict = {
            "Version": "2012-10-17",
            "Id": "efs-policy",
            "Statement": [
                {
                    "Sid": "efs-statement",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": policy,
                    "Condition": {
                        "Bool": {"elasticfilesystem:AccessedViaMountTarget": "true"}
                    },
                }
            ],
        }
        mock_efs_client.describe_file_system_policy = Mock(
            return_value={"Policy": json.dumps(mock_policy_dict)}
        )
    else:
        mock_efs_client.describe_file_system_policy = Mock(
            side_effect=ClientError(
                error_response={"Error": {"Code": "PolicyNotFound"}},
                operation_name="describe_file_system_policy",
            )
        )

    mock_boto3.client = Mock(return_value=mock_efs_client)
    verification_result = _verify_aws_efs_policy(
        mock_boto3, efs_id, CloudSetupLogger(), strict
    )

    _, stderr = capsys.readouterr()
    if not policy:
        assert verification_result is True
        assert "does not have sufficient permissions" not in stderr
    elif len(policy) == 3:
        assert verification_result is True
        assert "does not have sufficient permissions" not in stderr
    else:
        assert verification_result == (not strict)
        assert "does not have sufficient permissions" in stderr


@pytest.mark.parametrize(
    ("valid_ip", "expected_result", "expected_log_message",),
    [
        pytest.param(
            False, False, "Mount target registered with the cloud no longer exists."
        ),
        pytest.param(True, True, None),
    ],
)
@mock_efs
@mock_ec2
def test_verify_aws_efs_valid_ip(
    capsys, valid_ip: bool, expected_result: bool, expected_log_message: str,
):
    cloud_resource_mock = generate_cloud_resource_mock_aws()

    region = "us-west-2"

    vpc_id = _create_vpc(region=region)
    subnet_ids_with_az = _create_subnets(vpc_id, region, num_subnets=2)
    subnet_ids = [
        subnet_id_with_az.subnet_id for subnet_id_with_az in subnet_ids_with_az
    ]
    security_groups = [_create_security_group(region)]

    mount_target_ips = {
        subnet_id_with_az.subnet_id: f"10.0.{i}.123"
        for i, subnet_id_with_az in enumerate(subnet_ids_with_az)
    }

    efs_id = _create_efs(
        region, subnet_ids, security_groups, mount_target_ips, backup=True
    )
    cloud_resource_mock.aws_subnet_ids = subnet_ids
    cloud_resource_mock.aws_security_groups = security_groups
    cloud_resource_mock.aws_efs_id = efs_id

    if valid_ip:
        cloud_resource_mock.aws_efs_mount_target_ip = mount_target_ips[subnet_ids[0]]
    else:
        cloud_resource_mock.aws_efs_mount_target_ip = "1.2.3.4"

    with patch.multiple(
        "anyscale.cloud_resource", _verify_aws_efs_policy=Mock(return_value=True),
    ):
        result = verify_aws_efs(
            cloud_resource=cloud_resource_mock,
            boto3_session=boto3.Session(region_name=region),
            logger=CloudSetupLogger(),
        )

    stdout, stderr = capsys.readouterr()
    sys.stdout.write(stdout)
    sys.stderr.write(stderr)

    assert result == expected_result
    if expected_log_message:
        assert re.search(expected_log_message, stderr)


@pytest.mark.parametrize(
    ("cloudformation_stack_exists", "expected_result"),
    [pytest.param(False, False), pytest.param(True, True)],
)
@mock_cloudformation
def test_verify_aws_cloudformation_stack(
    cloudformation_stack_exists: bool, expected_result: bool
):
    cloud_resource_mock = generate_cloud_resource_mock_aws()

    region = "us-west-2"
    if cloudformation_stack_exists:
        cloud_resource_mock.aws_cloudformation_stack_id = _create_cloudformation_stack(
            region
        )

    result = verify_aws_cloudformation_stack(
        cloud_resource=cloud_resource_mock,
        boto3_session=boto3.Session(region_name=region),
        logger=CloudSetupLogger(),
    )
    assert result == expected_result


@pytest.mark.parametrize(
    (
        "enable_head_node_fault_tolerance",
        "redis_cluster_exist",
        "matching_security_group",
        "matching_vpc",
        "matching_subnets",
        "has_lru_set",
        "tls_enabled",
        "is_ha",
        "should_raise_exception",
        "expected_result",
        "expected_log_message",
    ),
    [
        pytest.param(
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            "Missing MemoryDB cluster id",
        ),
        pytest.param(
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            "Could not find MemoryDB cluster",
        ),
        pytest.param(
            True,
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            "that is not the same as the cloud's security group",
        ),
        pytest.param(
            True,
            True,
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            "is not in the same VPC as the cloud",
        ),
        pytest.param(
            True,
            True,
            True,
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            "that is not one of the subnets in the cloud",
        ),
        pytest.param(
            True,
            True,
            True,
            True,
            True,
            False,
            False,
            False,
            False,
            False,
            "should have parameter group with maxmemory-policy set to allkeys-lru",
        ),
        pytest.param(
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            False,
            False,
            False,
            "Please create a memorydb cluster with TLS enabled",
        ),
        pytest.param(
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            False,
            False,
            "This is not enough for high availability",
        ),
        pytest.param(
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            "Failed to verify MemoryDB cluster",
        ),
        pytest.param(True, True, True, True, True, True, True, True, False, True, None),
    ],
)
def test_verify_aws_memorydb_cluster(  # noqa: PLR0913
    capsys,
    enable_head_node_fault_tolerance,
    redis_cluster_exist,
    matching_security_group,
    matching_vpc,
    matching_subnets,
    has_lru_set,
    should_raise_exception,
    tls_enabled,
    is_ha,
    expected_result,
    expected_log_message,
):
    cloud_resource_mock = generate_cloud_resource_mock_aws(
        enable_head_node_fault_tolerance=enable_head_node_fault_tolerance
    )

    if not redis_cluster_exist:
        mock_cluster_resp = {"Clusters": []}
    else:
        mock_cluster_resp = {
            "Clusters": [
                {
                    "SecurityGroups": [
                        {
                            "SecurityGroupId": cloud_resource_mock.aws_security_groups[
                                0
                            ]
                            if matching_security_group
                            else "not-matching-security-group"
                        }
                    ],
                    "SubnetGroupName": "subnet-group-1234567890",
                    "ParameterGroupName": "parameter-group-1234567890",
                    "TLSEnabled": False,
                    "Shards": [
                        {
                            "Name": "shard-0001",
                            "Nodes": [
                                {
                                    "Name": "node-0001",
                                    "Status": "available",
                                    "Endpoint": "node-0001.fake.com",
                                }
                            ],
                        }
                    ],
                },
            ]
        }

    mock_subnet_group_resp = {
        "SubnetGroups": [
            {
                "SubnetGroupName": "subnet-group-1234567890",
                "VpcId": cloud_resource_mock.aws_vpc_id
                if matching_vpc
                else "not-matching-vpc",
            }
        ]
    }

    if matching_subnets:
        mock_subnet_group_resp["SubnetGroups"][0]["Subnets"] = [
            {
                "Identifier": cloud_resource_mock.aws_subnet_ids_with_availability_zones[
                    0
                ].subnet_id,
            },
            {
                "Identifier": cloud_resource_mock.aws_subnet_ids_with_availability_zones[
                    1
                ].subnet_id,
            },
        ]
    else:
        mock_subnet_group_resp["SubnetGroups"][0]["Subnets"] = [
            {"Identifier": "not-matching-subnet-1",},
            {"Identifier": "not-matching-subnet-2",},
        ]

    if has_lru_set:
        mock_parameter_group_resp = {
            "Parameters": [{"Name": "maxmemory-policy", "Value": "allkeys-lru",}]
        }
    else:
        mock_parameter_group_resp = {
            "Parameters": [{"Name": "maxmemory-policy", "Value": "not-allkeys-lru",}]
        }

    if tls_enabled:
        mock_cluster_resp["Clusters"][0]["TLSEnabled"] = True

    if is_ha:
        mock_cluster_resp["Clusters"][0]["Shards"][0]["Nodes"].append(
            {
                "Name": "node-0002",
                "Status": "available",
                "Endpoint": "node-0002.fake.com",
            }
        )

    mock_memorydb_client = Mock(
        describe_clusters=Mock(return_value=mock_cluster_resp),
        describe_subnet_groups=Mock(return_value=mock_subnet_group_resp),
        describe_parameters=Mock(return_value=mock_parameter_group_resp),
    )
    if should_raise_exception:
        mock_memorydb_client.describe_clusters.side_effect = ClientError(
            {
                "Error": {
                    "Code": "AccessDeniedException",
                    "Message": "Permission denied",
                }
            },
            "describe_clusters",
        )

    mock_boto3 = Mock(client=Mock(return_value=mock_memorydb_client))

    if should_raise_exception:
        with pytest.raises(ClickException, match=expected_log_message):
            verify_aws_memorydb_cluster(
                cloud_resource=cloud_resource_mock,
                boto3_session=mock_boto3,
                logger=CloudSetupLogger(),
                strict=True,
            )
        return

    result = verify_aws_memorydb_cluster(
        cloud_resource=cloud_resource_mock,
        boto3_session=mock_boto3,
        logger=CloudSetupLogger(),
        strict=True,
    )

    stdout, stderr = capsys.readouterr()
    sys.stdout.write(stdout)
    sys.stderr.write(stderr)

    assert result == expected_result
    if expected_log_message:
        assert re.search(expected_log_message, stderr)
