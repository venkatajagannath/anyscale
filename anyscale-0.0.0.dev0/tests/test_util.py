import json
import os
import re
import time
from typing import Any, Dict
from unittest.mock import Mock, patch

import boto3
from botocore.exceptions import ClientError
from click import ClickException
from moto import mock_ec2
from packaging import version
import pytest

from anyscale.aws_iam_policies import (
    ANYSCALE_IAM_PERMISSIONS_EC2_STEADY_STATE,
    DEFAULT_RAY_IAM_ASSUME_ROLE_POLICY,
    get_anyscale_aws_iam_assume_role_policy,
)
from anyscale.client.openapi_client.models import CloudAnalyticsEventCloudResource
from anyscale.conf import MINIMUM_RAY_VERSION
from anyscale.util import (
    _check_python_version,
    _get_memorydb_cluster_config,
    _get_subnet,
    _ray_version_major_minor,
    _update_external_ids_for_policy,
    contains_control_plane_role,
    DEFAULT_RAY_VERSION,
    extract_versions_from_image_name,
    filter_actions_from_policy_document,
    get_cluster_model_for_current_workspace,
    get_latest_ray_version,
    get_ray_and_py_version_for_default_cluster_env,
    poll,
    populate_unspecified_cluster_configs,
    prepare_cloudformation_template,
    sleep_till,
    str_data_size,
    updating_printer,
    verify_data_plane_role_assume_role_policy,
)
from anyscale.utils.cloud_utils import CloudSetupError
from anyscale.utils.name_utils import gen_valid_name
from backend.server.common.utils.constants import NAME_VALIDATION_REGEX_PATTERN


def test_updating_printer() -> None:
    out = ""

    def mock_print(
        string: str, *args: Any, end: str = "\n", flush: bool = False, **kwargs: Any
    ) -> None:
        nonlocal out
        out += string
        out += end

    with patch("anyscale.util.print", new=mock_print), patch(
        "shutil.get_terminal_size"
    ) as get_terminal_size_mock:
        get_terminal_size_mock.return_value = (10, 24)
        with updating_printer() as print_status:
            print_status("Step 1")
            print_status("Step 2")
            print_status("Step 3")

    assert out == (
        "\r          \r"
        "Step 1"
        "\r          \r"
        "Step 2"
        "\r          \r"
        "Step 3"
        "\r          \r"
    )


def test_updating_printer_multiline() -> None:
    out = ""

    def mock_print(
        string: str, *args: Any, end: str = "\n", flush: bool = False, **kwargs: Any
    ) -> None:
        nonlocal out
        out += string
        out += end

    with patch("anyscale.util.print", new=mock_print), patch(
        "shutil.get_terminal_size"
    ) as get_terminal_size_mock:
        get_terminal_size_mock.return_value = (10, 24)
        with updating_printer() as print_status:
            print_status("Step 1\nExtra stuff")
            print_status("ExtraLongLine12345")
            print_status("ExtraLongLine12345\nExtra stuff")
            print_status("Step 3")

    assert out == (
        "\r          \r"
        "Step 1..."
        "\r          \r"
        "ExtraLo..."
        "\r          \r"
        "ExtraLo..."
        "\r          \r"
        "Step 3"
        "\r          \r"
    )


STATEMENT_TEMPLATE = {
    "Action": "sts:AssumeRole",
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::ACCT_ID:root"},
}


