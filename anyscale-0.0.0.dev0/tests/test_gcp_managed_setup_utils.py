import re
from unittest.mock import Mock, patch

from click import ClickException
from google.cloud.certificate_manager_v1.types import (
    Certificate,
    CertificateMap,
    CertificateMapEntry,
)
import pytest
import yaml

from anyscale.cli_logger import BlockLogger, CloudSetupLogger
from anyscale.utils.gcp_managed_setup_utils import (
    append_project_iam_policy,
    configure_firewall_policy,
    create_anyscale_aws_provider,
    create_workload_identity_pool,
    delete_gcp_deployment,
    delete_gcp_tls_certificates,
    delete_workload_identity_pool,
    enable_project_apis,
    GCPDeployment,
    generate_deployment_manager_config,
    get_anyscale_gcp_access_service_acount,
    get_deployment_config,
    get_deployment_resource,
    get_deployment_resources,
    get_or_create_memorystore_gcp,
    get_project_number,
    get_workload_identity_pool,
    remove_firewall_policy_associations,
    update_deployment,
    update_deployment_with_bucket_only,
    wait_for_operation_completion,
)


@pytest.mark.parametrize(
    ("response", "expected_error_message"),
    [
        pytest.param(("200 OK", "project_get.json"), None, id="succeed",),
        pytest.param(
            ("403 Forbidden", None),
            "Error occurred when trying to access the project",
            id="error",
        ),
    ],
)
def test_get_project_number(setup_mock_server, response, expected_error_message):
    factory, tracker = setup_mock_server
    mock_project_id = "anyscale-bridge-deadbeef"
    mock_project_name = "projects/112233445566"
    tracker.reset({".*": [response]})
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            get_project_number(factory, mock_project_id)
        e.match(expected_error_message)
    else:
        assert get_project_number(factory, mock_project_id) == mock_project_name


@pytest.mark.parametrize(
    ("responses", "expected_error_message"),
    [
        pytest.param(
            [
                ("200 OK", "project_get_iam_policy.json"),
                ("200 OK", "project_set_iam_policy.json"),
            ],
            None,
            id="no-role-in-bindings",
        ),
        pytest.param(
            [
                ("200 OK", "project_get_iam_policy_role_exists.json"),
                ("200 OK", "project_set_iam_policy_role_exists.json"),
            ],
            None,
            id="member-not-in-role",
        ),
        pytest.param(
            [
                ("200 OK", "project_set_iam_policy.json"),
                ("200 OK", "project_set_iam_policy.json"),
            ],
            None,
            id="member-already-exists",
        ),
        pytest.param(
            [("400 Bad Request", None)],
            "Failed to set IAM policy for project",
            id="member not found",
        ),
        pytest.param(
            [("403 Forbidden", None)],
            "Failed to set IAM policy for project",
            id="project-not-found",
        ),
    ],
)
def test_append_project_iam_policy(
    setup_mock_server, responses, expected_error_message
):
    factory, tracker = setup_mock_server
    tracker.reset({".*": responses})
    mock_project_id = "mock-project"
    mock_role = "roles/iam.securityAdmin"
    mock_member = "serviceAccount:112233445566@cloudservices.gserviceaccount.com"
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            append_project_iam_policy(factory, mock_project_id, mock_role, mock_member)
        e.match(expected_error_message)
    else:
        updated_policy = append_project_iam_policy(
            factory, mock_project_id, mock_role, mock_member
        )
        bingdings = updated_policy.bindings
        assert mock_role in [binding.role for binding in bingdings]
        assert mock_member in [
            member
            for binding in bingdings
            if binding.role == mock_role
            for member in binding.members
        ]


@pytest.mark.parametrize(
    ("response", "expected_error_message"),
    [
        pytest.param(("200 OK", "enable_api_operation.json"), None, id="succeed",),
        pytest.param(
            ("403 Forbidden", None), "Failed to enable APIs for project", id="error",
        ),
    ],
)
@pytest.mark.parametrize("enable_head_node_fault_tolerance", [True, False])
def test_enable_project_apis(
    setup_mock_server,
    response,
    expected_error_message,
    enable_head_node_fault_tolerance,
):
    factory, tracker = setup_mock_server
    mock_project_id = "mock-project"
    tracker.reset({".*": [response]})
    if expected_error_message:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ), pytest.raises(ClickException) as e:
            enable_project_apis(
                factory,
                mock_project_id,
                CloudSetupLogger(),
                enable_head_node_fault_tolerance,
            )
        e.match(expected_error_message)
    else:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            assert (
                enable_project_apis(
                    factory,
                    mock_project_id,
                    CloudSetupLogger(),
                    enable_head_node_fault_tolerance,
                )
                is None
            )


