# Standard library imports
import logging
from typing import TYPE_CHECKING, Any, Literal

# Third-party imports
from anyscale import AnyscaleSDK
from anyscale.sdk.anyscale_client.models import *

# Airflow imports
from airflow.hooks.base_hook import BaseHook
from airflow.exceptions import AirflowException
from airflow.compat.functools import cached_property

logger = logging.getLogger(__name__)

class AnyscaleHook(BaseHook):
    """
    This hook handles the authentication and session management for Anyscale services.
    """

    conn_name_attr = "conn_id"
    default_conn_name = "anyscale_default"
    conn_type = "anyscale"
    hook_name = "AnyscaleHook"

    def __init__(self, conn_id: str = default_conn_name, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.sdk = None
        self.kwargs = kwargs
        logger.info(f"Initializing AnyscaleHook with connection_id: {conn_id}")

    @classmethod
    def get_ui_field_behaviour(cls) -> dict[str, Any]:
        """Return custom field behaviour."""
        return {
            "hidden_fields": ["schema", "port", "login"],
            "relabeling": {"password": "API Key"},
            "placeholders": {},
        }
    
    @cached_property
    def conn(self) -> AnyscaleSDK:
        """Return an Anyscale connection object."""
        conn = self.get_connection(self.conn_id)
        token = conn.password
        if not token:
            raise AirflowException(f"Missing token for connection id {self.conn_id}")

        extras = conn.extra_dejson
        # Merge any extra kwargs from the connection and any additional ones passed at runtime
        sdk_params = {**extras, **self.kwargs}
        
        try:
            return AnyscaleSDK(auth_token=token, **sdk_params)
        except Exception as e:
            logger.error(f"Unable to authenticate with Anyscale cloud. Error: {e}")
            raise AirflowException(f"Unable to authenticate with Anyscale cloud. Error: {e}")
    
    def create_job(self, config: CreateProductionJob) -> str:

        if self.sdk is None:
            self.sdk = self.conn
        
        prod_job = self.sdk.create_job(config)

        return prod_job
        
    def get_production_job_status(self, job_id: str) -> str:
        
        if self.sdk is None:
            self.sdk = self.conn
        
        return self.sdk.get_production_job(production_job_id=job_id).result.state.current_state


