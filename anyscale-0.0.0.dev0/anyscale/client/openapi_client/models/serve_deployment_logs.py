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


class ServeDeploymentLogs(object):
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
        'logs': 'str',
        'ready': 'bool'
    }

    attribute_map = {
        'logs': 'logs',
        'ready': 'ready'
    }

    def __init__(self, logs=None, ready=None, local_vars_configuration=None):  # noqa: E501
        """ServeDeploymentLogs - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._logs = None
        self._ready = None
        self.discriminator = None

        self.logs = logs
        self.ready = ready

    @property
    def logs(self):
        """Gets the logs of this ServeDeploymentLogs.  # noqa: E501

        Logs of this entity  # noqa: E501

        :return: The logs of this ServeDeploymentLogs.  # noqa: E501
        :rtype: str
        """
        return self._logs

    @logs.setter
    def logs(self, logs):
        """Sets the logs of this ServeDeploymentLogs.

        Logs of this entity  # noqa: E501

        :param logs: The logs of this ServeDeploymentLogs.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and logs is None:  # noqa: E501
            raise ValueError("Invalid value for `logs`, must not be `None`")  # noqa: E501

        self._logs = logs

    @property
    def ready(self):
        """Gets the ready of this ServeDeploymentLogs.  # noqa: E501

                     Indicates if underlying logs service is ready to use.             If false, clients will need to request for logs until this field is True.           # noqa: E501

        :return: The ready of this ServeDeploymentLogs.  # noqa: E501
        :rtype: bool
        """
        return self._ready

    @ready.setter
    def ready(self, ready):
        """Sets the ready of this ServeDeploymentLogs.

                     Indicates if underlying logs service is ready to use.             If false, clients will need to request for logs until this field is True.           # noqa: E501

        :param ready: The ready of this ServeDeploymentLogs.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and ready is None:  # noqa: E501
            raise ValueError("Invalid value for `ready`, must not be `None`")  # noqa: E501

        self._ready = ready

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
        if not isinstance(other, ServeDeploymentLogs):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ServeDeploymentLogs):
            return True

        return self.to_dict() != other.to_dict()