@pytest.mark.parametrize(
    ("statement_policy", "expected_conditions"),
    [
        pytest.param(
            [STATEMENT_TEMPLATE],
            [{"StringEquals": {"sts:ExternalId": ["new_id"]}}],
            id="OneStatement,NoPrior",
        ),
        pytest.param(
            [STATEMENT_TEMPLATE, STATEMENT_TEMPLATE],
            [{"StringEquals": {"sts:ExternalId": ["new_id"]}}] * 2,
            id="TwoStatements,NoPrior",
        ),
        pytest.param(
            [
                {
                    "Condition": {"StringEquals": {"sts:ExternalId": "old_id"}},
                    **STATEMENT_TEMPLATE,  # type: ignore
                }
            ],
            [{"StringEquals": {"sts:ExternalId": ["old_id", "new_id"]}}],
            id="OneStatement,OnePriorExternal",
        ),
        pytest.param(
            [
                {
                    "Condition": {"StringEquals": {"sts:ExternalId": "old_id"}},
                    **STATEMENT_TEMPLATE,  # type: ignore
                },
                STATEMENT_TEMPLATE,
            ],
            [
                {"StringEquals": {"sts:ExternalId": ["old_id", "new_id"]}},
                {"StringEquals": {"sts:ExternalId": ["new_id"]}},
            ],
            id="TwoStatements,OnePriorExternal",
        ),
        pytest.param(
            [
                {
                    "Condition": {"StringNotEquals": {"sts:ExternalId": "old_id"}},
                    **STATEMENT_TEMPLATE,  # type: ignore
                },
                STATEMENT_TEMPLATE,
            ],
            [
                {
                    "StringEquals": {"sts:ExternalId": ["new_id"]},
                    "StringNotEquals": {"sts:ExternalId": "old_id"},
                },
            ],
            id="OneStatemnt,OtherCondition",
        ),
    ],
)
def test_update_external_ids_for_policy(statement_policy, expected_conditions):
    policy_document = {
        "Statement": statement_policy,
        "Version": "2012-10-17",
    }
    new_policy = _update_external_ids_for_policy(policy_document, "new_id")

    for new, expected in zip(new_policy["Statement"], expected_conditions):
        assert new["Condition"] == expected


@pytest.mark.parametrize(
    ("image_name", "expected", "exception_substr"),
    [
        ("anyscale/ray-ml:1.11.1-py38-gpu", ("py38", "1.11.1"), None),
        ("anyscale/ray:1.12-py37-cpu", ("py37", "1.12"), None),
        ("anyscale/ray:1.12-py37", ("py37", "1.12"), None),
        ("anyscale/ray:1.12py37", None, "got 1.12py37"),
    ],
)
def test_extract_versions_from_image_name(image_name, expected, exception_substr):
    if exception_substr is not None:
        with pytest.raises(ValueError) as exc_info:
            extract_versions_from_image_name(image_name)
        assert exception_substr in str(exc_info.value)
    else:
        python_version, ray_version = extract_versions_from_image_name(image_name)
        assert (python_version, ray_version) == expected


@pytest.mark.parametrize(
    ("ray_version", "expected", "exception_substr"),
    [
        ("1.12", (1, 12), None),
        ("0.0", (0, 0), None),
        ("0:0", (0, 0), "unexpected"),
        ("112", (0, 0), "unexpected"),
        ("", (0, 0), "unexpected"),
        ("1.x", (0, 0), "unexpected"),
        ("0x10.12", (0, 0), "unexpected"),
    ],
)
def test_ray_version_major_minor(ray_version, expected, exception_substr):
    if exception_substr is not None:
        with pytest.raises(Exception) as exc_info:  # noqa: PT011
            _ray_version_major_minor(ray_version)
        assert exception_substr in str(exc_info.value)
    else:
        got = _ray_version_major_minor(ray_version)
        assert got == expected


@pytest.mark.parametrize(
    ("python_version", "exception_substr"),
    [
        ("py36", None),
        ("py37", None),
        ("py38", None),
        ("py39", None),
        ("py10", "got py10"),
        ("py3.6", "got py3.6"),
        ("py3", "got py3."),
        ("py35", "got py35"),
    ],
)
def test_python_version_major_minor(python_version, exception_substr):
    if exception_substr is not None:
        with pytest.raises(Exception) as exc_info:  # noqa: PT011
            _check_python_version(python_version)
        assert exception_substr in str(exc_info.value)
    else:
        _check_python_version(python_version)


