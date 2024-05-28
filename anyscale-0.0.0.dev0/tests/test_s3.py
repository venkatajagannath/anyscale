import copy
import json
from typing import Any, List
from unittest.mock import Mock

import boto3
from moto import mock_iam, mock_s3
import pytest

from anyscale.aws_iam_policies import AMAZON_S3_FULL_ACCESS_POLICY_ARN
from anyscale.utils.s3 import (
    _verify_identity_based_s3_access,
    _verify_resource_based_s3_access,
    REQUIRED_S3_PERMISSIONS,
    verify_s3_access,
)


"""
Negative Test Cases
* Role with Wrong S3 Bucket permissions
"""

_POLICY_TEMPLATE = {
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": list(REQUIRED_S3_PERMISSIONS)}],
}

_BUCKET_NAME = "bucket-test"


def _create_role() -> Any:
    _name = "our-role"
    boto3.client("iam").create_role(RoleName=_name, AssumeRolePolicyDocument="{}")
    return boto3.resource("iam").Role(_name)


def _create_bucket() -> Any:
    boto3.client("s3").create_bucket(Bucket=_BUCKET_NAME)
    return boto3.resource("s3").Bucket(_BUCKET_NAME)


def _add_policy(role: Any, resource: str, inline: bool, as_list: bool):
    policy_document = copy.deepcopy(_POLICY_TEMPLATE)
    policy_document["Statement"][0]["Resource"] = [resource] if as_list else resource  # type: ignore
    if inline:
        boto3.client("iam").put_role_policy(
            RoleName=role.name,
            PolicyName="inline-iam-s3-specific",
            PolicyDocument=json.dumps(policy_document),
        )
    else:
        policy = boto3.client("iam").create_policy(
            PolicyName="iam-s3-specific", PolicyDocument=json.dumps(policy_document)
        )["Policy"]["Arn"]
        role.attach_policy(PolicyArn=policy)


@mock_iam
@mock_s3
@pytest.mark.parametrize(
    "resource",
    [
        pytest.param("arn:aws:s3:::" + _BUCKET_NAME, id="S3SpecificPermissions"),
        pytest.param("*", id="S3GenericPermissions"),
    ],
)
@pytest.mark.parametrize("inline", [True, False])
@pytest.mark.parametrize("as_list", [True, False])
def test_correct_policy_on_role(resource: str, inline: bool, as_list: bool):
    role = _create_role()
    bucket = _create_bucket()
    _add_policy(role, resource, inline, as_list)
    mock_logger = Mock()

    assert _verify_identity_based_s3_access(boto3.Session(), bucket, role, mock_logger)
    mock_logger.info.assert_not_called()


@mock_iam
@mock_s3
def test_s3_full_access_on_role():
    role = _create_role()
    role.attach_policy(PolicyArn=AMAZON_S3_FULL_ACCESS_POLICY_ARN)
    bucket = _create_bucket()
    mock_logger = Mock()

    assert _verify_identity_based_s3_access(boto3.Session(), bucket, role, mock_logger)
    mock_logger.info.assert_not_called()


@mock_iam
@mock_s3
@pytest.mark.parametrize(
    "allow_actions",
    [
        pytest.param(["s3:*"], id="S3_Star"),
        pytest.param(list(REQUIRED_S3_PERMISSIONS), id="S3_Specific"),
    ],
)
def test_correct_policy_on_bucket(allow_actions: List[str]):
    role = _create_role()
    bucket = _create_bucket()

    policy_document = copy.deepcopy(_POLICY_TEMPLATE)
    policy_document["Statement"][0]["Resource"] = [  # type: ignore
        f"arn:aws:s3:::{bucket.name}",
        f"arn:aws:s3:::{bucket.name}/*",
    ]
    policy_document["Statement"][0]["Principal"] = {"AWS": role.arn}  # type: ignore
    policy_document["Statement"][0]["Actions"] = allow_actions  # type: ignore
    bucket.Policy().put(Policy=json.dumps(policy_document))

    mock_logger = Mock()
    assert _verify_resource_based_s3_access(bucket, role, mock_logger)
    mock_logger.info.assert_not_called()


@mock_s3
@mock_iam
def test_no_permissions():
    bucket = _create_bucket()
    role = _create_role()
    mock_logger = Mock()
    assert not verify_s3_access(boto3.Session(), bucket, role, mock_logger)
    mock_logger.info.assert_not_called()


@mock_iam
@mock_s3
def test_policy_on_bucket_missing_perms():
    role = _create_role()
    bucket = _create_bucket()

    policy_document = copy.deepcopy(_POLICY_TEMPLATE)
    policy_document["Statement"][0]["Resource"] = [  # type: ignore
        f"arn:aws:s3:::{bucket.name}",
        f"arn:aws:s3:::{bucket.name}/*",
    ]
    policy_document["Statement"][0]["Principal"] = {"AWS": role.arn}  # type: ignore
    policy_document["Statement"][0]["Action"] = list(REQUIRED_S3_PERMISSIONS)[:-1]  # type: ignore
    bucket.Policy().put(Policy=json.dumps(policy_document))

    assert not verify_s3_access(boto3.Session(), bucket, role, Mock())

    mock_logger = Mock()
    assert not _verify_resource_based_s3_access(bucket, role, mock_logger)
    mock_logger.info.assert_called_once()


@mock_iam
@mock_s3
def test_policy_on_role_missing_perms():
    role = _create_role()
    bucket = _create_bucket()

    policy_document = copy.deepcopy(_POLICY_TEMPLATE)
    policy_document["Statement"][0]["Resource"] = [  # type: ignore
        f"arn:aws:s3:::{bucket.name}",
        f"arn:aws:s3:::{bucket.name}/*",
    ]
    policy_document["Statement"][0]["Action"] = list(REQUIRED_S3_PERMISSIONS)[:-1]  # type: ignore
    boto3.client("iam").put_role_policy(
        RoleName=role.name,
        PolicyName="inline-iam-s3-specific",
        PolicyDocument=json.dumps(policy_document),
    )

    assert not verify_s3_access(boto3.Session(), bucket, role, Mock())

    mock_logger = Mock()
    assert not _verify_identity_based_s3_access(
        boto3.Session(), bucket, role, mock_logger
    )
    mock_logger.info.assert_called_once()


@mock_iam
@mock_s3
@pytest.mark.parametrize("inline", [True, False])
@pytest.mark.parametrize("as_list", [True, False])
def test_policy_on_role_for_wrong_bucket(inline: bool, as_list: bool):
    role = _create_role()
    bucket = _create_bucket()
    _add_policy(role, "arn:aws:s3:::incorrect-bucket-name", inline, as_list)

    mock_logger = Mock()
    assert not verify_s3_access(boto3.Session(), bucket, role, mock_logger)
    mock_logger.info.assert_not_called()


@mock_iam
@mock_s3
def test_policy_on_bucket_for_wrong_role():
    role = _create_role()
    bucket = _create_bucket()

    policy_document = copy.deepcopy(_POLICY_TEMPLATE)
    policy_document["Statement"][0]["Resource"] = [  # type: ignore
        f"arn:aws:s3:::{bucket.name}",
        f"arn:aws:s3:::{bucket.name}/*",
    ]
    policy_document["Statement"][0]["Principal"] = {"AWS": "something_random"}  # type: ignore
    bucket.Policy().put(Policy=json.dumps(policy_document))

    mock_logger = Mock()
    assert not verify_s3_access(boto3.Session(), bucket, role, mock_logger)
    mock_logger.info.assert_not_called()
