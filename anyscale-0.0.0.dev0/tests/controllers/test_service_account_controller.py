from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from unittest.mock import Mock, patch

import click
import pytest

from anyscale.anyscale_pydantic import BaseModel
from anyscale.client.openapi_client.models import (
    AnyscaleServiceAccount,
    AnyscaleserviceaccountResponse,
    OrganizationCollaborator,
    OrganizationPermissionLevel,
    ServerSessionToken,
    ServersessiontokenResponse,
)
from anyscale.controllers.service_account_controller import ServiceAccountController


T = TypeVar("T")


class ListResponseMetadata(BaseModel):
    total: Optional[int] = None
    next_paging_token: Optional[str] = None


class ListResponse(BaseModel, Generic[T]):
    results: List[T]
    metadata: ListResponseMetadata


test_service_account_0 = AnyscaleServiceAccount(
    email="test_email",
    user_id="test_user_id",
    name="test_name",
    organization_id="test_org_id",
    permission_level=OrganizationPermissionLevel.COLLABORATOR,
    created_at=datetime(2021, 1, 1),
)

test_service_account_1 = AnyscaleServiceAccount(
    email="test_email_1",
    user_id="test_user_id_1",
    name="test_name_1",
    organization_id="test_org_id_1",
    permission_level=OrganizationPermissionLevel.COLLABORATOR,
    created_at=datetime(2021, 1, 1),
)

test_organization_collaborator_0 = OrganizationCollaborator(
    id="test_identity_id",
    name=test_service_account_0.name,
    permission_level=test_service_account_0.permission_level,
    created_at=test_service_account_0.created_at,
    email=test_service_account_0.email,
    user_id=test_service_account_0.user_id,
)

test_organization_collaborator_1 = OrganizationCollaborator(
    id="test_identity_id_1",
    name=test_service_account_1.name,
    permission_level=test_service_account_1.permission_level,
    created_at=test_service_account_1.created_at,
    email=test_service_account_1.email,
    user_id=test_service_account_1.user_id,
)


@pytest.fixture()
def mock_api_client() -> Mock:
    mock_api_client = Mock()
    mock_api_client.create_service_account_api_v2_users_service_accounts_post = Mock(
        return_value=AnyscaleserviceaccountResponse(result=test_service_account_0)
    )
    mock_api_client.create_api_key_api_v2_users_create_api_key_post = Mock(
        return_value=ServersessiontokenResponse(
            result=ServerSessionToken(server_session_id="test_server_session_id")
        )
    )

    def list_organization_collaborators_api_v2_organization_collaborators_get(
        is_service_account=None, email=None
    ):
        if email == "test_email":
            return ListResponse(
                results=[test_organization_collaborator_0],
                metadata=ListResponseMetadata(total=1),
            )
        if email == "test_email_1":
            return ListResponse(
                results=[test_organization_collaborator_1],
                metadata=ListResponseMetadata(total=1),
            )
        if email == "non_existent_email":
            return ListResponse(results=[], metadata=ListResponseMetadata(total=0))
        return ListResponse(
            results=[
                test_organization_collaborator_0,
                test_organization_collaborator_1,
            ],
            metadata=ListResponseMetadata(total=2),
        )

    mock_api_client.list_organization_collaborators_api_v2_organization_collaborators_get = Mock(
        side_effect=list_organization_collaborators_api_v2_organization_collaborators_get
    )
    return mock_api_client


@pytest.fixture()
def mock_auth_api_client(mock_api_client: Mock, base_mock_anyscale_api_client: Mock):
    mock_auth_api_client = Mock(
        api_client=mock_api_client, anyscale_api_client=base_mock_anyscale_api_client,
    )
    with patch.multiple(
        "anyscale.controllers.base_controller",
        get_auth_api_client=Mock(return_value=mock_auth_api_client),
    ):
        yield


def test_create_service_account(mock_api_client, mock_auth_api_client):
    sa_controller = ServiceAccountController()
    mock_console = Mock()
    sa_controller.console = mock_console
    sa_controller.api_client = mock_api_client
    sa_controller.create_service_account("test_name")

    mock_api_client.create_service_account_api_v2_users_service_accounts_post.assert_called_once_with(
        name="test_name"
    )
    mock_api_client.create_api_key_api_v2_users_create_api_key_post.assert_called_once_with(
        api_key_parameters={"user_id": "test_user_id", "duration": 3153600000}
    )

    mock_console.print.assert_called_with("test_server_session_id")