def test_poll():
    """Test the poll function."""

    end_time = time.time() + 0.5
    sleep_till(end_time)
    assert time.time() == pytest.approx(end_time)

    # This should poll forever
    count = 0
    start_time = time.time()
    for i in poll(0.01):
        count += 1
        assert count == i
        if count > 100:
            break
    assert count == 101
    assert time.time() == pytest.approx(start_time + 1.01)

    # Assert we stop iterating at max iter
    expected_i = 1
    for i in poll(0.01, max_iter=5):
        assert i == expected_i
        expected_i += 1
        assert i <= 5


def test_str_data_size():
    assert str_data_size("abcd") == 4

    # Serialized form: '{"hi": "ih"}'
    assert str_data_size(json.dumps({"hi": "ih"})) == 12


@pytest.mark.parametrize("is_anyscale_hosted", [True, False])
def test_prepare_cloudformation_template(is_anyscale_hosted):

    mock_region = "us-east-1"
    mock_cfn_stack_name = "mock_cfn_stack_name"
    mock_cloud_id = "mock_cloud_id"

    mock_azs = [
        "us-east-1a",
        "us-east-1b",
        "us-east-1c",
        "us-east-1d",
        "us-east-1e",
        "us-east-1f",
    ]

    with patch("anyscale.util.get_availability_zones", new=Mock(return_value=mock_azs)):
        cfn_template = prepare_cloudformation_template(
            mock_region,
            mock_cfn_stack_name,
            mock_cloud_id,
            True,
            is_anyscale_hosted=is_anyscale_hosted,
        )

    # If you make some changes to the prepare_cloudformation_template(), update the
    # cloud_formation_template.txt by commenting out these code. And use `bazelisk run`
    # to update the template (bazelisk run will not use the sandbox so that we have the
    # write permission).
    # with open(f"{os.environ['HOME']}/product/frontend/cli/tests/cloud_formation_template.txt", 'w') as f:
    #     f.write(cfn_template)
    cft_name = "cloud_formation_template.txt"
    if is_anyscale_hosted:
        cft_name = "cloud_formation_template_oa.txt"
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/{cft_name}") as f:
        expected_content = f.read()
    assert cfn_template == expected_content


@pytest.mark.parametrize("request_output", ["mock_latest_version", Exception()])
def test_get_latest_ray_version(request_output):
    if isinstance(request_output, str):
        mock_get = Mock(
            return_value=Mock(
                json=Mock(return_value={"info": {"version": request_output}})
            )
        )
    else:
        mock_get = Mock(side_effect=request_output)

    expected_latest_version = (
        request_output if isinstance(request_output, str) else DEFAULT_RAY_VERSION
    )
    with patch.multiple("anyscale.util.requests", get=mock_get):
        latest_ray_version = get_latest_ray_version()
        assert latest_ray_version == expected_latest_version
    mock_get.assert_called_once_with("https://pypi.org/pypi/ray/json")


@pytest.mark.parametrize(
    "pyversion_param", [["3", "6"], ["3", "7"], ["3", "8"], ["3", "9"]]
)
def test_get_ray_and_py_version_for_default_cluster_env(pyversion_param):
    # TODO(nikita): This test should be run in an environment that has Ray
    # installed, and one that doesn't have Ray installed. The
    # `import ray` statement inside the method cannot be mocked.
    mock_get_latest_ray_version = Mock(return_value="mock_latest_ray_version")
    with patch.multiple(
        "anyscale.util.sys", version_info=pyversion_param
    ), patch.multiple(
        "anyscale.util", get_latest_ray_version=mock_get_latest_ray_version
    ):
        ray_version, pyversion = get_ray_and_py_version_for_default_cluster_env()
    assert pyversion == "".join(str(x) for x in pyversion_param)
    try:
        import ray

        assert version.parse(ray_version) == version.parse(ray.__version__)
        assert version.parse(ray_version) >= version.parse(MINIMUM_RAY_VERSION)
    except ImportError:
        assert ray_version == "mock_latest_ray_version"


