from datetime import datetime, timezone
import json
from typing import Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from click import ClickException
from moto import mock_cloudformation, mock_iam
import pytest

from anyscale.aws_iam_policies import ANYSCALE_IAM_POLICIES, AnyscaleIAMPolicy
from anyscale.cli_logger import CloudSetupLogger
from anyscale.client.openapi_client.models import Cloud
from anyscale.utils.cloud_update_utils import (
    add_missing_parameters_to_template_body,
    append_statements_to_customer_drifts_policy,
    AWSCloudformationHandler,
    CUSTOMER_DRIFTS_POLICY_NAME,
    extract_cross_account_iam_role_drift,
    extract_drifted_statements,
    generate_drifted_statements_to_append,
    generate_updated_parameters_and_template,
    get_all_sids,
    get_all_sids_from_policy,
    get_or_create_memorydb,
    get_sids_to_remove,
    is_template_policy_documents_up_to_date,
    merge_parameters,
    PropertyDifference,
    try_delete_customer_drifts_policy,
    update_iam_role,
    update_template_with_memorydb,
    validate_stack_version,
)


def get_mock_cloud():
    mock_cloud = Cloud(
        id="cloud_id_1",
        name="cloud_name_1",
        provider="AWS",
        region="us-west-2",
        credentials="credentials",
        creator_id="creator_id",
        type="PUBLIC",
        created_at=datetime.now(timezone.utc),
        config="",
        state="ACTIVE",
        is_bring_your_own_resource=False,
        is_default=False,
        customer_aggregated_logs_config_id="calc_fake_id",
    )
    return mock_cloud


def generate_mock_statement(sid="IAM") -> Dict:
    statement: Dict = {
        "Sid": sid,
        "Effect": "Allow",
        "Action": ["iam:PassRole", "iam:GetInstanceProfile"],
        "Resource": "*",
    }
    return statement


@pytest.mark.parametrize(
    ("mock_parameter_list", "expected_result"),
    [
        pytest.param([], False, id="no_parameters"),
        pytest.param(
            [
                {
                    "ParameterKey": policy.parameter_key,
                    "ParameterValue": policy.policy_document,
                }
                for policy in ANYSCALE_IAM_POLICIES
            ],
            True,
            id="up_to_date",
        ),
        pytest.param(
            [
                {
                    "ParameterKey": policy.parameter_key,
                    "ParameterValue": policy.policy_document + "extra",
                }
                for policy in ANYSCALE_IAM_POLICIES
            ],
            False,
            id="not_up_to_date",
        ),
    ],
)
def test_is_template_policy_documents_up_to_date(mock_parameter_list, expected_result):
    assert (
        is_template_policy_documents_up_to_date(mock_parameter_list) == expected_result
    )


def _get_cloudformation_template_and_parameters():
    cfn_template_body = """Description: This template creates the resources necessary for an anyscale cloud.
Transform: AWS::LanguageExtensions
Parameters:
  AnyscaleCrossAccountIAMRoleName:
    Description: Name of the cross account IAM role.
    Type: String

  AnyscaleCrossAccountIAMPolicySteadyState:
    Description: Stead state IAM policy document
    Type: String

  AnyscaleCrossAccountIAMPolicyServiceSteadyState:
    Description: Stead state IAM policy document for services
    Type: String

  AnyscaleCrossAccountIAMPolicyInitialRun:
    Description: Initial run IAM policy document
    Type: String

Resources:
  customerRole:
    Type: 'AWS::IAM::Role'
    Properties:
      RoleName: !Ref AnyscaleCrossAccountIAMRoleName
      AssumeRolePolicyDocument:
        Statement:
          - Action: 'sts:AssumeRole'
            Effect: Allow
            Principal:
              AWS: 525325868955
            Sid: 'AnyscaleControlPlaneAssumeRole'
        Version: 2012-10-17
      Path: /

  IAMPermissionEC2SteadyState:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref AnyscaleCrossAccountIAMPolicySteadyState
      PolicyName: Anyscale_IAM_Policy_Steady_State
      Roles:
        - !Ref customerRole

  IAMPermissionServiceSteadyState:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref AnyscaleCrossAccountIAMPolicyServiceSteadyState
      PolicyName: Anyscale_IAM_Policy_Service_Steady_State
      Roles:
        - !Ref customerRole

  IAMPermissionEC2InitialRun:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref AnyscaleCrossAccountIAMPolicyInitialRun
      PolicyName: Anyscale_IAM_Policy_Initial_Setup
      Roles:
        - !Ref customerRole
"""
    mock_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "IAM",
                "Effect": "Allow",
                "Action": ["iam:PassRole", "iam:GetInstanceProfile"],
                "Resource": "*",
            },
        ],
    }
    parameters = [
        {
            "ParameterKey": "AnyscaleCrossAccountIAMRoleName",
            "ParameterValue": "anyscale-iam-role",
        },
        {
            "ParameterKey": "AnyscaleCrossAccountIAMPolicySteadyState",
            "ParameterValue": json.dumps(mock_policy),
        },
        {
            "ParameterKey": "AnyscaleCrossAccountIAMPolicyServiceSteadyState",
            "ParameterValue": json.dumps(mock_policy),
        },
        {
            "ParameterKey": "AnyscaleCrossAccountIAMPolicyInitialRun",
            "ParameterValue": json.dumps(mock_policy),
        },
    ]
    return cfn_template_body, parameters