def test_create_new_service_account_api_key(mock_api_client, mock_auth_api_client):
    sa_controller = ServiceAccountController()
    mock_console = Mock()
    sa_controller.console = mock_console
    sa_controller.api_client = mock_api_client
    sa_controller.create_new_service_account_api_key("test_email")

    mock_api_client.list_organization_collaborators_api_v2_organization_collaborators_get.assert_called_once_with(
        is_service_account=True, email="test_email"
    )
    mock_api_client.create_api_key_api_v2_users_create_api_key_post.assert_called_once_with(
        api_key_parameters={"user_id": "test_user_id", "duration": 3153600000}
    )
    mock_console.print.assert_called_with("test_server_session_id")


@pytest.mark.parametrize("max_items", [1, 2])
def test_list_service_accounts(mock_api_client, mock_auth_api_client, max_items):
    sa_controller = ServiceAccountController()
    sa_controller._print_service_account_table = Mock()
    mock_console = Mock()
    sa_controller.console = mock_console
    sa_controller.api_client = mock_api_client
    sa_controller.list_service_accounts(max_items)

    mock_api_client.list_organization_collaborators_api_v2_organization_collaborators_get.assert_called_once_with(
        is_service_account=True
    )
    if max_items == 1:
        sa_controller._print_service_account_table.assert_called_once_with(
            [test_organization_collaborator_0]
        )
    else:
        sa_controller._print_service_account_table.assert_called_once_with(
            [test_organization_collaborator_0, test_organization_collaborator_1]
        )


@pytest.mark.parametrize(
    "input_email", ["test_email", "non_existent_email", "multiple_service_accounts"]
)
def test_delete_service_account(mock_api_client, mock_auth_api_client, input_email):
    sa_controller = ServiceAccountController()
    mock_console = Mock()
    sa_controller.console = mock_console
    sa_controller.api_client = mock_api_client

    if input_email == "non_existent_email":
        with pytest.raises(
            click.ClickException,
            match=f"No service account with email {input_email} found.",
        ):
            sa_controller.delete_service_account(input_email)
        mock_api_client.list_organization_collaborators_api_v2_organization_collaborators_get.assert_called_once_with(
            is_service_account=True, email=input_email
        )
        return

    if input_email == "multiple_service_accounts":
        with pytest.raises(
            click.ClickException,
            match=f"Internal server error when fetching service account with email {input_email}. Please contact support.",
        ):
            sa_controller.delete_service_account(input_email)
        mock_api_client.list_organization_collaborators_api_v2_organization_collaborators_get.assert_called_once_with(
            is_service_account=True, email=input_email
        )
        return

    sa_controller.delete_service_account(input_email)
    mock_api_client.list_organization_collaborators_api_v2_organization_collaborators_get.assert_called_once_with(
        is_service_account=True, email=input_email
    )
    mock_api_client.remove_organization_collaborator_api_v2_organization_collaborators_identity_id_delete(
        user_id="test_user_id"
    )


def test_rotate_service_account_api_keys(mock_api_client, mock_auth_api_client):
    sa_controller = ServiceAccountController()
    mock_console = Mock()
    sa_controller.console = mock_console
    sa_controller.api_client = mock_api_client

    sa_controller.rotate_service_account_api_keys("test_email")
    mock_api_client.list_organization_collaborators_api_v2_organization_collaborators_get.assert_called_once_with(
        is_service_account=True, email="test_email"
    )
    mock_api_client.create_api_key_api_v2_users_create_api_key_post.assert_called_once_with(
        api_key_parameters={"user_id": "test_user_id", "duration": 3153600000}
    )
    mock_api_client.rotate_api_key_for_user_api_v2_organization_collaborators_rotate_api_key_for_user_user_id_post.assert_called_once_with(
        "test_user_id"
    )
    mock_console.print.assert_called_with("test_server_session_id")