@pytest.mark.parametrize(
    ("response", "expected_error_message", "pool_exists"),
    [
        pytest.param(
            ("200 OK", "get_workload_identity_pool.json"), None, True, id="succeed",
        ),
        pytest.param(("404 Not Found", None), None, False, id="NotFound"),
        pytest.param(
            ("403 Forbidden", None),
            "Failed to get Workload Identity Provider Pool.",
            True,
            id="error",
        ),
    ],
)
def test_get_workload_identity_pool(
    setup_mock_server, response, pool_exists, expected_error_message
):
    factory, tracker = setup_mock_server
    mock_project_id = "anyscale-bridge-deadbeef"
    mock_pool_id = "mock-pool-id"
    tracker.reset({".*": [response]})
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            get_workload_identity_pool(factory, mock_project_id, mock_pool_id)
        e.match(expected_error_message)
    elif pool_exists:
        assert (
            get_workload_identity_pool(factory, mock_project_id, mock_pool_id)
            == mock_pool_id
        )
    else:
        assert (
            get_workload_identity_pool(factory, mock_project_id, mock_pool_id) is None
        )


@pytest.mark.parametrize(
    ("response", "expected_error_message", "service_account_exists"),
    [
        pytest.param(("200 OK", "get_service_account.json"), None, True, id="succeed",),
        pytest.param(("404 Not Found", None), None, False, id="NotFound"),
        pytest.param(
            ("403 Forbidden", None), "Failed to get service account: ", True, id="error"
        ),
    ],
)
def test_get_anyscale_gcp_access_service_acount(
    setup_mock_server, response, service_account_exists, expected_error_message
):
    factory, tracker = setup_mock_server
    mock_service_account = (
        "anyscale-access@anyscale-bridge-deadbeef.iam.gserviceaccount.com"
    )
    tracker.reset({".*": [response]})
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            get_anyscale_gcp_access_service_acount(factory, mock_service_account)
        e.match(expected_error_message)
    elif service_account_exists:
        assert (
            get_anyscale_gcp_access_service_acount(factory, mock_service_account)
            == mock_service_account
        )
    else:
        assert (
            get_anyscale_gcp_access_service_acount(factory, mock_service_account)
            is None
        )


@pytest.mark.parametrize(
    ("response", "expected_log_message"),
    [
        pytest.param(
            ("200 OK", "create_workload_identity_pool.json"), None, id="succeed",
        ),
        pytest.param(("409 conflict", None), "already exists", id="pool-exists",),
        pytest.param(("418 I'm a teapot", None), "Error occurred", id="error",),
    ],
)
def test_create_workload_identity_pool(
    setup_mock_server, response, expected_log_message, capsys
):
    factory, tracker = setup_mock_server
    mock_project_id = "anyscale-bridge-deadbeef"
    mock_project_number = "123456789"
    mock_pool_id = "mock-pool-id"
    display_name = "mock pool"
    description = "mock provider pool"
    tracker.reset({".*": [response]})
    if expected_log_message:
        with pytest.raises(ClickException) as e, patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            create_workload_identity_pool(
                factory,
                mock_project_id,
                mock_pool_id,
                BlockLogger(),
                display_name,
                description,
            )
        e.match("Failed to create Workload Identity Provider Pool")
        _, err = capsys.readouterr()
        assert expected_log_message in err

    else:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            assert (
                create_workload_identity_pool(
                    factory,
                    mock_project_id,
                    mock_pool_id,
                    BlockLogger(),
                    display_name,
                    description,
                )
                == f"projects/{mock_project_number}/locations/global/workloadIdentityPools/{mock_pool_id}"
            )


