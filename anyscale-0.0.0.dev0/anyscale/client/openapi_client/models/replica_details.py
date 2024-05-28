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


class ReplicaDetails(object):
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
        'replica_id': 'str',
        'state': 'ReplicaState'
    }

    attribute_map = {
        'replica_id': 'replica_id',
        'state': 'state'
    }

    def __init__(self, replica_id=None, state=None, local_vars_configuration=None):  # noqa: E501
        """ReplicaDetails - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._replica_id = None
        self._state = None
        self.discriminator = None

        self.replica_id = replica_id
        self.state = state

    @property
    def replica_id(self):
        """Gets the replica_id of this ReplicaDetails.  # noqa: E501

        ID of the replica  # noqa: E501

        :return: The replica_id of this ReplicaDetails.  # noqa: E501
        :rtype: str
        """
        return self._replica_id

    @replica_id.setter
    def replica_id(self, replica_id):
        """Sets the replica_id of this ReplicaDetails.

        ID of the replica  # noqa: E501

        :param replica_id: The replica_id of this ReplicaDetails.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and replica_id is None:  # noqa: E501
            raise ValueError("Invalid value for `replica_id`, must not be `None`")  # noqa: E501

        self._replica_id = replica_id

    @property
    def state(self):
        """Gets the state of this ReplicaDetails.  # noqa: E501

        State of the replica  # noqa: E501

        :return: The state of this ReplicaDetails.  # noqa: E501
        :rtype: ReplicaState
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this ReplicaDetails.

        State of the replica  # noqa: E501

        :param state: The state of this ReplicaDetails.  # noqa: E501
        :type: ReplicaState
        """
        if self.local_vars_configuration.client_side_validation and state is None:  # noqa: E501
            raise ValueError("Invalid value for `state`, must not be `None`")  # noqa: E501

        self._state = state

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
        if not isinstance(other, ReplicaDetails):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ReplicaDetails):
            return True

        return self.to_dict() != other.to_dict()