@pytest.mark.parametrize(
    ("existing_parameters", "parameters_to_update", "expected_merged_parameters"),
    [
        pytest.param(
            [
                {"ParameterKey": "key1", "ParameterValue": "value1"},
                {"ParameterKey": "key2", "ParameterValue": "value2"},
            ],
            [
                {"ParameterKey": "key1", "ParameterValue": "value1"},
                {"ParameterKey": "key2", "ParameterValue": "newvalue2"},
            ],
            [
                {"ParameterKey": "key1", "ParameterValue": "value1"},
                {"ParameterKey": "key2", "ParameterValue": "newvalue2"},
            ],
        ),
        pytest.param(
            [
                {"ParameterKey": "key1", "ParameterValue": "value1"},
                {"ParameterKey": "key2", "ParameterValue": "value2"},
                {"ParameterKey": "key4", "ParameterValue": "value4"},
            ],
            [
                {"ParameterKey": "key1", "ParameterValue": "newvalue1"},
                {"ParameterKey": "key3", "ParameterValue": "newvalue3"},
            ],
            [
                {"ParameterKey": "key1", "ParameterValue": "newvalue1"},
                {"ParameterKey": "key2", "ParameterValue": "value2"},
                {"ParameterKey": "key4", "ParameterValue": "value4"},
                {"ParameterKey": "key3", "ParameterValue": "newvalue3"},
            ],
            id="missing_parameters",
        ),
    ],
)
def test_merge_parameters(
    existing_parameters: List[Dict],
    parameters_to_update: List[Dict],
    expected_merged_parameters: List[str],
):
    assert (
        merge_parameters(existing_parameters, parameters_to_update)
        == expected_merged_parameters
    )


def test_add_missing_parameters_to_template_body():
    mock_template_body, mock_parameters = _get_cloudformation_template_and_parameters()
    mock_new_policy = AnyscaleIAMPolicy(
        parameter_key="NewParameter",
        parameter_description="NewParameter description",
        resource_logical_id="NewParameterResource",
        policy_name="New_Parameter_Policy",
        policy_document='{"Version": "2012-10-17", "Statement": []}',
    )
    mock_parameters.append(
        {
            "ParameterKey": mock_new_policy.parameter_key,
            "ParameterValue": mock_new_policy.policy_document,
        }
    )
    with patch.multiple(
        "anyscale.utils.cloud_update_utils", ANYSCALE_IAM_POLICIES=[mock_new_policy]
    ):
        modified_template_body = add_missing_parameters_to_template_body(
            mock_template_body,
            ["NewParameter", "AnyscaleCLIVersion", "MemoryDBRedisPort"],
        )
        assert (
            modified_template_body
            == f"""Description: This template creates the resources necessary for an anyscale cloud.
Transform: AWS::LanguageExtensions
Parameters:
  {mock_new_policy.parameter_key}:
    Description: {mock_new_policy.parameter_description}
    Type: String

  AnyscaleCLIVersion:
    Description: Anyscale CLI version
    Type: String

  MemoryDBRedisPort:
    Description: Port for MemoryDB Redis
    Type: String
    Default: \"6379\"

  AnyscaleCrossAccountIAMRoleName:
    Description: Name of the cross account IAM role.
    Type: String

  AnyscaleCrossAccountIAMPolicySteadyState:
    Description: Stead state IAM policy document
    Type: String

  AnyscaleCrossAccountIAMPolicyServiceSteadyState:
    Description: Stead state IAM policy document for services
    Type: String

  AnyscaleCrossAccountIAMPolicyInitialRun:
    Description: Initial run IAM policy document
    Type: String

Resources:
  {mock_new_policy.resource_logical_id}:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref {mock_new_policy.parameter_key}
      PolicyName: {mock_new_policy.policy_name}
      Roles:
        - !Ref customerRole

  customerRole:
    Type: 'AWS::IAM::Role'
    Properties:
      RoleName: !Ref AnyscaleCrossAccountIAMRoleName
      AssumeRolePolicyDocument:
        Statement:
          - Action: 'sts:AssumeRole'
            Effect: Allow
            Principal:
              AWS: 525325868955
            Sid: 'AnyscaleControlPlaneAssumeRole'
        Version: 2012-10-17
      Path: /

  IAMPermissionEC2SteadyState:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref AnyscaleCrossAccountIAMPolicySteadyState
      PolicyName: Anyscale_IAM_Policy_Steady_State
      Roles:
        - !Ref customerRole

  IAMPermissionServiceSteadyState:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref AnyscaleCrossAccountIAMPolicyServiceSteadyState
      PolicyName: Anyscale_IAM_Policy_Service_Steady_State
      Roles:
        - !Ref customerRole

  IAMPermissionEC2InitialRun:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref AnyscaleCrossAccountIAMPolicyInitialRun
      PolicyName: Anyscale_IAM_Policy_Initial_Setup
      Roles:
        - !Ref customerRole
"""
        )


@pytest.mark.parametrize(
    ("mock_drift", "has_drift"),
    [
        pytest.param(
            {
                "ResourceType": "AWS::IAM::Role",
                "LogicalResourceId": "customerRole",
                "StackResourceDriftStatus": "MODIFIED",
            },
            True,
            id="has_drift",
        ),
        pytest.param(MagicMock(), False, id="no_drift"),
    ],
)
def test_extract_cross_account_iam_role_drift(mock_drift, has_drift):
    assert (extract_cross_account_iam_role_drift([mock_drift]) is not None) == has_drift


@pytest.mark.parametrize(
    ("all_have_sid"),
    [
        pytest.param(True, id="all_have_sid"),
        pytest.param(False, id="not_all_have_sid"),
    ],
)
def test_get_all_sids_from_policy(all_have_sid: bool):
    policy: Dict = {
        "PolicyDocument": {
            "Version": "2012-10-17",
            "Statement": [generate_mock_statement(),],
        },
        "PolicyName": "mock_policy_name",
    }
    if not all_have_sid:
        statements = policy["PolicyDocument"]["Statement"]
        statements[0].pop("Sid")
        with pytest.raises(ClickException) as e:
            get_all_sids_from_policy(policy)
        e.match("doesn't have a Sid")
    else:
        assert get_all_sids_from_policy(policy) == ["IAM"]