@pytest.mark.parametrize(
    ("response", "expected_error_message"),
    [
        pytest.param(
            ("200 OK", "create_workload_identity_provider.json"), None, id="succeed",
        ),
        pytest.param(("409 conflict", None), "already exists", id="pool-exists",),
        pytest.param(("404 Not Found", None), "Error occurred", id="error",),
    ],
)
def test_create_anyscale_aws_provider(
    setup_mock_server, response, expected_error_message, capsys
):
    factory, tracker = setup_mock_server
    mock_project_number = "123456789"
    mock_pool_id = f"projects/{mock_project_number}/locations/global/workloadIdentityPools/mock-pool-id"
    mock_provider_id = "mock-provider"
    mock_aws_account = "123456"
    mock_display_name = "mock provider"
    mock_org_id = "mock_org_id"
    tracker.reset({".*": [response]})
    if expected_error_message:
        with pytest.raises(ClickException) as e, patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            create_anyscale_aws_provider(
                factory,
                mock_org_id,
                mock_pool_id,
                mock_provider_id,
                mock_aws_account,
                mock_display_name,
                BlockLogger(),
            )
        e.match("Failed to create Anyscale AWS Workload Identity Provider")
        _, err = capsys.readouterr()
        assert expected_error_message in err
    else:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            assert (
                create_anyscale_aws_provider(
                    factory,
                    mock_org_id,
                    mock_pool_id,
                    mock_provider_id,
                    mock_aws_account,
                    mock_display_name,
                    BlockLogger(),
                )
                == f"{mock_pool_id}/providers/{mock_provider_id}"
            )


@pytest.mark.parametrize(
    ("response", "expected_log_message", "deletion_succeed"),
    [
        pytest.param(
            ("200 OK", "delete_workload_identity_pool.json"),
            "Deleted workload identity pool",
            True,
            id="succeed",
        ),
        pytest.param(
            ("403 Forbidden", None),
            "Error occurred when trying to delete workload identity pool",
            False,
            id="error1",
        ),
        pytest.param(("404 Not Found", None), None, False, id="error2",),
    ],
)
def test_delete_workload_identity_pool(
    setup_mock_server, response, deletion_succeed, expected_log_message, capsys
):
    factory, tracker = setup_mock_server
    mock_project_number = "123456789"
    mock_pool_id = "mock-pool-id"
    mock_pool_name = f"projects/{mock_project_number}/locations/global/workloadIdentityPools/{mock_pool_id}"
    tracker.reset({".*": [response]})
    if deletion_succeed:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            delete_workload_identity_pool(
                factory, mock_pool_name, BlockLogger(),
            )
            _, log = capsys.readouterr()
            assert expected_log_message in log
    elif expected_log_message:
        with pytest.raises(ClickException) as e, patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            delete_workload_identity_pool(
                factory, mock_pool_name, BlockLogger(),
            )
        e.match(expected_log_message)
    else:
        # not found
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            assert (
                delete_workload_identity_pool(factory, mock_pool_name, BlockLogger(),)
                is None
            )


@pytest.mark.parametrize("service_type", ["workload_identity_pool", "provider"])
@pytest.mark.parametrize(
    ("response", "expected_error_message"),
    [
        pytest.param(
            ("200 OK", "create_workload_identity_pool.json"),
            "did not complete within the timeout period",
            id="timeout",
        ),
        pytest.param(("200 OK", "operation_completed.json"), None, id="succeed",),
        pytest.param(
            ("200 OK", "operation_error.json"), "encountered an error", id="error",
        ),
    ],
)
def test_wait_for_operation_completion(
    setup_mock_server, response, expected_error_message, service_type
):
    factory, tracker = setup_mock_server
    mock_project_name = "projects/112233445566"
    mock_pool_id = "mock-pool-id"
    mock_provider_id = "mock-provider"
    if service_type == "workload_identity_pool":
        service = (
            factory.build("iam", "v1").projects().locations().workloadIdentityPools()
        )
        mock_operation_id = f"{mock_project_name}/locations/global/workloadIdentityPools/{mock_pool_id}/operations/mock_operation_id"
    elif service_type == "provider":
        service = (
            factory.build("iam", "v1")
            .projects()
            .locations()
            .workloadIdentityPools()
            .providers()
        )
        mock_operation_id = f"{mock_project_name}/locations/global/workloadIdentityPools/{mock_pool_id}/providers/{mock_provider_id}/operations/mock_operation_id"
    tracker.reset({".*": [response]})
    if expected_error_message:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils.time",
            time=Mock(side_effect=list(range(10))),  # only iterates once
            sleep=Mock(),
        ), pytest.raises(ClickException) as e:
            wait_for_operation_completion(
                service,
                {"name": mock_operation_id},
                "test",
                timeout=2,
                polling_interval=10,
            )
        e.match(expected_error_message)
    else:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils.time",
            time=Mock(side_effect=list(range(10))),
            sleep=Mock(),
        ):
            assert (
                wait_for_operation_completion(
                    service, {"name": mock_operation_id}, "test",
                )
                is None
            )