test_workspace_cluster = Mock()
test_workspace_cluster.name = "workspace-cluster-test_name"
test_workspace_cluster.project_id = "test_project_id"
test_workspace_cluster.cluster_environment_build_id = "test_build_id"
test_workspace_cluster.cluster_compute_id = "test_compute_config_id"


def test_get_cluster_model_for_current_workspace():
    api_client_result_mock = Mock()
    api_client_result_mock.result = test_workspace_cluster

    mock_base_api_client = Mock()
    mock_base_api_client.get_cluster = Mock(return_value=api_client_result_mock)

    # If workspace_id or session_id is missing in the env, should return None.
    assert get_cluster_model_for_current_workspace(mock_base_api_client) is None
    mock_base_api_client.get_cluster.assert_not_called()

    with patch.dict(
        os.environ,
        {"ANYSCALE_EXPERIMENTAL_WORKSPACE_ID": "test_workspace_id",},
        clear=True,
    ):
        assert get_cluster_model_for_current_workspace(mock_base_api_client) is None
        mock_base_api_client.get_cluster.assert_not_called()

    with patch.dict(
        os.environ, {"ANYSCALE_SESSION_ID": "test_session_id",}, clear=True,
    ):
        assert get_cluster_model_for_current_workspace(mock_base_api_client) is None
        mock_base_api_client.get_cluster.assert_not_called()

    # If both workspace_id and session_id are present in the env, should call the API
    # and return the cluster model.
    with patch.dict(
        os.environ,
        {
            "ANYSCALE_EXPERIMENTAL_WORKSPACE_ID": "test_workspace_id",
            "ANYSCALE_SESSION_ID": "test_session_id",
        },
        clear=True,
    ):
        assert (
            get_cluster_model_for_current_workspace(mock_base_api_client)
            == test_workspace_cluster
        )
        mock_base_api_client.get_cluster.assert_called_once_with("test_session_id")


@pytest.mark.parametrize(
    ("input_config", "output_config"),
    [
        # Test all fields being defaulted.
        (
            {"name": "test_job"},
            {
                "name": "test_job",
                "project_id": "test_project_id",
                "build_id": "test_build_id",
                "compute_config_id": "test_compute_config_id",
            },
        ),
        # Test no fields being defaulted.
        (
            {
                "name": "test_job",
                "project_id": "existing_project_id",
                "build_id": "existing_build_id",
                "compute_config_id": "existing_compute_config_id",
            },
            {
                "name": "test_job",
                "project_id": "existing_project_id",
                "build_id": "existing_build_id",
                "compute_config_id": "existing_compute_config_id",
            },
        ),
        # If project_id is specified, it shouldn't be overwritten.
        (
            {"name": "test_job", "project_id": "existing_project_id"},
            {
                "name": "test_job",
                "project_id": "existing_project_id",
                "build_id": "test_build_id",
                "compute_config_id": "test_compute_config_id",
            },
        ),
        # If cluster_env or build_id are specified, they shouldn't be changed.
        (
            {"name": "test_job", "cluster_env": "existing_cluster_env"},
            {
                "name": "test_job",
                "project_id": "test_project_id",
                "cluster_env": "existing_cluster_env",
                "compute_config_id": "test_compute_config_id",
            },
        ),
        (
            {"name": "test_job", "build_id": "existing_build_id"},
            {
                "name": "test_job",
                "project_id": "test_project_id",
                "build_id": "existing_build_id",
                "compute_config_id": "test_compute_config_id",
            },
        ),
        # If cloud, compute_config, or compute_config_id are specified, they shouldn't be changed.
        (
            {"name": "test_job", "cloud": "test_cloud"},
            {
                "name": "test_job",
                "project_id": "test_project_id",
                "build_id": "test_build_id",
                "cloud": "test_cloud",
            },
        ),
        (
            {"name": "test_job", "compute_config": "test_compute_config"},
            {
                "name": "test_job",
                "project_id": "test_project_id",
                "build_id": "test_build_id",
                "compute_config": "test_compute_config",
            },
        ),
        (
            {"name": "test_job", "compute_config_id": "existing_compute_config_id"},
            {
                "name": "test_job",
                "project_id": "test_project_id",
                "build_id": "test_build_id",
                "compute_config_id": "existing_compute_config_id",
            },
        ),
    ],
)
def test_populate_unspecified_cluster_configs(
    input_config: Dict[str, str], output_config: Dict[str, str]
):
    assert (
        populate_unspecified_cluster_configs(input_config, test_workspace_cluster)
        == output_config
    )