@pytest.mark.parametrize(
    ("no_statement_number", "policy_drift_unexpected"),
    [
        pytest.param(True, False, id="no_statement_number"),
        pytest.param(False, True, id="policy_drift_unexpected"),
        pytest.param(False, False, id="happy_path"),
    ],
)
def test_get_sids_to_remove(no_statement_number: bool, policy_drift_unexpected: bool):
    diffs: List[Dict] = [
        # Not a policy drift
        {
            "PropertyPath": "/Something/Else",
            "ExpectedValue": "sth",
            "ActualValue": "sth",
            "DifferenceType": "NOT_EQUAL",
        },
        # Not a policy we care about
        {
            "PropertyPath": "/Policies/0",
            "ExpectedValue": "sth",
            "ActualValue": "sth",
            "DifferenceType": "NOT_EQUAL",
        },
        # REMOVE
        {
            "PropertyPath": "/Policies/1/PolicyDocument/Statement/0",
            "ExpectedValue": "sth",
            "ActualValue": "sth",
            "DifferenceType": "REMOVE",
        },
        # ADD
        {
            "PropertyPath": "/Policies/1/PolicyDocument/Statement/10",
            "ExpectedValue": "sth",
            "ActualValue": "sth",
            "DifferenceType": "ADD",
        },
        # statement_number longer than number of statements
        {
            "PropertyPath": "/Policies/1/PolicyDocument/Statement/100/Action/4",
            "ExpectedValue": "sth",
            "ActualValue": "sth",
            "DifferenceType": "NOT_EQUAL",
        },
        # sid to remove
        {
            "PropertyPath": "/Policies/1/PolicyDocument/Statement/1/Action/1",
            "ExpectedValue": "sth",
            "ActualValue": "sth",
            "DifferenceType": "NOT_EQUAL",
        },
        # sid already removed
        {
            "PropertyPath": "/Policies/1/PolicyDocument/Statement/1/Action/0",
            "ExpectedValue": "sth",
            "ActualValue": "sth",
            "DifferenceType": "NOT_EQUAL",
        },
    ]
    if no_statement_number:
        diffs.append(
            {
                "PropertyPath": "/Policies/1/PolicyDocument/nostatementnumber",
                "ExpectedValue": "sth",
                "ActualValue": "sth",
                "DifferenceType": "NOT_EQUAL",
            }
        )
    elif policy_drift_unexpected:
        diffs.append(
            {
                "PropertyPath": "/Policies/1/PolicyDocument/Statement/10",
                "ExpectedValue": "sth",
                "ActualValue": "sth",
                "DifferenceType": "NOT_EQUAL",  # shouldn't be not_equal
            }
        )
    mock_policy_name = ANYSCALE_IAM_POLICIES[0].policy_name

    expected_policies = [
        {
            "PolicyName": "AnotherPolicy",
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [generate_mock_statement(),],
            },
        },
        {
            "PolicyName": mock_policy_name,
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [Mock(), generate_mock_statement(),],
            },
        },
    ]

    if no_statement_number or policy_drift_unexpected:
        with pytest.raises(ClickException) as e:
            get_sids_to_remove(diffs, expected_policies)
        e.match("cannot be resolved")
    else:
        sids = get_sids_to_remove(diffs, expected_policies)
        assert len(sids[mock_policy_name]) == 1


def test_generate_drifted_statements_to_append():
    statement_with_no_sid = generate_mock_statement()
    statement_with_no_sid.pop("Sid")
    mock_policy_name = "mock_policy_name"
    actual_policies = [
        {
            "PolicyName": mock_policy_name,
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    generate_mock_statement(),
                    generate_mock_statement("AnotherSid"),
                    statement_with_no_sid,
                ],
            },
        },
        {
            "PolicyName": "AnotherPolicy",
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [generate_mock_statement(),],
            },
        },
    ]
    undrifted_sid = {mock_policy_name: {"IAM"}}
    drifted_statements = generate_drifted_statements_to_append(
        actual_policies, undrifted_sid
    )
    assert len(drifted_statements) == 2
    for statement in drifted_statements:
        assert "Drifted" in statement["Sid"]


@pytest.mark.parametrize("invalid_version", [True, False])
def test_extract_drifted_statements(invalid_version: bool):
    mock_policy_name = "mock_policy_name"
    mock_actual_policies = "mock"
    mock_drift: Dict = {
        "ExpectedProperties": json.dumps(
            {
                "Policies": [
                    {
                        "PolicyName": mock_policy_name,
                        "PolicyDocument": {
                            "Version": "wrong_version"
                            if invalid_version
                            else "2012-10-17",
                            "Statement": [
                                generate_mock_statement(),
                                generate_mock_statement("AnotherSid"),
                            ],
                        },
                    },
                    {
                        "PolicyName": "AnotherPolicy",
                        "PolicyDocument": {
                            "Version": "wrong_version",  # shouldn't raise exception
                            "Statement": [generate_mock_statement(),],
                        },
                    },
                ]
            }
        ),
        "PropertyDifferences": Mock(),
        "ActualProperties": json.dumps({"Policies": mock_actual_policies,}),
    }
    mock_get_all_sids_from_policy = Mock(return_value=["IAM", "AnotherSid"])
    mock_get_sids_to_remove = Mock(
        return_value={mock_policy_name: {"IAM", "AnotherActualSid"}}
    )
    mock_generate_drifted_statements_to_append = Mock()
    with patch.multiple(
        "anyscale.utils.cloud_update_utils",
        ANYSCALE_IAM_POLICIES=[MagicMock(policy_name=mock_policy_name)],
        get_sids_to_remove=mock_get_sids_to_remove,
        generate_drifted_statements_to_append=mock_generate_drifted_statements_to_append,
        get_all_sids_from_policy=mock_get_all_sids_from_policy,
    ):
        if invalid_version:
            with pytest.raises(ClickException) as e:
                extract_drifted_statements(mock_drift)
            e.match("Unexpected policy version")
        else:
            extract_drifted_statements(mock_drift)
            mock_get_all_sids_from_policy.assert_called_once()
            mock_get_sids_to_remove.assert_called_once()
            mock_generate_drifted_statements_to_append.assert_called_once_with(
                mock_actual_policies, {mock_policy_name: {"AnotherSid"}}
            )