@pytest.mark.parametrize(
    ("responses", "expected_error_message"),
    [
        pytest.param(
            [
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "associate_firewall_policy.json"),
                ("200 OK", "add_firewall_policy_rule_done.json"),
                ("200 OK", "add_firewall_policy_rule_done.json"),
                ("200 OK", "associate_firewall_policy_done.json"),
            ],
            None,
            id="succeed",
        ),
        pytest.param(
            [
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "associate_firewall_policy.json"),
                ("200 OK", "add_firewall_policy_rule.json"),
            ],
            "Timeout when trying to configure firewall policy",
            id="timeout",
        ),
        pytest.param(
            [
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "associate_firewall_policy.json"),
                ("200 OK", "add_firewall_policy_rule_error.json"),
            ],
            "Failed to configure firewall policy ",
            id="error",
        ),
        pytest.param(
            [("400 Bad Request", None)],
            "Failed to configure firewall policy",
            id="bad-request",
        ),
        pytest.param(
            [
                ("200 OK", "add_firewall_policy_rule.json"),
                ("200 OK", "add_firewall_policy_rule.json"),
                ("404 Not Found", None),
            ],
            "Failed to configure firewall policy",
            id="not-found",
        ),
    ],
)
def test_configure_firewall_policy(
    setup_mock_server, responses, expected_error_message
):
    factory, tracker = setup_mock_server
    mock_project_id = "mock-project"
    mock_vpc_name = "mock-vpc"
    mock_firewall_policy = "mock-fp"
    mock_subnet_cidr = "10.0.0.0/20"
    tracker.reset({".*": responses})
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            configure_firewall_policy(
                factory,
                mock_vpc_name,
                mock_project_id,
                mock_firewall_policy,
                mock_subnet_cidr,
            )
        e.match(expected_error_message)
    else:
        configure_firewall_policy(
            factory,
            mock_vpc_name,
            mock_project_id,
            mock_firewall_policy,
            mock_subnet_cidr,
        )


@pytest.mark.parametrize(
    ("responses", "expected_error_message"),
    [
        pytest.param(
            [("404 Not Found", None)], "Failed to get deployment", id="failed",
        ),
        pytest.param(
            [("200 OK", "deployment_get.json"), ("200 OK", "manifest_get.json")],
            None,
            id="succeed",
        ),
    ],
)
def test_get_deployment_resources(setup_mock_server, responses, expected_error_message):
    factory, tracker = setup_mock_server
    mock_deployment_name = "mock-deployment"
    mock_project_id = "mock-project"
    mock_anyscale_access_service_account_name = "anyscale-access-cld-congtest"
    tracker.reset({".*": responses})
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            get_deployment_resources(
                factory,
                mock_deployment_name,
                mock_project_id,
                mock_anyscale_access_service_account_name,
            )
        e.match(expected_error_message)
    else:
        assert get_deployment_resources(
            factory,
            mock_deployment_name,
            mock_project_id,
            mock_anyscale_access_service_account_name,
        ) == {
            "compute.v1.network": "vpc-cld-congtest",
            "compute.v1.subnetwork": "subnet-cld-congtest",
            "gcp-types/compute-v1:networkFirewallPolicies": "firewall-policy-cld-congtest",
            "filestore_instance": "filestore-cld-congtest",
            "filestore_location": "us-west1",
            "gcp-types/file-v1beta1:projects.locations.instances": "filestore-cld-congtest",
            "storage.v1.bucket": "storage-bucket-cld-congtest",
            "iam.v1.serviceAccount": "instance-cld-congtest",
        }


@pytest.mark.parametrize(
    ("responses", "expected_error_message"),
    [
        pytest.param(
            [("200 OK", "deployment_get.json"), ("200 OK", "deployment_delete.json")],
            None,
            id="no-bucket-delete-succeed",
        ),
        pytest.param(
            [("200 OK", "deployment_get.json"), ("403 Forbidden", None)],
            "Failed to delete deployment",
            id="no-bucket-delete-fail",
        ),
        pytest.param([("404 Not Found", None)], None, id="no-deployment"),
        pytest.param(
            [("403 Forbidden", None)], "Failed to get deployment", id="forbidden"
        ),
    ],
)
def test_delete_gcp_deployment(setup_mock_server, responses, expected_error_message):
    factory, tracker = setup_mock_server
    mock_project_id = "mock-project"
    mock_deployment = "mock-deployment"
    tracker.reset({".*": responses})

    if expected_error_message:

        with pytest.raises(ClickException) as e, patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):
            delete_gcp_deployment(factory, mock_project_id, mock_deployment)
        e.match(expected_error_message)
    else:
        with patch.multiple(
            "anyscale.utils.gcp_managed_setup_utils",
            wait_for_operation_completion=Mock(),
        ):

            assert (
                delete_gcp_deployment(factory, mock_project_id, mock_deployment) is None
            )