def test_populate_unspecified_cluster_configs_populate_name():
    base_expected_output = {
        "project_id": "test_project_id",
        "build_id": "test_build_id",
        "compute_config_id": "test_compute_config_id",
    }

    # If a name is passed in, it shouldn't be overwritten.
    assert populate_unspecified_cluster_configs(
        {"name": "existing_name"}, test_workspace_cluster, populate_name=True
    ) == {"name": "existing_name", **base_expected_output}

    # If a name is not passed in and populate_name=False, it shouldn't be overwritten.
    assert populate_unspecified_cluster_configs({}, test_workspace_cluster,) == {
        **base_expected_output
    }

    # If a name is not passed in, it should default to the cluster name stripped of the workspace prefix.
    assert populate_unspecified_cluster_configs(
        {}, test_workspace_cluster, populate_name=True
    ) == {"name": "test_name", **base_expected_output}

    # That that missing the workspace prefix in the cluster name picks it up as-is.
    test_workspace_cluster_no_name_prefix = Mock()
    test_workspace_cluster_no_name_prefix.name = "oopsies_unexpected_name"
    test_workspace_cluster_no_name_prefix.project_id = "test_project_id"
    test_workspace_cluster_no_name_prefix.cluster_environment_build_id = "test_build_id"
    test_workspace_cluster_no_name_prefix.cluster_compute_id = "test_compute_config_id"
    assert populate_unspecified_cluster_configs(
        {}, test_workspace_cluster_no_name_prefix, populate_name=True
    ) == {"name": "oopsies_unexpected_name", **base_expected_output}


@pytest.mark.parametrize(
    ("policy_document", "expected_actions"),
    [
        pytest.param(
            ANYSCALE_IAM_PERMISSIONS_EC2_STEADY_STATE,
            {
                "iam:PassRole",
                "iam:CreateServiceLinkedRole",
                "iam:GetInstanceProfile",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeInstanceTypes",
                "ec2:DescribeRegions",
                "ec2:DescribeAccountAttributes",
                "ec2:DescribeInstances",
                "ec2:DescribeSubnets",
                "ec2:DescribeRouteTables",
                "ec2:DescribeSecurityGroups",
                "ec2:RunInstances",
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:TerminateInstances",
                "ec2:CreateTags",
                "ec2:DeleteTags",
                "ec2:CancelSpotInstanceRequests",
                "ec2:ModifyImageAttribute",
                "ec2:ModifyInstanceAttribute",
                "ec2:RequestSpotInstances",
                "ec2:AttachVolume",
                "ec2:CreateVolume",
                "ec2:DescribeVolumes",
                "ec2:AssociateIamInstanceProfile",
                "ec2:DisassociateIamInstanceProfile",
                "ec2:ReplaceIamInstanceProfileAssociation",
                "ec2:CreatePlacementGroup",
                "ec2:AllocateAddress",
                "ec2:ReleaseAddress",
                "ec2:DescribeIamInstanceProfileAssociations",
                "ec2:DescribeInstanceStatus",
                "ec2:DescribePlacementGroups",
                "ec2:DescribePrefixLists",
                "ec2:DescribeReservedInstancesOfferings",
                "ec2:DescribeSpotInstanceRequests",
                "ec2:DescribeSpotPriceHistory",
                "elasticfilesystem:DescribeMountTargets",
            },
        ),
        pytest.param(DEFAULT_RAY_IAM_ASSUME_ROLE_POLICY, {"sts:AssumeRole"},),
        pytest.param(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": ["ec2.amazonaws.com"]},
                        "Action": ["sts:AssumeRole", "sts:AssumeRole"],
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": ["ec2.amazonaws.com"]},
                        "Action": ["sts:AssumeRole", "sts:AssumeRole"],
                    },
                ],
            },
            {"sts:AssumeRole"},
        ),
        pytest.param(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Deny",
                        "Principal": {"Service": ["ec2.amazonaws.com"]},
                        "Action": ["sts:AssumeRole", "sts:AssumeRole"],
                    },
                    {
                        "Effect": "Deny",
                        "Principal": {"Service": ["ec2.amazonaws.com"]},
                        "Action": ["sts:AssumeRole", "sts:AssumeRole"],
                    },
                ],
            },
            set(),
        ),
    ],
)
def test_filter_actions_from_policy_document(policy_document, expected_actions):
    actions = filter_actions_from_policy_document(policy_document=policy_document)
    assert actions == expected_actions