@mock_iam
@pytest.mark.parametrize("policy_exists", [True, False])
def test_append_statements_to_customer_drifts_policy(policy_exists: bool):
    mock_region = "us-west-2"
    mock_role_name = "mock_role_name"
    statements = [generate_mock_statement("DriftedSid")]

    # Create the role
    boto3.client("iam", region_name=mock_region).create_role(
        Path="/",
        RoleName=mock_role_name,
        AssumeRolePolicyDocument=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "mock"},
                        "Action": "sts:AssumeRole",
                    },
                ],
            }
        ),
    )
    if policy_exists:
        boto3.client("iam", region_name=mock_region).put_role_policy(
            RoleName=mock_role_name,
            PolicyName=CUSTOMER_DRIFTS_POLICY_NAME,
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [generate_mock_statement("MockSid")],
                }
            ),
        )

    append_statements_to_customer_drifts_policy(mock_region, mock_role_name, statements)

    # Check that the policy has been appended
    policy = boto3.client("iam", region_name=mock_region).get_role_policy(
        RoleName=mock_role_name, PolicyName=CUSTOMER_DRIFTS_POLICY_NAME
    )
    assert "DriftedSid" in [s["Sid"] for s in policy["PolicyDocument"]["Statement"]]


@pytest.mark.parametrize("invalid_version", [True, False])
def test_get_all_sids(invalid_version: bool):
    mock_policy_name = "mock_policy_name"
    mock_expected_policies = [
        {
            "PolicyName": mock_policy_name,
            "PolicyDocument": {
                "Version": "wrong_version" if invalid_version else "2012-10-17",
                "Statement": [
                    generate_mock_statement("OneSid"),
                    generate_mock_statement("AnotherSid"),
                ],
            },
        },
        {
            "PolicyName": "AnotherPolicy",
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [generate_mock_statement(),],
            },
        },
    ]
    with patch.multiple(
        "anyscale.utils.cloud_update_utils",
        ANYSCALE_IAM_POLICIES=[MagicMock(policy_name=mock_policy_name)],
    ):
        if invalid_version:
            with pytest.raises(ClickException) as e:
                get_all_sids(mock_expected_policies)
            e.match("Unexpected policy version")
        else:
            sids = get_all_sids(mock_expected_policies)
            assert len(sids) == 1
            assert mock_policy_name in sids
            assert len(sids[mock_policy_name]) == 2
            assert "OneSid" in sids[mock_policy_name]
            assert "AnotherSid" in sids[mock_policy_name]


@pytest.mark.parametrize(
    ("path", "expected_result"),
    [
        pytest.param(
            "/Policies/1024/PolicyDocument/Statement/0/Action/0",
            1024,
            id="is_policy_drift",
        ),
        pytest.param("/Something/Else", None, id="is_not_policy_drift"),
    ],
)
def test_get_policy_number(path: str, expected_result: Optional[int]):
    mock_diff = PropertyDifference(
        DifferenceType="NOT_EQUAL",
        PropertyPath=path,
        ExpectedValue="iam:PassRole",
        ActualValue="iam:PassRole",
    )
    assert mock_diff.get_policy_number() == expected_result


@pytest.mark.parametrize(
    ("path", "expected_result"),
    [
        pytest.param(
            "/Policies/1024/PolicyDocument/Statement/100/Action/20",
            100,
            id="is_action_drift",
        ),
        pytest.param("/Something/Else", None, id="is_not_policy_drift"),
        pytest.param("/Policies/3", None, id="is_not_statement_drift"),
        pytest.param(
            "/Policies/3/PolicyDocument/Statement/1024", 1024, id="is_statement_drift"
        ),
    ],
)
def test_get_statement_number(path: str, expected_result: Optional[int]):
    mock_diff = PropertyDifference(
        DifferenceType="NOT_EQUAL",
        PropertyPath=path,
        ExpectedValue="iam:PassRole",
        ActualValue="iam:PassRole",
    )
    assert mock_diff.get_statement_number() == expected_result


@pytest.mark.parametrize(
    ("path", "expected_result", "invalid"),
    [
        pytest.param(
            "/Policies/1024/PolicyDocument/Statement/100/Action/20",
            False,
            True,
            id="is_action_drift",
        ),
        pytest.param("/Something/Else", False, False, id="is_not_policy_drift"),
        pytest.param("/Policies/3", False, False, id="is_policy_drift"),
        pytest.param(
            "/Policies/3/PolicyDocument/Statement/1024",
            True,
            False,
            id="is_statement_drift",
        ),
        pytest.param(
            "/Policies/3/PolicyDocument/Statement/1024", True, True, id="invalid"
        ),
    ],
)
def test_is_add_or_remove_statement(path: str, expected_result: bool, invalid: bool):
    mock_diff = PropertyDifference(
        DifferenceType="ADD" if not invalid else "NOT_EQUAL",
        PropertyPath=path,
        ExpectedValue="iam:PassRole",
        ActualValue="iam:PassRole",
    )
    if expected_result and invalid:
        with pytest.raises(ClickException) as e:
            mock_diff.is_add_or_remove_statement()
        e.match("cannot be resolved")
    else:
        assert mock_diff.is_add_or_remove_statement() == expected_result


