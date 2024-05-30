import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from threading import Thread
from typing import Any, Dict, Iterator, List, Optional, Tuple
from unittest.mock import Mock, patch
from wsgiref.simple_server import make_server

from google.auth.credentials import AnonymousCredentials
import pytest

from anyscale.client.openapi_client import (
    Cloud,
    ExecuteCommandResponse,
    Organization,
    Project,
    Session,
    SessionCommand,
    SessionCommandTypes,
    SessionListResponse,
    SessionStartingUpData,
    SessionStateData,
    UserInfo,
)
from anyscale.sdk.anyscale_client.models.cluster_compute import ClusterCompute
from anyscale.sdk.anyscale_client.models.cluster_compute_config import (
    ClusterComputeConfig,
)
from anyscale.sdk.anyscale_client.models.compute_template import ComputeTemplate
from anyscale.utils.gcp_utils import GoogleCloudClientFactory


@pytest.fixture()
def base_mock_api_client() -> Mock:
    mock_api_client = Mock()
    return mock_api_client


@pytest.fixture()
def base_mock_anyscale_api_client() -> Mock:
    mock_anyscale_api_client = Mock()
    return mock_anyscale_api_client


@pytest.fixture()
def mock_auth_api_client(
    base_mock_api_client: Mock, base_mock_anyscale_api_client: Mock
):
    mock_auth_api_client = Mock(
        api_client=base_mock_api_client,
        anyscale_api_client=base_mock_anyscale_api_client,
        host="https://api.anyscale.com",
    )
    with patch.multiple(
        "anyscale.controllers.base_controller",
        get_auth_api_client=Mock(return_value=mock_auth_api_client),
    ):
        yield


@pytest.fixture()
def mock_api_client_with_session(
    base_mock_api_client: Mock, session_test_data: Session
) -> Mock:
    base_mock_api_client.list_sessions_api_v2_sessions_get.return_value = SessionListResponse(
        results=[session_test_data]
    )
    return base_mock_api_client


@pytest.fixture(scope="module")
def cloud_test_data() -> Cloud:
    return Cloud(
        id="cloud_id_1",
        name="cloud_name_1",
        provider="AWS",
        region="region",
        credentials="credentials",
        creator_id="creator_id",
        type="PUBLIC",
        created_at=datetime(2023, 10, 14),
        config='{"max_stopped_instances": 0}',
        state="ACTIVE",
        is_default=False,
        customer_aggregated_logs_config_id="calc_fake_id",
    )


@pytest.fixture(scope="module")
def project_test_data() -> Project:
    return Project(
        name="project_name",
        description="test project",
        cloud_id="cloud_id",
        initial_cluster_config="initial_config",
        id="project_id",
        created_at=datetime.now(tz=timezone.utc),
        creator_id="creator_id",
        is_owner=True,
        directory_name="/directory/name",
        active_sessions=0,
        last_activity_at=datetime.now(tz=timezone.utc),
        is_default=False,
    )


@pytest.fixture(scope="module")
def session_test_data() -> Session:
    return Session(
        id="session_id",
        name="session_name",
        created_at=datetime.now(tz=timezone.utc),
        snapshots_history=[],
        tensorboard_available=False,
        project_id="project_id",
        state="Running",
        idle_timeout=120,
        access_token="token",
        host_name="https://test.anyscale.com",
    )


@pytest.fixture(scope="module")
def compute_config_test_data() -> ClusterComputeConfig:
    return ClusterComputeConfig(
        cloud_id="cld_123",
        head_node_type={
            "instance_type": "m5.2xlarge",
            "name": "head-node-type",
            "resources": None,
        },
        max_workers=20,
        region="us-west-2",
        worker_node_types=[
            {
                "instance_type": "m5.4xlarge",
                "max_workers": 10,
                "min_workers": None,
                "name": "worker-node-type-0",
                "resources": None,
                "use_spot": False,
            },
            {
                "instance_type": "g4dn.4xlarge",
                "max_workers": 10,
                "min_workers": None,
                "name": "worker-node-type-1",
                "resources": None,
                "use_spot": False,
            },
        ],
    )


@pytest.fixture(scope="module")
def cluster_compute_test_data(
    compute_config_test_data: ClusterComputeConfig,
) -> ClusterCompute:
    return ClusterCompute(
        id="cpt_123",
        name="compute_config_name",
        creator_id="user_123",
        organization_id="org_123",
        project_id="prj_123",
        created_at=datetime.now(tz=timezone.utc),
        last_modified_at=datetime.now(tz=timezone.utc),
        config=compute_config_test_data,
        anonymous=False,
        version=1,
    )


