# Standard library imports
import logging
from typing import TYPE_CHECKING, Any, Literal

# Third-party imports
from anyscale import AnyscaleSDK

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
        self.kwargs = kwargs
        logger.info(f"Initializing AnyscaleHook with connection_id: {conn_id}")

    @classmethod
    def get_ui_field_behaviour(cls) -> dict[str, Any]:
        """Return custom field behaviour."""
        return {
            "hidden_fields": ["schema", "port", "login"],
            "relabeling": {"password": "API Key"},
            "placeholders": {
                "password": "API key from Anyscale UI",
            },
        }
    
    @classmethod
    def get_connection_form_widgets(cls) -> dict[str, Any]:
        """Return connection widgets to add to connection form."""
        from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
        from flask_babel import lazy_gettext
        from wtforms import StringField

        return {
            "api_key": StringField(lazy_gettext("API Key"), widget=BS3TextFieldWidget()),
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
            return AnyscaleSDK(token=token, **sdk_params)
        except Exception as e:
            logger.error(f"Unable to authenticate with Anyscale cloud. Error: {e}")
            raise AirflowException(f"Unable to authenticate with Anyscale cloud. Error: {e}")
