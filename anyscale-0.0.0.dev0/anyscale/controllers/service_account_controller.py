from typing import List

import click
from rich import box
from rich.console import Console
from rich.table import Table

from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models import ServerSessionToken, ServiceAccount
from anyscale.controllers.base_controller import BaseController


WARNING_COLOR = "bold red"
DEFAULT_OVERFLOW = "fold"
DEFAULT_COL_WIDTH = 36
ONE_HUNDRED_YEARS_IN_SECONDS = 3153600000


class ServiceAccountController(BaseController):
    def __init__(self):
        super().__init__()
        self.log = BlockLogger()
        self.console = Console()

    def _validate_exactly_one_service_account_per_email(
        self, service_accounts: List[ServiceAccount], email: str
    ):
        if len(service_accounts) == 0:
            raise click.ClickException(f"No service account with email {email} found.")

        if len(service_accounts) > 1:
            raise click.ClickException(
                f"Internal server error when fetching service account with email {email}. Please contact support."
            )

    def _print_new_api_key(self, api_key: ServerSessionToken):
        self.console.print(
            "The following API token for the service account will only appear once:\n",
            style=WARNING_COLOR,
        )
        self.console.print(api_key.server_session_id)

    def create_service_account(self, name: str):
        service_account = self.api_client.create_service_account_api_v2_users_service_accounts_post(
            name=name
        ).result
        api_key = self.api_client.create_api_key_api_v2_users_create_api_key_post(
            api_key_parameters={
                "user_id": service_account.user_id,
                "duration": ONE_HUNDRED_YEARS_IN_SECONDS,
            }
        ).result

        self.console.print(f"\nService account {name} created successfully.")
        self._print_new_api_key(api_key)

    def create_new_service_account_api_key(self, email: str):
        service_accounts = (
            self.api_client.list_organization_collaborators_api_v2_organization_collaborators_get(
                is_service_account=True, email=email
            )
        ).results
        self._validate_exactly_one_service_account_per_email(service_accounts, email)
        sa = service_accounts[0]
        api_key = self.api_client.create_api_key_api_v2_users_create_api_key_post(
            api_key_parameters={
                "user_id": sa.user_id,
                "duration": ONE_HUNDRED_YEARS_IN_SECONDS,
            }
        ).result

        self._print_new_api_key(api_key)

    def _print_service_account_table(self, service_accounts: List[ServiceAccount]):
        table = Table(box=box.MINIMAL, header_style="bright_cyan")
        table.add_column("NAME", width=DEFAULT_COL_WIDTH, overflow=DEFAULT_OVERFLOW)
        table.add_column(
            "CREATED AT",
            style="dim",
            width=DEFAULT_COL_WIDTH,
            overflow=DEFAULT_OVERFLOW,
        )
        table.add_column(
            "ORGANIZATION ROLE", width=DEFAULT_COL_WIDTH, overflow=DEFAULT_OVERFLOW
        )
        table.add_column("EMAIL", width=80, overflow=DEFAULT_OVERFLOW)
        for sa in service_accounts:
            table.add_row(
                sa.name,
                sa.created_at.strftime("%Y/%m/%d"),
                sa.permission_level,
                sa.email,
            )

        self.console.print(table)

    def list_service_accounts(self, max_items: int):
        service_accounts = self.api_client.list_organization_collaborators_api_v2_organization_collaborators_get(
            is_service_account=True
        ).results

        self._print_service_account_table(service_accounts[:max_items])

    def delete_service_account(self, email: str):
        service_accounts = self.api_client.list_organization_collaborators_api_v2_organization_collaborators_get(
            is_service_account=True, email=email
        ).results
        self._validate_exactly_one_service_account_per_email(service_accounts, email)
        sa = service_accounts[0]
        self.api_client.remove_organization_collaborator_api_v2_organization_collaborators_identity_id_delete(
            identity_id=sa.id
        )
        self.console.print(f"Service account {email} deleted successfully.")

    def rotate_service_account_api_keys(self, email: str):
        service_accounts = (
            self.api_client.list_organization_collaborators_api_v2_organization_collaborators_get(
                is_service_account=True, email=email
            )
        ).results

        self._validate_exactly_one_service_account_per_email(service_accounts, email)
        sa = service_accounts[0]
        self.api_client.rotate_api_key_for_user_api_v2_organization_collaborators_rotate_api_key_for_user_user_id_post(
            sa.user_id
        )
        api_key = self.api_client.create_api_key_api_v2_users_create_api_key_post(
            api_key_parameters={
                "user_id": sa.user_id,
                "duration": ONE_HUNDRED_YEARS_IN_SECONDS,
            }
        ).result
        self.console.print(
            f"\nAll API keys for service account {email} rotated successfully."
        )
        self._print_new_api_key(api_key)
