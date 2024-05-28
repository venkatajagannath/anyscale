# coding: utf-8

"""
    Managed Ray API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from openapi_client.configuration import Configuration


class CardId(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    allowed enum values
    """
    SETUP_CLOUD = "setup_cloud"
    INVITE_COWORKERS = "invite_coworkers"
    SETUP_LOCAL_ENV = "setup_local_env"
    RUN_HELLO_WORLD = "run_hello_world"
    RUN_EXISTING_CODE = "run_existing_code"
    EXPLORE_ANYSCALE = "explore_anyscale"
    GOLDEN_NOTEBOOK_DATA_LOADING = "golden_notebook_data_loading"
    GOLDEN_NOTEBOOK_MODEL_BUILDING = "golden_notebook_model_building"
    GOLDEN_NOTEBOOK_MODEL_SERVING = "golden_notebook_model_serving"
    GOLDEN_NOTEBOOK_INTEGRATING_ANYSCALE = "golden_notebook_integrating_anyscale"

    allowable_values = [SETUP_CLOUD, INVITE_COWORKERS, SETUP_LOCAL_ENV, RUN_HELLO_WORLD, RUN_EXISTING_CODE, EXPLORE_ANYSCALE, GOLDEN_NOTEBOOK_DATA_LOADING, GOLDEN_NOTEBOOK_MODEL_BUILDING, GOLDEN_NOTEBOOK_MODEL_SERVING, GOLDEN_NOTEBOOK_INTEGRATING_ANYSCALE]  # noqa: E501

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
    }

    attribute_map = {
    }

    def __init__(self, local_vars_configuration=None):  # noqa: E501
        """CardId - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration
        self.discriminator = None

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, CardId):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CardId):
            return True

        return self.to_dict() != other.to_dict()