def test_update_deployment_with_bucket_only():
    factory = Mock()
    mock_project_id = "mock-project"
    mock_deployment = "mock-deployment"
    mock_fingerprint = "mock"
    mock_config_content = '\nresources:\n- name: vpc-cld-congtest\n  type: compute.v1.network\n  properties:\n    name: vpc-cld-congtest\n    autoCreateSubnetworks: False\n- name: subnet-cld-congtest\n  type: compute.v1.subnetwork\n  properties:\n    name: subnet-cld-congtest\n    ipCidrRange: 10.0.0.0/20\n    region: us-west1\n    network: $(ref.vpc-cld-congtest.selfLink)\n- name: firewall-policy-cld-congtest\n  type: gcp-types/compute-v1:networkFirewallPolicies\n  properties:\n    parentId: projects/mock-project/regions/us-west1\n    name: firewall-policy-cld-congtest\n    description: "firewall policy for Anyscale managed cloud cld-congtest"\n- name: filestore-cld-congtest\n  type: gcp-types/file-v1beta1:projects.locations.instances\n  properties:\n    instanceId: filestore-cld-congtest\n    parent: projects/mock-project/locations/us-west1\n    tier: ENTERPRISE\n    networks:\n      - network: projects/mock-project/global/networks/$(ref.vpc-cld-congtest.name)\n    fileShares:\n      - name: anyscale_fileshare\n        capacityGb: 1024\n- name: storage-bucket-cld-congtest\n  type: storage.v1.bucket\n  properties:\n    location: us-west1\n    storageClass: REGIONAL\n    iamConfiguration:\n      uniformBucketLevelAccess:\n        enabled: True\n      publicAccessPrevention: enforced\n    cors:\n    - origin: ["https://console.anyscale-staging.com"]\n      responseHeader: ["*"]\n      method: ["GET"]\n- name: anyscale-access-cld-congtest\n  type: iam.v1.serviceAccount\n  properties:\n    accountId: anyscale-access-cld-congtest\n    displayName: test anyscale account for managed setup\n    projectId: mock-project\n  accessControl:\n    gcpIamPolicy:\n        bindings:\n        - role: roles/iam.serviceAccountTokenCreator\n          members:\n          - serviceAccount:anyscale-access-cld-congtest@mock-project.iam.gserviceaccount.com \n- name: iam-policy-anyscale-access-project-cld-congtest\n  type: gcp-types/cloudresourcemanager-v1:virtual.projects.iamMemberBinding\n  metadata:\n    dependsOn:\n      - anyscale-access-cld-congtest\n  properties: \n    resource: mock-project\n    role: roles/editor\n    member: "serviceAccount:$(ref.anyscale-access-cld-congtest.email)"\n- name: instance-cld-congtest\n  type: iam.v1.serviceAccount\n  properties:\n    accountId: instance-cld-congtest\n    displayName: test instance account for managed setup\n    projectId: mock-project\n- name: iam-policy-instance-project-cld-congtest\n  type: gcp-types/cloudresourcemanager-v1:virtual.projects.iamMemberBinding\n  metadata:\n    dependsOn:\n      - instance-cld-congtest\n  properties: \n    resource: mock-project\n    role: roles/artifactregistry.reader\n    member: "serviceAccount:$(ref.instance-cld-congtest.email)"\n- name: bucket-iam-anyscale-acess-cld-congtest\n  type: gcp-types/storage-v1:virtual.buckets.iamMemberBinding\n  properties:\n    bucket: $(ref.storage-bucket-cld-congtest.name)\n    member: serviceAccount:$(ref.anyscale-access-cld-congtest.email)\n    role: roles/storage.admin\n  metadata:\n    dependsOn:\n      - anyscale-access-cld-congtest\n- name: bucket-iam-instance-cld-congtest\n  type: gcp-types/storage-v1:virtual.buckets.iamMemberBinding\n  properties:\n    bucket: $(ref.storage-bucket-cld-congtest.name)\n    member: serviceAccount:$(ref.instance-cld-congtest.email)\n    role: roles/storage.admin\n  metadata:\n    dependsOn:\n      - instance-cld-congtest\n    '
    mock_gcp_deployment = GCPDeployment(
        deployment_name=mock_deployment,
        fingerprint=mock_fingerprint,
        config_content=mock_config_content,
    )

    mock_get_deployment_config = Mock(return_value=mock_gcp_deployment)
    mock_update_deployment = Mock()

    with patch.multiple(
        "anyscale.utils.gcp_managed_setup_utils",
        wait_for_operation_completion=Mock(),
        get_deployment_config=mock_get_deployment_config,
        update_deployment=mock_update_deployment,
    ):

        assert (
            update_deployment_with_bucket_only(
                factory, mock_project_id, mock_deployment
            )
            is None
        )
        mock_get_deployment_config.assert_called_once_with(
            factory, mock_project_id, mock_deployment
        )
        expected_config_content = "resources:\n- name: storage-bucket-cld-congtest\n  properties:\n    cors:\n    - method:\n      - GET\n      origin:\n      - https://console.anyscale-staging.com\n      responseHeader:\n      - '*'\n    iamConfiguration:\n      publicAccessPrevention: enforced\n      uniformBucketLevelAccess:\n        enabled: true\n    location: us-west1\n    storageClass: REGIONAL\n  type: storage.v1.bucket\n"
        mock_update_deployment.assert_called_once_with(
            factory,
            mock_project_id,
            mock_deployment,
            mock_fingerprint,
            expected_config_content,
        )


