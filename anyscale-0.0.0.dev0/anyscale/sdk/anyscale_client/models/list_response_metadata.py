# coding: utf-8

"""
    Anyscale API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from anyscale_client.configuration import Configuration


class ListResponseMetadata(object):
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
        'total': 'int',
        'next_paging_token': 'str'
    }

    attribute_map = {
        'total': 'total',
        'next_paging_token': 'next_paging_token'
    }

    def __init__(self, total=None, next_paging_token=None, local_vars_configuration=None):  # noqa: E501
        """ListResponseMetadata - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._total = None
        self._next_paging_token = None
        self.discriminator = None

        if total is not None:
            self.total = total
        if next_paging_token is not None:
            self.next_paging_token = next_paging_token

    @property
    def total(self):
        """Gets the total of this ListResponseMetadata.  # noqa: E501


        :return: The total of this ListResponseMetadata.  # noqa: E501
        :rtype: int
        """
        return self._total

    @total.setter
    def total(self, total):
        """Sets the total of this ListResponseMetadata.


        :param total: The total of this ListResponseMetadata.  # noqa: E501
        :type: int
        """

        self._total = total

    @property
    def next_paging_token(self):
        """Gets the next_paging_token of this ListResponseMetadata.  # noqa: E501


        :return: The next_paging_token of this ListResponseMetadata.  # noqa: E501
        :rtype: str
        """
        return self._next_paging_token

    @next_paging_token.setter
    def next_paging_token(self, next_paging_token):
        """Sets the next_paging_token of this ListResponseMetadata.


        :param next_paging_token: The next_paging_token of this ListResponseMetadata.  # noqa: E501
        :type: str
        """

        self._next_paging_token = next_paging_token

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
        if not isinstance(other, ListResponseMetadata):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ListResponseMetadata):
            return True

        return self.to_dict() != other.to_dict()
