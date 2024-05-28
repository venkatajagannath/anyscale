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


class ProviderMetadata(object):
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
        'timestamp': 'datetime',
        'available_regions': 'object',
        'available_azs': 'object',
        'available_instance_types': 'object'
    }

    attribute_map = {
        'timestamp': 'timestamp',
        'available_regions': 'available_regions',
        'available_azs': 'available_azs',
        'available_instance_types': 'available_instance_types'
    }

    def __init__(self, timestamp=None, available_regions=None, available_azs=None, available_instance_types=None, local_vars_configuration=None):  # noqa: E501
        """ProviderMetadata - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._timestamp = None
        self._available_regions = None
        self._available_azs = None
        self._available_instance_types = None
        self.discriminator = None

        self.timestamp = timestamp
        if available_regions is not None:
            self.available_regions = available_regions
        if available_azs is not None:
            self.available_azs = available_azs
        if available_instance_types is not None:
            self.available_instance_types = available_instance_types

    @property
    def timestamp(self):
        """Gets the timestamp of this ProviderMetadata.  # noqa: E501


        :return: The timestamp of this ProviderMetadata.  # noqa: E501
        :rtype: datetime
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this ProviderMetadata.


        :param timestamp: The timestamp of this ProviderMetadata.  # noqa: E501
        :type: datetime
        """
        if self.local_vars_configuration.client_side_validation and timestamp is None:  # noqa: E501
            raise ValueError("Invalid value for `timestamp`, must not be `None`")  # noqa: E501

        self._timestamp = timestamp

    @property
    def available_regions(self):
        """Gets the available_regions of this ProviderMetadata.  # noqa: E501

        The available regions for this Cloud.  # noqa: E501

        :return: The available_regions of this ProviderMetadata.  # noqa: E501
        :rtype: object
        """
        return self._available_regions

    @available_regions.setter
    def available_regions(self, available_regions):
        """Sets the available_regions of this ProviderMetadata.

        The available regions for this Cloud.  # noqa: E501

        :param available_regions: The available_regions of this ProviderMetadata.  # noqa: E501
        :type: object
        """

        self._available_regions = available_regions

    @property
    def available_azs(self):
        """Gets the available_azs of this ProviderMetadata.  # noqa: E501

        The available AZs for this Cloud.  # noqa: E501

        :return: The available_azs of this ProviderMetadata.  # noqa: E501
        :rtype: object
        """
        return self._available_azs

    @available_azs.setter
    def available_azs(self, available_azs):
        """Sets the available_azs of this ProviderMetadata.

        The available AZs for this Cloud.  # noqa: E501

        :param available_azs: The available_azs of this ProviderMetadata.  # noqa: E501
        :type: object
        """

        self._available_azs = available_azs

    @property
    def available_instance_types(self):
        """Gets the available_instance_types of this ProviderMetadata.  # noqa: E501

        The instance types available for this Cloud.  # noqa: E501

        :return: The available_instance_types of this ProviderMetadata.  # noqa: E501
        :rtype: object
        """
        return self._available_instance_types

    @available_instance_types.setter
    def available_instance_types(self, available_instance_types):
        """Sets the available_instance_types of this ProviderMetadata.

        The instance types available for this Cloud.  # noqa: E501

        :param available_instance_types: The available_instance_types of this ProviderMetadata.  # noqa: E501
        :type: object
        """

        self._available_instance_types = available_instance_types

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
        if not isinstance(other, ProviderMetadata):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ProviderMetadata):
            return True

        return self.to_dict() != other.to_dict()
