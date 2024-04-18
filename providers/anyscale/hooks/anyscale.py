from airflow.hooks.base_hook import BaseHook
from airflow.exceptions import AirflowException
from airflow.compat.functools import cached_property

import logging

from anyscale import AnyscaleSDK

logger = logging.getLogger(__name__)

class AnyscaleHook(BaseHook):
    """
    This hook handles the authentication and session management for Anyscale services.
    """

    def __init__(self, anyscale_conn_id: str):
        super().__init__()
        self.anyscale_conn_id = anyscale_conn_id
        self.sdk = None
        logger.info(f"Initializing AnyscaleHook with connection_id: {anyscale_conn_id}")
    
    @cached_property
    def sdk(self) -> AnyscaleSDK:
        return AnyscaleSDK(auth_token=self.auth_token)

    def get_conn(self, **kwargs):
        """
        Authenticate to Anyscale using the connection details stored in Airflow's connection and initializes the SDK.
        """
        if self.sdk is None:
            conn = self.get_connection(self.anyscale_conn_id)
            token = conn.password
            if not token:
                raise AirflowException(f"Missing token for connection id {self.anyscale_conn_id}")

            extras = conn.extra_dejson
            # Merge any extra kwargs from the connection and any additional ones passed at runtime
            sdk_params = {**extras, **kwargs}
            
            try:
                self.sdk = AnyscaleSDK(token=token, **sdk_params)
                logger.info("Successfully initialized Anyscale SDK")
            except Exception as e:
                logger.error(f"Unable to authenticate with Anyscale cloud. Error: {e}")
                raise AirflowException(f"Unable to authenticate with Anyscale cloud. Error: {e}")

        return self.sdk
