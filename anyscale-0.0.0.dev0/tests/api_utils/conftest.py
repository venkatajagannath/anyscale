import json
from typing import Any, Dict
from unittest.mock import Mock

from anyscale_client.exceptions import ApiException

from anyscale.sdk.anyscale_client.api.default_api import DefaultApi as BaseApi


class MockBaseApi(Mock, BaseApi):
    pass


def get_mock_base_api(function_to_return_vals: Dict[str, Any]) -> MockBaseApi:
    base_api = Mock()
    for function_name, side_effects in function_to_return_vals.items():
        mock_return_val = Mock()
        if type(side_effects) is list or issubclass(type(side_effects), Exception):
            mock_return_val.side_effect = side_effects
        else:
            mock_return_val.return_value = side_effects
        setattr(base_api, function_name, mock_return_val)
    return base_api


def get_mock_api_exception(status: int, error_message: str) -> ApiException:
    mock_api_exception = ApiException(status=status)
    mock_api_exception.body = json.dumps({"error": {"detail": error_message}})
    return mock_api_exception