@pytest.mark.parametrize(
    ("responses", "expected_error_message"),
    [
        pytest.param([("404 Not Found", None)], None, id="no-firewall",),
        pytest.param(
            [
                ("200 OK", "firewall_policy_get.json"),
                ("200 OK", "remove_firewall_vpc_association.json"),
                ("200 OK", "remove_firewall_vpc_association_done.json"),
            ],
            None,
            id="succeed",
        ),
        pytest.param(
            [("200 OK", "firewall_policy_get.json"), ("400 Bad Request", None)],
            None,
            id="no-association",
        ),
        pytest.param(
            [("200 OK", "firewall_policy_get.json"), ("403 Forbidden", None)],
            "Failed to remove firewall policy association.",
            id="forbidden",
        ),
        pytest.param(
            [
                ("200 OK", "firewall_policy_get.json"),
                ("200 OK", "remove_firewall_vpc_association.json"),
                ("200 OK", "remove_firewall_vpc_association.json"),
            ],
            "Timeout",
            id="timeout",
        ),
        pytest.param(
            [
                ("200 OK", "firewall_policy_get.json"),
                ("200 OK", "remove_firewall_vpc_association.json"),
                ("200 OK", "remove_firewall_vpc_association_error.json"),
            ],
            "Failed to remove",
            id="error",
        ),
    ],
)
def test_remove_firewall_policy_associations(
    setup_mock_server, responses, expected_error_message
):
    factory, tracker = setup_mock_server
    mock_project_id = "mock-project"
    mock_firewall_policy = "mock-firewall-policy"
    tracker.reset({".*": responses})
    if expected_error_message:
        with pytest.raises(ClickException) as e:
            remove_firewall_policy_associations(
                factory, mock_project_id, mock_firewall_policy
            )
        e.match(expected_error_message)
    else:
        assert (
            remove_firewall_policy_associations(
                factory, mock_project_id, mock_firewall_policy
            )
            is None
        )