@mock_iam
@pytest.mark.parametrize(
    ("policy_exists", "delete_failed"),
    [
        pytest.param(True, False, id="policy_exists"),
        pytest.param(False, False, id="policy_does_not_exist"),
        pytest.param(False, True, id="delete_failed"),
    ],
)
def test_try_delete_customer_drifts_policy(policy_exists: bool, delete_failed: bool):
    cloud = get_mock_cloud()
    iam_client = boto3.client("iam", region_name=cloud.region)
    mock_role_name = "mock_role_name"
    cloud.credentials = "arn:aws:iam::123456789012:role/" + mock_role_name

    iam_client.create_role(
        Path="/",
        RoleName=mock_role_name,
        AssumeRolePolicyDocument=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "mock"},
                        "Action": "sts:AssumeRole",
                    },
                ],
            }
        ),
    )

    if policy_exists:
        iam_client.put_role_policy(
            RoleName=mock_role_name,
            PolicyName=CUSTOMER_DRIFTS_POLICY_NAME,
            PolicyDocument=json.dumps(
                {"Version": "2012-10-17", "Statement": [generate_mock_statement()],}
            ),
        )

    if delete_failed:
        iam_client.delete_role_policy = Mock(
            side_effect=ClientError(
                {"Error": {"Code": "Mock", "Message": "Mock Error",}},
                "delete_role_policy",
            )
        )
        with pytest.raises(ClickException) as e, patch.multiple(
            "anyscale.utils.cloud_update_utils", _client=Mock(return_value=iam_client)
        ):
            try_delete_customer_drifts_policy(cloud)
        e.match("Failed to delete inline policy")
    else:
        try_delete_customer_drifts_policy(cloud)
        assert (
            CUSTOMER_DRIFTS_POLICY_NAME
            not in iam_client.list_role_policies(RoleName=mock_role_name)["PolicyNames"]
        )


@pytest.mark.parametrize(
    (
        "describe_stack_client_error",
        "describe_stack_no_credentials",
        "stack_num",
        "stack_status_invalid",
        "expected_error",
    ),
    [
        pytest.param(False, False, 1, False, False, id="happy_path"),
        pytest.param(True, False, 1, False, True, id="describe_stack_client_error"),
        pytest.param(False, True, 1, False, True, id="describe_stack_no_credentials"),
        pytest.param(False, False, 0, False, True, id="unexpected_stacks"),
        pytest.param(False, False, 1, True, True, id="invalid_stack_status"),
    ],
)
def test_AWSCloudformationHandler_init(
    describe_stack_client_error,
    describe_stack_no_credentials,
    stack_num,
    stack_status_invalid,
    expected_error,
):
    mock_id = "mock_id"
    mock_region = "us-west-2"
    mock_client = Mock()
    mock_describe_stacks = Mock()
    mock_client.describe_stacks = mock_describe_stacks
    if describe_stack_client_error:
        mock_describe_stacks.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Mock"}}, "Mock"
        )
    if describe_stack_no_credentials:
        mock_describe_stacks.side_effect = NoCredentialsError()
    stack_list = []
    for _ in range(stack_num):
        stack_list.append(
            {
                "StackName": "mock_stack",
                "StackStatus": "CREATE_COMPLETE"
                if not stack_status_invalid
                else "CREATE_FAILED",
            }
        )
    mock_describe_stacks.return_value = {"Stacks": stack_list}

    with patch.multiple(
        "anyscale.utils.cloud_update_utils", _client=Mock(return_value=mock_client)
    ):
        if expected_error:
            with pytest.raises(ClickException) as e:
                AWSCloudformationHandler(mock_id, mock_region, CloudSetupLogger())
            if describe_stack_client_error:
                e.match("Failed to describe cloudformation stack")
            elif describe_stack_no_credentials:
                e.match("Unable to locate AWS credentials.")
            elif stack_num != 1:
                e.match("unexpected number of cloudformation stacks")
            elif stack_status_invalid:
                e.match("stack is in a stable state")
        else:
            handler = AWSCloudformationHandler(mock_id, mock_region, CloudSetupLogger())
            assert handler.cfn_client == mock_client
            assert handler.region == mock_region
            assert handler.aws_cloudformation_stack_id == mock_id