@pytest.mark.parametrize(
    ("assume_role_policy_document", "expected_result"),
    [
        pytest.param(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "000000"},
                        "Action": "sts:AssumeRole",
                    },
                ],
            },
            True,
        ),
        pytest.param(
            get_anyscale_aws_iam_assume_role_policy(anyscale_aws_account="000000"),
            True,
        ),
        pytest.param(
            {
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": [
                                "arn:aws:iam::other_account",
                                "arn:aws:iam::000000:root",
                            ]
                        },
                        "Action": "sts:AssumeRole",
                    },
                ],
            },
            True,
        ),
        pytest.param(
            {
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": [
                                "arn:aws:iam::other_account",
                                "arn:aws:iam::another_account:root",
                            ]
                        },
                        "Action": "sts:AssumeRole",
                    },
                ],
            },
            False,
        ),
        pytest.param(
            {
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "arn:aws:iam::000000:root"},
                        "Action": "sts:AssumeRole",
                    },
                ],
            },
            False,
        ),
    ],
)
def test_contains_control_plane_role(assume_role_policy_document, expected_result):
    result = contains_control_plane_role(
        assume_role_policy_document=assume_role_policy_document,
        anyscale_aws_account="000000",
    )
    assert result == expected_result


@pytest.mark.parametrize(
    ("assume_role_policy_document", "expected_result"),
    [
        pytest.param(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "000000"},
                        "Action": "sts:AssumeRole",
                    },
                ],
            },
            False,
        ),
        pytest.param(
            {
                "Statement": [
                    {
                        "Effect": "Reject",
                        "Principal": {
                            "AWS": [
                                "arn:aws:iam::other_account",
                                "arn:aws:iam::000000:root",
                            ]
                        },
                        "Action": "sts:AssumeRole",
                    },
                ],
            },
            False,
        ),
        pytest.param(
            {
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": [
                                "arn:aws:iam::other_account",
                                "arn:aws:iam::another_account:root",
                            ]
                        },
                        "Action": "sts:AssumeRole",
                    },
                ],
            },
            False,
        ),
        pytest.param(
            {
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com", "AWS": "000000"},
                        "Action": "sts:AssumeRole",
                    },
                ],
            },
            True,
        ),
    ],
)
def test_verify_data_plane_role_assume_role_policy(
    assume_role_policy_document, expected_result
):
    result = verify_data_plane_role_assume_role_policy(
        assume_role_policy_document=assume_role_policy_document
    )
    assert result == expected_result


def test_gen_valid_name():
    name_without_prefiex = gen_valid_name()
    name_with_prefiex = gen_valid_name("test prefix name")

    assert re.match(NAME_VALIDATION_REGEX_PATTERN, name_without_prefiex) is not None
    assert re.match(NAME_VALIDATION_REGEX_PATTERN, name_with_prefiex) is not None