def test_delete_gcp_tls_certificates():
    mock_factory = Mock()
    mock_certificate_manager_client = Mock()
    mock_operation_client = Mock()
    project_id = "project_id"
    cloud_id = "cloud_id"
    location_path = "projects/project_id/locations/global"
    certificate_id = "certificate_id"
    certificate_map_entry_path = (
        "projects/project_id/locations/global/certificateMaps/certificate_map_entry_id"
    )
    certificate_map_entry_name = f"projects/project_id/locations/global/certificateMaps/{certificate_id}/certificateMapEntries/certificate_map_entry_id"
    certificate_name = (
        f"projects/project_id/locations/global/certificates/{certificate_id}"
    )
    certificate_map_name = (
        f"projects/project_id/locations/global/certificateMaps/{certificate_id}"
    )

    anyscale_cloud_label = {}
    anyscale_cloud_label["anyscale-cloud-id"] = cloud_id

    # Mock certificate_manager_client.common_location_path
    mock_certificate_manager_client.common_location_path = Mock(
        return_value=location_path
    )

    # Mock certificate_manager_client.list_certificates
    certificate = Certificate(name=certificate_name, labels=anyscale_cloud_label)
    mock_certificate_manager_client.list_certificates = Mock(return_value=[certificate])

    # Mock certificate_manager_client.list_certificate_maps
    certificate_map = CertificateMap(
        name=certificate_map_name, labels=anyscale_cloud_label
    )
    mock_certificate_manager_client.list_certificate_maps = Mock(
        return_value=[certificate_map]
    )

    # Mock certificate_manager_client.certificate_map_path
    mock_certificate_manager_client.certificate_map_path = Mock(
        return_value=certificate_map_entry_path
    )

    # Mock certificate_manager_client.list_certificate_map_entries
    certificate_map_entry = CertificateMapEntry(
        name=certificate_map_entry_name, labels=anyscale_cloud_label
    )
    mock_certificate_manager_client.list_certificate_map_entries = Mock(
        return_value=[certificate_map_entry]
    )

    # Mock delete resource requests
    mock_certificate_manager_client.delete_certificate_map_entry = Mock()
    mock_certificate_manager_client.delete_certificate_map = Mock()
    mock_certificate_manager_client.delete_certificate = Mock()

    # Create Mock clients
    mock_factory.compute_v1.GlobalOperationsClient = Mock(
        return_value=mock_operation_client
    )
    mock_factory.certificate_manager_v1.CertificateManagerClient = Mock(
        return_value=mock_certificate_manager_client
    )

    delete_gcp_tls_certificates(mock_factory, project_id, cloud_id)

    # Assert function calls
    mock_certificate_manager_client.common_location_path.assert_called_once_with(
        project_id, "global"
    )
    mock_certificate_manager_client.list_certificates.assert_called_once_with(
        parent=location_path
    )
    mock_certificate_manager_client.list_certificate_maps.assert_called_once_with(
        parent=location_path
    )
    mock_certificate_manager_client.certificate_map_path.assert_called_once_with(
        project_id, "global", certificate_id
    )
    mock_certificate_manager_client.list_certificate_map_entries.assert_called_once_with(
        parent=certificate_map_entry_path
    )
    mock_certificate_manager_client.delete_certificate_map_entry.assert_called_once_with(
        name=certificate_map_entry_name
    )
    mock_certificate_manager_client.delete_certificate_map.assert_called_once_with(
        name=certificate_map_name
    )
    mock_certificate_manager_client.delete_certificate.assert_called_once_with(
        name=certificate_name
    )


@pytest.mark.parametrize("enable_head_node_fault_tolerance", [True, False])
def test_generate_deployment_manager_config(enable_head_node_fault_tolerance):
    mock_region = "mock-region"
    mock_project_id = "mock-project"
    mock_cloud_id = "cld_mock"
    mock_service_account_name = "anyscale-access-mock"
    workload_identity_pool_name = (
        "projects/112233445566/locations/global/workloadIdentityPools/mock-pool"
    )
    anyscale_aws_account = "123456"
    organization_id = "org_mock"

    generated_config = generate_deployment_manager_config(
        mock_region,
        mock_project_id,
        mock_cloud_id,
        mock_service_account_name,
        workload_identity_pool_name,
        anyscale_aws_account,
        organization_id,
        enable_head_node_fault_tolerance,
    )

    # verify it's a valid yaml file
    yaml.safe_load(generated_config)

    # verify all ${val} are substituted
    assert re.search(r"\$\{.*\}", generated_config) is None

    if enable_head_node_fault_tolerance:
        assert "gcp-types/redis-v1:projects.locations.instances" in generated_config
    else:
        assert "gcp-types/redis-v1:projects.locations.instances" not in generated_config


@pytest.mark.parametrize(
    ("redis_instance_exists", "expected_error"),
    [
        pytest.param(True, False, id="redis-instance-exists"),
        pytest.param(False, True, id="error"),
        pytest.param(False, False, id="happy-path"),
    ],
)
@pytest.mark.parametrize("yes", [True, False])
def test_get_or_create_memorystore_gcp(redis_instance_exists, yes, expected_error):
    factory = Mock()
    mock_cloud_id = "mock-cloud-id"
    mock_deployment = mock_cloud_id
    mock_project_id = "mock-project"
    mock_resource_name = f"redis-{mock_deployment}"
    mock_region = "mock-region"

    mock_get_deployment_config = Mock(
        return_value=GCPDeployment(
            deployment_name=mock_deployment, fingerprint="mock", config_content="mock",
        )
    )
    mock_update_deployment = Mock()
    mock_get_deployment_resource = Mock()
    if redis_instance_exists:
        mock_get_deployment_resource.return_value = {"name": mock_resource_name}
    elif expected_error:
        mock_get_deployment_resource.side_effect = [None, None]
    else:
        mock_get_deployment_resource.side_effect = [None, {"name": mock_resource_name}]

    with patch.multiple(
        "anyscale.utils.gcp_managed_setup_utils",
        get_deployment_resource=mock_get_deployment_resource,
        get_deployment_config=mock_get_deployment_config,
        update_deployment=mock_update_deployment,
        confirm=Mock(),
    ):
        if expected_error:
            with pytest.raises(ClickException) as e:
                get_or_create_memorystore_gcp(
                    factory,
                    mock_cloud_id,
                    mock_deployment,
                    mock_project_id,
                    mock_region,
                    CloudSetupLogger(),
                    yes,
                )
            e.match("Failed to create Memorystore instance in deployment")
        else:
            assert (
                get_or_create_memorystore_gcp(
                    factory,
                    mock_cloud_id,
                    mock_deployment,
                    mock_project_id,
                    mock_region,
                    CloudSetupLogger(),
                    yes,
                )
                == f"projects/{mock_project_id}/locations/{mock_region}/instances/{mock_resource_name}"
            )
            if redis_instance_exists:
                mock_get_deployment_resource.assert_called_once()
                mock_get_deployment_config.assert_not_called()
                mock_update_deployment.assert_not_called()
            else:
                assert mock_get_deployment_resource.call_count == 2
                assert mock_get_deployment_config.call_count == 2
                if yes:
                    mock_update_deployment.assert_called_once()
                else:
                    assert mock_get_deployment_resource.call_count == 2