@pytest.mark.parametrize("get_resource_failed", [True, False])
@mock_cloudformation
def test_AWSCloudformationHandler_get_resource(get_resource_failed):
    region = "us-west-2"
    mock_stack_name = "mock_cloudformation_stack"
    mock_logical_id = "mock_resource"
    cloudformation = boto3.client("cloudformation", region_name=region)
    cfn = cloudformation.create_stack(
        StackName=mock_stack_name,
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
    handler = AWSCloudformationHandler(cfn["StackId"], region, CloudSetupLogger())

    if get_resource_failed:
        with pytest.raises(ClickException) as e:
            handler.get_resource("no_such_id")
        e.match("Failed to get resource")
    else:
        resource = handler.get_resource(mock_logical_id)
        assert resource.get("LogicalResourceId") == mock_logical_id


@pytest.mark.parametrize(
    ("detection_failed", "timeout"),
    [
        pytest.param(True, False, id="detection_failed"),
        pytest.param(False, True, id="timeout"),
    ],
)
def test_AWSCloudformationHandler_detect_drift(detection_failed: bool, timeout: bool):
    # we don't use moto here since moto doesn't support drift detection
    mock_id = "mock_id"
    mock_describe_stack_drift_detection_status = Mock(
        return_value={"DetectionStatus": "DETECTION_COMPLETE",}
    )
    mock_detection_failed_reason = "mock"
    if detection_failed:
        mock_describe_stack_drift_detection_status = Mock(
            return_value={
                "DetectionStatus": "DETECTION_FAILED",
                "DetectionStatusReason": mock_detection_failed_reason,
            }
        )
    elif timeout:
        mock_describe_stack_drift_detection_status = Mock(
            return_value={"DetectionStatus": "DETECTION_IN_PROGRESS",}
        )
    mock_drifts = Mock()
    mock_cfn_client = MagicMock(
        detect_stack_drift=Mock(return_value={"StackDriftDetectionId": mock_id}),
        describe_stack_drift_detection_status=mock_describe_stack_drift_detection_status,
        describe_stack_resource_drifts=Mock(
            return_value={"StackResourceDrifts": mock_drifts}
        ),
        describe_stacks=Mock(
            return_value={
                "Stacks": [{"StackStatus": "CREATE_COMPLETE", "StackName": mock_id}]
            }
        ),
    )
    with patch.multiple(
        "anyscale.utils.cloud_update_utils",
        _client=Mock(return_value=mock_cfn_client),
        DETECT_DRIFT_TIMEOUT_SECONDS=1,
    ):
        cfn_handler = AWSCloudformationHandler(mock_id, "us-west-2", CloudSetupLogger())
        if not detection_failed and not timeout:
            assert cfn_handler.detect_drift() == mock_drifts
        else:
            with pytest.raises(ClickException) as e:
                cfn_handler.detect_drift()
            if detection_failed:
                assert e.match(mock_detection_failed_reason)
            elif timeout:
                e.match("timeout")


@pytest.mark.parametrize(
    ("no_drift", "append_failed", "extract_failed"),
    [
        pytest.param(True, False, False, id="no_drift"),
        pytest.param(False, True, False, id="append_failed"),
        pytest.param(False, False, True, id="extract_failed"),
        pytest.param(False, False, False, id="happy_path"),
    ],
)
def test_AWSCloudformationHandler_resolve_drift(
    no_drift: bool, append_failed: bool, extract_failed: bool, capsys
):
    mock_extract_drifted_statements = Mock(
        return_value=[] if no_drift else [MagicMock()]
    )
    if extract_failed:
        mock_extract_drifted_statements.side_effect = ClickException("mock")
    mock_append_statements_to_customer_drifts_policy = Mock()
    if append_failed:
        mock_append_statements_to_customer_drifts_policy.side_effect = ClickException(
            "mock"
        )
    mock_client = MagicMock(
        describe_stacks=Mock(
            return_value={
                "Stacks": [{"StackStatus": "CREATE_COMPLETE", "StackName": "mock_id"}]
            }
        ),
    )

    with patch.multiple(
        "anyscale.utils.cloud_update_utils",
        extract_drifted_statements=mock_extract_drifted_statements,
        append_statements_to_customer_drifts_policy=mock_append_statements_to_customer_drifts_policy,
        _client=Mock(return_value=mock_client),
    ):

        cfn_handler = AWSCloudformationHandler("mock", "us-west-2", CloudSetupLogger())
        result = cfn_handler.resolve_drift(MagicMock())
    _, stdout = capsys.readouterr()
    if no_drift:
        assert "No drifted statements found." in stdout
        assert result is True
    elif append_failed or extract_failed:
        assert "Failed to resolve drift" in stdout
        assert result is False
    else:
        assert "Drifted statements have been appended to the policy" in stdout
        assert result is True


@mock_cloudformation
def test_AWSCloudformationHandler_get_template_body():
    region = "us-west-2"
    mock_stack_name = "mock_cloudformation_stack"

    mock_template_body = json.dumps(
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
    )

    cloudformation = boto3.client("cloudformation", region_name=region)
    cfn = cloudformation.create_stack(
        StackName=mock_stack_name, TemplateBody=mock_template_body,
    )

    cfn_handler = AWSCloudformationHandler(cfn["StackId"], region, CloudSetupLogger())
    template_body = cfn_handler.get_template_body()
    assert json.dumps(template_body) == mock_template_body


@pytest.mark.parametrize(
    (
        "create_change_set_error",
        "create_change_set_timeout",
        "update_stack_error",
        "update_stack_timeout",
    ),
    [
        pytest.param(True, False, False, False, id="create_change_set_error"),
        pytest.param(False, True, False, False, id="create_change_set_timeout"),
        pytest.param(False, False, True, False, id="update_stack_error"),
        pytest.param(False, False, False, True, id="update_stack_timeout"),
        pytest.param(False, False, False, False, id="happy-path"),
    ],
)
def test_AWSCloudformationHandler_update_cloudformation_stack(
    create_change_set_error,
    create_change_set_timeout,
    update_stack_error,
    update_stack_timeout,
):
    mock_stack_name = "mock_stack_name"
    mock_region = "mock_region"
    mock_change_set_id = "mock_change_set_id"
    mock_template_body, mock_parameters = _get_cloudformation_template_and_parameters()
    mock_change_set = {
        "Status": "CREATE_COMPLETE",
        "StackId": "mock_stack_id",
    }
    if create_change_set_error:
        mock_change_set = {
            "Status": "FAILED",
            "StatusReason": "mock_status_reason",
        }
    elif create_change_set_timeout:
        mock_change_set = {
            "Status": "CREATE_IN_PROGRESS",
        }
    mock_stacks = {
        "Stacks": [{"StackName": mock_stack_name, "StackStatus": "UPDATE_COMPLETE",}]
    }
    mock_describe_stacks = Mock(return_value=mock_stacks)
    if update_stack_error:
        mock_stacks["Stacks"][0]["StackStatus"] = "UPDATE_ROLLBACK_COMPLETE"
    elif update_stack_timeout:
        mock_stacks["Stacks"][0]["StackStatus"] = "CREATE_COMPLETE"

    mock_cfn_client = MagicMock(
        get_template=Mock(return_value={"TemplateBody": mock_template_body}),
        create_change_set=Mock(return_value={"Id": mock_change_set_id}),
        describe_change_set=Mock(return_value=mock_change_set),
        delete_change_set=Mock(),
        execute_change_set=Mock(),
        describe_stacks=mock_describe_stacks,
    )
    with patch.multiple(
        "anyscale.utils.cloud_update_utils",
        _client=Mock(return_value=mock_cfn_client),
        CREATE_CHANGE_SET_TIMEOUT_SECONDS=1,
        UPDATE_CLOUDFORMATION_STACK_TIMEOUT_SECONDS=1,
    ):
        cfn_handler = AWSCloudformationHandler(
            mock_stack_name, mock_region, CloudSetupLogger()
        )
        if (
            create_change_set_error
            or create_change_set_timeout
            or update_stack_error
            or update_stack_timeout
        ):
            with pytest.raises(ClickException) as e:
                cfn_handler.update_cloudformation_stack(
                    mock_template_body, mock_parameters, True, timeout_seconds=1
                )
            if create_change_set_error:
                assert e.match("Failed to create change set")
                mock_cfn_client.delete_change_set.assert_called_once_with(
                    ChangeSetName=mock_change_set_id
                )
                mock_cfn_client.execute_change_set.assert_not_called()
            elif create_change_set_timeout:
                assert e.match("Timeout when creating change set")
                mock_cfn_client.execute_change_set.assert_not_called()
            elif update_stack_error:
                assert e.match("Failed to execute change set")
                mock_cfn_client.execute_change_set.assert_called_once_with(
                    ChangeSetName=mock_change_set_id
                )
            elif update_stack_timeout:
                assert e.match("Timeout when executing change set")
                mock_cfn_client.execute_change_set.assert_called_once_with(
                    ChangeSetName=mock_change_set_id
                )
        else:
            cfn_handler.update_cloudformation_stack(
                mock_template_body, mock_parameters, True,
            )


@pytest.mark.parametrize(
    ("stack_version", "cli_version", "expected_result"),
    [
        pytest.param("0.0.2", "0.0.2", True, id="version-match"),
        pytest.param("0.0.1", "0.0.2", False, id="version-mismatch"),
        pytest.param(None, "0.0.2", False, id="no-stack-version"),
        pytest.param(None, "0.0.0-dev", False, id="dev-cli-1"),
        pytest.param("0.0.2", "0.0.0-dev", False, id="dev-cli-2"),
    ],
)
def test_validate_stack_version(stack_version, cli_version, expected_result):
    mock_parameters = []
    if stack_version:
        mock_parameters.append(
            {"ParameterKey": "AnyscaleCLIVersion", "ParameterValue": stack_version}
        )
    with patch.multiple(
        "anyscale.utils.cloud_update_utils", anyscale_version=cli_version,
    ):
        validate_stack_version(mock_parameters)


@pytest.mark.parametrize("missing_parameter", [True, False])
def test_generate_updated_parameters_and_template(missing_parameter):
    mock_parameters = [
        {"ParameterKey": "AnyscaleCLIVersion", "ParameterValue": "0.0.1"},
    ]
    parameters_to_update = [
        {"ParameterKey": "AnyscaleCLIVersion", "ParameterValue": "0.0.2"},
    ]
    mock_missing_parameter_key = "MemoryDBRedisPort"
    if missing_parameter:
        parameters_to_update.append(
            {"ParameterKey": mock_missing_parameter_key, "ParameterValue": "6379"}
        )
    mock_template_body = "mock"
    mock_add_missing_parameters_to_template_body = Mock()
    with patch.multiple(
        "anyscale.utils.cloud_update_utils",
        merge_parameters=Mock(),
        add_missing_parameters_to_template_body=mock_add_missing_parameters_to_template_body,
    ):
        generate_updated_parameters_and_template(
            mock_parameters, mock_template_body, parameters_to_update
        )
        if missing_parameter:
            mock_add_missing_parameters_to_template_body.assert_called_once_with(
                mock_template_body, {mock_missing_parameter_key}
            )


def test_update_template_with_memorydb():
    mock_template_body = """
Resources:
Outputs:
"""
    assert (
        update_template_with_memorydb(mock_template_body, 2)
        == """
Resources:
  MemoryDBSubnetGroup:
    Type: AWS::MemoryDB::SubnetGroup
    Properties:
      Description: Anyscale managed MemoryDB subnet group
      SubnetGroupName: !Ref AWS::StackName
      SubnetIds:
        - !Ref Subnet0
        - !Ref Subnet1
      Tags:
        - Key: anyscale-cloud-id
          Value: !Ref CloudID

  MemoryDBParameterGroup:
    Type: AWS::MemoryDB::ParameterGroup
    Properties:
      Description: Parameter group for anyscale managed MemoryDB
      Family: memorydb_redis7
      ParameterGroupName:  !Ref AWS::StackName
      Tags:
        - Key: anyscale-cloud-id
          Value: !Ref CloudID

  MemoryDB:
    Type: AWS::MemoryDB::Cluster
    Properties:
      ACLName: open-access
      Description: Anyscale managed MemoryDB
      ClusterName: !Ref AWS::StackName
      NodeType: db.t4g.small
      Port: !Ref MemoryDBRedisPort
      SubnetGroupName: !Ref MemoryDBSubnetGroup
      SecurityGroupIds:
        - !Ref AnyscaleSecurityGroup
      EngineVersion: "7.0"
      ParameterGroupName: !Ref MemoryDBParameterGroup
      TLSEnabled: true
      Tags:
        - Key: anyscale-cloud-id
          Value: !Ref CloudID

Outputs:
  MemoryDB:
    Description: MemoryDB cluster
    Value:
      Fn::ToJsonString:
        arn: !GetAtt MemoryDB.ARN
        ClusterEndpointAddress: !GetAtt MemoryDB.ClusterEndpoint.Address

"""
    )


@pytest.mark.parametrize(
    (
        "stack_version_match",
        "parameter_up_to_date",
        "has_role_drift",
        "resolve_drift_failed",
    ),
    [
        pytest.param(False, False, False, False, id="happy-path"),
        pytest.param(True, False, False, False, id="version-match"),
        pytest.param(False, True, False, False, id="parameters-up-to-date"),
        pytest.param(False, False, True, False, id="has-role-drift"),
        pytest.param(False, False, True, True, id="resolve-drift-failed"),
    ],
)
def test_update_iam_role(
    stack_version_match: bool,
    parameter_up_to_date: bool,
    has_role_drift: bool,
    resolve_drift_failed: bool,
    capsys,
):
    region = "us-west-2"
    mock_cfn_id = "mock_id"
    mock_handler = Mock()
    mock_handler.get_cloudformation_stack = MagicMock(Parameters=Mock())
    mock_handler.detect_drift = Mock()
    mock_handler.resolve_drift = Mock(return_value=not resolve_drift_failed)
    mock_handler.update_cloudformation_stack = Mock()
    mock_handler.get_template_body = Mock(return_value="mock_template")

    mock_validate_stack_version = Mock(return_value=not stack_version_match)
    mock_is_template_policy_documents_up_to_date = Mock(
        return_value=parameter_up_to_date
    )
    mock_generate_updated_parameters_and_template = Mock(return_value=(Mock(), Mock()))
    mock_confirm = Mock()
    with patch.multiple(
        "anyscale.utils.cloud_update_utils",
        AWSCloudformationHandler=Mock(return_value=mock_handler),
        validate_stack_version=mock_validate_stack_version,
        is_template_policy_documents_up_to_date=mock_is_template_policy_documents_up_to_date,
        extract_cross_account_iam_role_drift=Mock(
            return_value=MagicMock(LogicalResourceId="mock") if has_role_drift else None
        ),
        generate_updated_parameters_and_template=mock_generate_updated_parameters_and_template,
        confirm=mock_confirm,
    ):
        update_iam_role(region, mock_cfn_id, CloudSetupLogger(), True)
        mock_validate_stack_version.assert_called_once()
        _, stdout = capsys.readouterr()

        if stack_version_match:
            mock_is_template_policy_documents_up_to_date.assert_not_called()
            assert "Cloud is already up-to-date." in stdout
        elif parameter_up_to_date:
            mock_is_template_policy_documents_up_to_date.assert_called_once()
            mock_handler.detect_drift.assert_not_called()
            assert "No inline policy changes" in stdout
        else:
            mock_is_template_policy_documents_up_to_date.assert_called_once()
            mock_handler.detect_drift.assert_called_once()
            mock_handler.get_template_body.assert_called_once()
            mock_generate_updated_parameters_and_template.assert_called_once()
            mock_handler.update_cloudformation_stack.assert_called_once()

            if has_role_drift:
                assert "Drfits detected" in stdout
                mock_handler.resolve_drift.assert_called_once()
                if resolve_drift_failed:
                    assert mock_confirm.call_count == 2
                else:
                    mock_confirm.assert_called_once()
            else:
                mock_handler.resolve_drift.assert_not_called()
                mock_confirm.assert_not_called()


@pytest.mark.parametrize("memorydb_exists", [True, False])
def test_get_or_create_memorydb(memorydb_exists: bool):
    mock_handler = Mock()
    mock_stack = MagicMock(Parameters=[])
    mock_template = "mock_template"
    if memorydb_exists:
        mock_template += " AWS::MemoryDB::Cluster"

    mock_handler.get_cloudformation_stack = Mock(return_value=mock_stack)
    mock_handler.get_template_body = Mock(return_value=mock_template)
    mock_handler.update_cloudformation_stack = Mock()
    mock_memorydb_id = "mock_id"
    mock_handler.get_resource = Mock(
        return_value={"PhysicalResourceId": mock_memorydb_id}
    )

    mock_generate_updated_parameters_and_template = Mock(return_value=(Mock(), Mock()))
    mock_update_template_with_memorydb = Mock()

    with patch.multiple(
        "anyscale.utils.cloud_update_utils",
        AWSCloudformationHandler=Mock(return_value=mock_handler),
        generate_updated_parameters_and_template=mock_generate_updated_parameters_and_template,
        update_template_with_memorydb=mock_update_template_with_memorydb,
        modify_memorydb_parameter_group=Mock(),
    ):
        result = get_or_create_memorydb(
            "mock_stack_name", "mock_region", 2, CloudSetupLogger(), True
        )
        assert result == mock_memorydb_id
        if memorydb_exists:
            mock_handler.update_cloudformation_stack.assert_not_called()
            mock_generate_updated_parameters_and_template.assert_not_called()
            mock_update_template_with_memorydb.assert_not_called()
            mock_handler.get_resource.assert_called_once()
        else:
            mock_handler.update_cloudformation_stack.assert_called_once()
            mock_generate_updated_parameters_and_template.assert_called_once()
            mock_update_template_with_memorydb.assert_called_once()
            assert mock_handler.get_resource.call_count == 2
