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


class SessionKillCommandMessage(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'session_command_id': 'str'
    }

    attribute_map = {
        'session_command_id': 'session_command_id'
    }

    def __init__(self, session_command_id=None, local_vars_configuration=None):  # noqa: E501
        """SessionKillCommandMessage - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._session_command_id = None
        self.discriminator = None

        self.session_command_id = session_command_id

    @property
    def session_command_id(self):
        """Gets the session_command_id of this SessionKillCommandMessage.  # noqa: E501


        :return: The session_command_id of this SessionKillCommandMessage.  # noqa: E501
        :rtype: str
        """
        return self._session_command_id

    @session_command_id.setter
    def session_command_id(self, session_command_id):
        """Sets the session_command_id of this SessionKillCommandMessage.


        :param session_command_id: The session_command_id of this SessionKillCommandMessage.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and session_command_id is None:  # noqa: E501
            raise ValueError("Invalid value for `session_command_id`, must not be `None`")  # noqa: E501

        self._session_command_id = session_command_id

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
        if not isinstance(other, SessionKillCommandMessage):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SessionKillCommandMessage):
            return True

        return self.to_dict() != other.to_dict()