@pytest.fixture(scope="module")
def compute_template_test_data(
    compute_config_test_data: ClusterComputeConfig,
) -> ComputeTemplate:
    return ComputeTemplate(
        id="cpt_123",
        name="compute_config_name",
        creator_id="user_123",
        organization_id="org_123",
        project_id="prj_123",
        created_at=datetime.now(tz=timezone.utc),
        last_modified_at=datetime.now(tz=timezone.utc),
        config=compute_config_test_data,
        anonymous=False,
        version=1,
    )


@pytest.fixture(scope="module")
def session_start_error_test_data() -> Session:
    return Session(
        id="session_id",
        name="session_name",
        created_at=datetime.now(tz=timezone.utc),
        snapshots_history=[],
        tensorboard_available=False,
        project_id="project_id",
        state="StartupErrored",
        state_data=SessionStateData(
            startup=SessionStartingUpData(startup_error="start up error")
        ),
        idle_timeout=120,
        access_token="token",
    )


@pytest.fixture(scope="module")
def session_terminated_test_data() -> Session:
    return Session(
        id="session_id",
        name="session_name",
        created_at=datetime.now(tz=timezone.utc),
        snapshots_history=[],
        tensorboard_available=False,
        project_id="project_id",
        state="Terminated",
        idle_timeout=120,
        access_token="token",
    )


@pytest.fixture(scope="module")
def session_command_test_data() -> SessionCommand:
    return SessionCommand(
        id="session_command_id",
        created_at=datetime.now(tz=timezone.utc),
        name="session_command",
        params="params",
        shell="shell",
        shell_command="shell_command",
        type=SessionCommandTypes.COMMAND_LINE_RUNNER,
    )


@pytest.fixture(scope="module")
def command_id_test_data() -> ExecuteCommandResponse:
    return ExecuteCommandResponse(
        command_id="command_id",
        directory_name="dir_name",
        dns_address="session.anyscaleuserdata-dev.com",
    )


@pytest.fixture(scope="module")
def userinfo_test_data() -> UserInfo:
    return UserInfo(
        id="mock_user_id",
        email="mock_email",
        name="mock_name",
        username="mock_user_name",
        verified=True,
        organization_permission_level="owner",
        organization_ids=["mock_org_id_1"],
        organizations=[
            Organization(
                id="mock_org_id_1",
                name="mock_org_1",
                public_identifier="mock_org_1",
                default_cloud_id="mock_default_cloud_id",
                sso_required=False,
                is_general_platform_enabled=True,
                is_private_endpoints_enabled=False,
                is_usage_blocked=False,
            )
        ],
        ld_hash="mock_ld_hash",
        ld_hash_fields=["email", "name", "username", "organization_ids"],
    )


@pytest.fixture(scope="session", autouse=True)
def default_session_fixture(
    request: "_pytest.fixtures.SubRequest",  # type: ignore # noqa: F821
) -> Any:
    with patch("time.sleep", Mock()):
        yield


class RequestTracker:
    def __init__(self):
        self.responses: Dict[str, List[Tuple[int, Optional[str]]]] = {}
        self.seen_requests: List[Any] = []

    def reset(self, responses):
        for k, v in responses.items():
            re.compile(k)
            assert all(len(i) == 2 for i in v)
        self.responses = copy.deepcopy(responses)
        self.seen_requests = []


class GCloudMockHandler:
    def __init__(self, tracker, *args, **kwargs):
        self.tracker = tracker

    def __call__(self, env, start_response):
        self.tracker.seen_requests.append(env)

        path = env["PATH_INFO"]

        for regex in self.tracker.responses:
            if re.match(regex, path):
                code, body_file = self.tracker.responses[regex].pop(0)
                start_response(code, [("Content-Type", "application/json")])
                if body_file is not None:
                    with open(
                        Path(__file__).parent.joinpath("gcp_responses", body_file)
                    ) as f:
                        return [json.dumps(json.load(f)).strip().encode()]
                return []

        pytest.fail(
            f"Un handled request to {self.path}:\n{self.tracker.responses}",
            pytrace=False,
        )


@pytest.fixture()
def setup_mock_server() -> Iterator[Tuple[GoogleCloudClientFactory, RequestTracker]]:
    tracker = RequestTracker()
    server = make_server("localhost", 0, GCloudMockHandler(tracker))
    port = server.server_port
    print(f"Serving on (http://localhost:{port})")
    t = Thread(target=server.serve_forever, daemon=True)
    t.start()
    yield (
        GoogleCloudClientFactory(
            credentials=AnonymousCredentials(),
            force_rest=True,
            client_options={"api_endpoint": f"http://127.0.0.1:{port}"},
        ),
        tracker,
    )
    print(f"Shutting down server on (http://localhost:{port})")
    server.server_close()
    t.join(timeout=0.1)