@pytest.mark.parametrize(
    ("response", "expected_error", "expected_none"),
    [
        pytest.param(("404 Not Found", None), False, True, id="404-not-found",),
        pytest.param(("403 Forbidden", None), True, True, id="403-forbidden",),
        pytest.param(
            ("200 OK", "deployment_manager_resources_get.json"),
            False,
            False,
            id="happy-path",
        ),
    ],
)
def test_get_deployment_resource(
    setup_mock_server, response, expected_error, expected_none
):
    factory, tracker = setup_mock_server
    mock_project_id = "mock-project"
    mock_deployment_name = "mock-deployment"
    mock_resource_name = f"redis-{mock_deployment_name}"
    tracker.reset({".*": [response]})
    if expected_error:
        with pytest.raises(ClickException) as e:
            get_deployment_resource(
                factory, mock_project_id, mock_deployment_name, mock_resource_name
            )
        e.match("Failed to get resource")
    else:
        assert (
            get_deployment_resource(
                factory, mock_project_id, mock_deployment_name, mock_resource_name
            )
            is None
        ) == expected_none


@pytest.mark.parametrize(
    ("responses", "expected_error"),
    [
        pytest.param(
            [("200 OK", "deployment_get.json"), ("200 OK", "manifest_get.json")],
            False,
            id="happy-path",
        ),
        pytest.param([("404 Not Found", None)], True, id="no-deployment",),
        pytest.param([("403 Forbidden", None)], True, id="forbidden",),
        pytest.param(
            [("200 OK", "deployment_get.json"), ("403 Forbidden", None)],
            True,
            id="manifest-failed",
        ),
    ],
)
def test_get_deployment_config(setup_mock_server, responses, expected_error):
    factory, tracker = setup_mock_server
    mock_project_id = "mock-project"
    mock_deployment_name = "mock-deployment"
    tracker.reset({".*": responses})
    if expected_error:
        with pytest.raises(ClickException) as e:
            get_deployment_config(factory, mock_project_id, mock_deployment_name)
        e.match("Failed to get deployment config from deployment")
    else:
        assert (
            get_deployment_config(factory, mock_project_id, mock_deployment_name)
            is not None
        )


@pytest.mark.parametrize(
    ("responses", "expected_error"),
    [
        pytest.param([("200 OK", "deployment_update.json")], False, id="happy-path",),
        pytest.param([("404 Not Found", None)], True, id="404",),
        pytest.param([("403 Forbidden", None)], True, id="403",),
    ],
)
def test_update_deployment(setup_mock_server, responses, expected_error):
    factory, tracker = setup_mock_server
    mock_project_id = "mock-project"
    mock_deployment_name = "mock-deployment"
    mock_fingerprint = "mock"
    mock_config_content = "mock"
    tracker.reset({".*": responses})
    with patch.multiple(
        "anyscale.utils.gcp_managed_setup_utils", wait_for_operation_completion=Mock(),
    ):
        if expected_error:
            with pytest.raises(ClickException) as e:
                update_deployment(
                    factory,
                    mock_project_id,
                    mock_deployment_name,
                    mock_fingerprint,
                    mock_config_content,
                )
            e.match("Failed")
        else:
            update_deployment(
                factory,
                mock_project_id,
                mock_deployment_name,
                mock_fingerprint,
                mock_config_content,
            )