@pytest.mark.parametrize(
    ("describe_cluster_response", "raise_exception", "exception_substr"),
    [
        pytest.param({}, True, "does not exist"),
        pytest.param({"Clusters": [{}]}, True, "does not exist"),
        pytest.param(
            {
                "Clusters": [
                    {
                        "Status": "creating",
                        "ARN": "mock_cluster_arn",
                        "ClusterEndpoint": {
                            "Address": "mock_cluster_endpoint_address",
                            "Port": 6379,
                        },
                    }
                ]
            },
            True,
            "not currently available.",
        ),
        pytest.param(
            {
                "Clusters": [
                    {
                        "Status": "available",
                        "ARN": "mock_cluster_arn",
                        "ClusterEndpoint": {
                            "Address": "mock_cluster_endpoint_address",
                            "Port": 6379,
                        },
                    }
                ]
            },
            False,
            "",
        ),
    ],
)
def test_get_memorydb_cluster_config(
    describe_cluster_response, raise_exception, exception_substr
):

    mock_memorydb_cluster_id = "mock_memorydb_cluster_id"
    mock_region = "mock_region"
    mock_memorydb_client = Mock(
        describe_clusters=Mock(return_value=describe_cluster_response)
    )
    mock_boto3 = Mock(client=Mock(return_value=mock_memorydb_client))

    with patch("anyscale.util.boto3", new=mock_boto3):
        if raise_exception:
            with pytest.raises(ClickException) as exc_info:
                _get_memorydb_cluster_config(
                    mock_memorydb_cluster_id, mock_region, Mock()
                )
            assert exception_substr in str(exc_info.value)
        else:
            cluster_config = _get_memorydb_cluster_config(
                mock_memorydb_cluster_id, mock_region, Mock()
            )
            assert cluster_config.id == "mock_cluster_arn"
            assert (
                cluster_config.endpoint == "rediss://mock_cluster_endpoint_address:6379"
            )


@pytest.mark.parametrize(
    ("cloud_region", "subnet_region", "success"),
    [
        pytest.param("us-east-1", "us-east-1", True),
        pytest.param("us-east-1", "us-east-2", False),
    ],
)
@mock_ec2
def test_get_subnet(cloud_region, subnet_region, success):
    ec2 = boto3.client("ec2", region_name=subnet_region)
    vpc = ec2.create_vpc(CidrBlock="10.0.0.0/16")
    subnet = ec2.create_subnet(
        VpcId=vpc["Vpc"]["VpcId"],
        CidrBlock="10.0.0.0/24",
        AvailabilityZone=f"{subnet_region}a",
    )
    subnet_arn = subnet["Subnet"]["SubnetArn"]

    if not success:
        mock_subnet = Mock(
            return_value=Mock(
                load=Mock(
                    side_effect=ClientError(
                        {
                            "Error": {
                                "Code": "InvalidSubnetID.NotFound",
                                "Message": "Not Found",
                            }
                        },
                        "describe_subnets",
                    )
                )
            )
        )

    else:
        mock_subnet = Mock()

    mock_ec2_resource = Mock(Subnet=mock_subnet)

    mock_logger = Mock()

    with patch("anyscale.util._resource", new=Mock(return_value=mock_ec2_resource)):
        if success:
            _get_subnet(subnet_arn, cloud_region, mock_logger)
        else:
            with pytest.raises(ClickException) as exc_info:
                _get_subnet(subnet_arn, cloud_region, mock_logger)
            assert "does not exist. Please make sur" in str(exc_info.value)
            mock_logger.log_resource_error.assert_called_with(
                CloudAnalyticsEventCloudResource.AWS_SUBNET,
                CloudSetupError.RESOURCE_NOT_FOUND,
            )

    mock_subnet.assert_called_once_with(subnet_arn)
